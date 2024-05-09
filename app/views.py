import csv
import json
import os
import uuid

import pandas as pd
from flask import Response, redirect, render_template, request, session
from loguru import logger

from app import app, db
from app.classes.aws import S3Object
from app.classes.webhook import WebhookNotifier
from app.methods.isbn import validate_isbn
from app.models import Account, Book, Publisher
from app.sql_config import (
    CREATE_BOOKS_TABLE,
    CREATE_PUBLISHERS_TABLE,
    CREATE_S3_TABLE,
    INSERT_BOOKS,
    INSERT_PUBLISHERS,
    INSERT_S3_TABLE,
    SELECT_ACCOUNT_ID,
    SELECT_MATCH_USER_BOOKS,
    SELECT_USERS_BOOKS,
)

BUCKET_NAME = "ubiquity-rest-api"
WEBHOOK_URL = app.config["WEBHOOK_URL"]

S3 = S3Object(BUCKET_NAME, app.config["AWS_API_KEY"], app.config["AWS_SECRET_KEY"])


@app.route("/", methods=["GET", "POST"])
def homepage() -> str | Response:
    """
    homepage: This function is used to render the homepage of the application.
    """
    if request.method == "POST":
        if request.form.get("Login") == "LOG":
            return redirect("/login")
        if request.form.get("Register") == "REG":
            return redirect("/register")
    elif request.method == "GET":
        return render_template("public/index.html")
    return app.response_class(
        response=json.dumps({"message": "Internal Server Error"}),
        status=500,
        mimetype="application/json",
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    """
    login: This function is used to render the login page of the application.
    """
    if request.method == "POST":
        session["email"] = request.form.get("email")
        session["password"] = request.form.get("password")

        account = Account.query.filter_by(email=session["email"]).first()

        if account:
            logger.success("Account Logged In Successfully!")
            return redirect("/dashboard")
        else:
            logger.error("Account does not exists!")
            msg = "Account does not exists!"
            if request.form.get("Register") == "REG":
                return redirect("/register")
            return render_template("public/fail_login.html", message=msg)
    elif request.method == "GET":
        return render_template("public/login.html")
    return app.response_class(
        response=json.dumps({"message": "Internal Server Error"}),
        status=500,
        mimetype="application/json",
    )


@app.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    """
    register: This function is used to render the register page of the application.
    """
    if (
            request.method == "POST"
            and "email" in request.form
            and "password" in request.form
    ):
        session["email"] = request.form["email"]
        session["password"] = request.form["password"]

        account = Account.query.filter_by(email=session["email"]).first()

        if account:
            msg = "Account already exists!"
            logger.error("Account already exists!")
            return render_template("public/fail_register.html", message=msg)
        else:
            new_account = Account(email=session["email"], password=session["password"])
            db.session.add(new_account)
            db.session.commit()
            logger.success("Account created successfully!")
            return redirect("/upload")
    elif request.method == "GET":
        return render_template("public/register.html")
    return app.response_class(
        response=json.dumps({"message": "Internal Server Error"}),
        status=500,
        mimetype="application/json",
    )


@app.route("/upload", methods=["GET", "POST"])
def upload() -> str | Response:
    """
    upload: This function is used to render the upload page of the application.
    """
    if request.method == "POST":
        if request.files:
            try:
                account_id = Account.query.filter_by(email=session["email"]).first().id
                session["account_id"] = account_id
                csv_file = request.files["uploaded-file"]
                csv_file.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], csv_file.filename)
                )
                session["csv_filename"] = csv_file.filename
                s3_file_name = f"{str(uuid.uuid4())}_{str(csv_file.filename)}"
                session["s3_file_name"] = s3_file_name
                session["uploaded_data_file_path"] = os.path.join(
                    app.config["UPLOAD_FOLDER"], csv_file.filename
                )
                with open(
                        os.path.join(app.config["UPLOAD_FOLDER"], csv_file.filename),
                        mode="r",
                        encoding="utf-8-sig"
                ) as csv_file_content:
                    csv_reader = csv.DictReader(csv_file_content)
                    for row in csv_reader:
                        if not validate_isbn(row["ISBN"]):
                            logger.error("Invalid ISBN Detected")
                            message = "Invalid ISBN Detected"
                            return render_template(
                                "public/fail_upload.html", message=message
                            )

                        new_book = Book(title=row["Book Title"], isbn=row["ISBN"], account_id=account_id)
                        db.session.add(new_book)
                        db.session.commit()

                        new_publisher = Publisher(books_id=new_book.id, author=row["Book Author"],
                                                  publisher_name=row["Publisher Name"],
                                                  publisher_date=row["Date Published"])
                        db.session.add(new_publisher)
                        db.session.commit()
                S3.upload_s3_file(session["uploaded_data_file_path"], s3_file_name)
                location = S3.get_bucket_location()
                session[
                    "s3_url"
                ] = f"https://{BUCKET_NAME}.s3.{location}.amazonaws.com/{s3_file_name}"
                session["uploaded_data_file_path"] = os.path.join(
                    app.config["UPLOAD_FOLDER"], csv_file.filename
                )
                webhook_notifier = WebhookNotifier(
                    session["csv_filename"], session["s3_url"]
                )
                webhook_notifier.send_notification()
                return redirect("/filedata")
            except FileNotFoundError as err:
                logger.error(err)
                message = "File Not Found"
                return render_template("public/fail_upload.html", message=message)
    elif request.method == "GET":
        return render_template("public/csv_upload.html")
    return app.response_class(
        response=json.dumps({"message": "Internal Server Error"}),
        status=500,
        mimetype="application/json",
    )


@app.route("/filedata", methods=["GET", "POST"])
def file_data() -> str | Response:
    """
    file_data: This function is used to render the file data page of the application.
    """
    try:
        data_file_path = session.get("uploaded_data_file_path", None)
        csv_filename = session.get("csv_filename", None)
        data = pd.read_csv(data_file_path, header=0)
        date_list = list(data.values)
        if request.method == "POST":
            with CONNECTION:
                with CONNECTION.cursor() as cursor:
                    cursor.execute(CREATE_S3_TABLE)
                    cursor.execute(
                        INSERT_S3_TABLE,
                        (
                            BUCKET_NAME,
                            session["s3_file_name"],
                            session["s3_url"],
                            session["account_id"],
                        ),
                    )
            return redirect("/dashboard")
        elif request.method == "GET":
            return render_template(
                "public/book_data.html",
                title=csv_filename,
                datelist=date_list,
                url=WEBHOOK_URL,
            )
    except ValueError as err:
        logger.error(err)
        return app.response_class(
            response=json.dumps({"message": f"{err}"}),
            status=500,
            mimetype="application/json",
        )
    return app.response_class(
        response=json.dumps({"message": "Internal Server Error"}),
        status=500,
        mimetype="application/json",
    )


@app.route("/dashboard", methods=["GET"])
def dashboard() -> str | Response:
    """
    dashboard: This function is used to render the dashboard page of the application.
    """
    try:
        account_id = Account.query.filter_by(email=session["email"]).first().id
        user_books = Book.query.filter_by(account_id=account_id).all()
        match_user_books = db.session.query(
            Book.account_id,
            Book.title,
            Publisher.author,
            Publisher.publisher_name,
            Publisher.publisher_date
        ).join(Publisher).join(Account).filter(Account.id == account_id).order_by(Book.id.desc()).limit(1)
        if session.get("email", None) is None:
            return redirect("/login")
        elif request.method == "GET":
            return render_template(
                "public/dashboard.html",
                email=session["email"],
                user_books=user_books,
                books_data=match_user_books,
            )
    except ValueError as err:
        logger.error(err)
        return app.response_class(
            response=json.dumps({"message": f"{err}"}),
            status=500,
            mimetype="application/json",
        )
    return app.response_class(
        response=json.dumps({"message": "Internal Server Error"}),
        status=500,
        mimetype="application/json",
    )


@app.route("/logout")
def logout() -> str | Response:
    """
    logout: This function is used to log out the user from the application.
    """
    session.pop("email", None)
    session.pop("password", None)
    session.pop("account_id", None)
    session.pop("s3_file_name", None)
    session.pop("s3_url", None)
    session.pop("csv_filename", None)
    return redirect("/login")
