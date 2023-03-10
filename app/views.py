import csv
import hashlib
import json
import os
import uuid

import boto3
import pandas as pd
import psycopg2
import requests
from flask import Response, redirect, render_template, request, session
from loguru import logger

from app import app
from app.methods import validate_isbn
from app.sql_config import (
    CHECK_ACCOUNTS,
    CREATE_ACCOUNTS_TABLE,
    CREATE_BOOKS_TABLE,
    CREATE_PUBLISHERS_TABLE,
    CREATE_S3_TABLE,
    INSERT_ACCOUNTS,
    INSERT_BOOKS,
    INSERT_PUBLISHERS,
    INSERT_S3_TABLE,
    SELECT_ACCOUNT_ID,
    SELECT_MATCH_USER_BOOKS,
    SELECT_USERS_BOOKS,
)

SESSION = boto3.Session(
    aws_access_key_id=app.config["API_KEY"],
    aws_secret_access_key=app.config["SECRET_KEY"],
)
S3 = SESSION.resource("s3")

CONNECTION = psycopg2.connect(app.config["DATABASE_URI"])

BUCKET_NAME = "ubiquity-rest-api"

WEBHOOK_REQUEST_URL = app.config["WEBHOOK_REQUEST_URL"]
WEBHOOK_URL = app.config["WEBHOOK_URL"]


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
        with CONNECTION:
            with CONNECTION.cursor() as cursor:
                cursor.execute(CREATE_ACCOUNTS_TABLE)
                cursor.execute(CHECK_ACCOUNTS, (session["email"],))
                account = cursor.fetchone()
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
        session["password"] = hashlib.md5(session["password"].encode()).hexdigest()
        with CONNECTION:
            with CONNECTION.cursor() as cursor:
                cursor.execute(CREATE_ACCOUNTS_TABLE)
                cursor.execute(CHECK_ACCOUNTS, (session["email"],))
                account = cursor.fetchone()
                if account:
                    msg = "Account already exists!"
                    logger.error("Account already exists!")
                    return render_template("public/fail_register.html", message=msg)
                else:
                    cursor.execute(
                        INSERT_ACCOUNTS, (session["email"], str(session["password"]))
                    )
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
                with CONNECTION:
                    with CONNECTION.cursor() as cursor:
                        cursor.execute(CREATE_BOOKS_TABLE)
                        cursor.execute(CREATE_PUBLISHERS_TABLE)
                        cursor.execute(SELECT_ACCOUNT_ID, (session["email"],))
                        account_id = cursor.fetchone()[0]
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
                ) as csv_file_content:
                    csv_reader = csv.DictReader(csv_file_content)
                    for row in csv_reader:
                        if not validate_isbn(row["ISBN"]):
                            logger.error("Invalid ISBN Detected")
                            message = "Invalid ISBN Detected"
                            return render_template(
                                "public/fail_upload.html", message=message
                            )
                        with CONNECTION:
                            with CONNECTION.cursor() as cursor:
                                cursor.execute(
                                    INSERT_BOOKS,
                                    (
                                        row["Book Title"],
                                        row["ISBN"],
                                        session["account_id"],
                                    ),
                                )
                                book_id = cursor.fetchone()[0]
                                cursor.execute(
                                    INSERT_PUBLISHERS,
                                    (
                                        book_id,
                                        row["Book Author"],
                                        row["Publisher Name"],
                                        row["Date Published"],
                                    ),
                                )
                S3.meta.client.upload_file(
                    Filename=os.path.join(
                        app.config["UPLOAD_FOLDER"], csv_file.filename
                    ),
                    Bucket=BUCKET_NAME,
                    Key=s3_file_name,
                )
                location = S3.meta.client.get_bucket_location(Bucket=BUCKET_NAME)[
                    "LocationConstraint"
                ]
                session[
                    "s3_url"
                ] = f"https://{BUCKET_NAME}.s3.{location}.amazonaws.com/{s3_file_name}"
                session["uploaded_data_file_path"] = os.path.join(
                    app.config["UPLOAD_FOLDER"], csv_file.filename
                )
                data = {
                    "app_source": "Up-Book",
                    "description": "Up-Book is a simple application to upload books data to S3 and store it in a database.",
                    "csv_uploaded": True,
                    "csv_filename": session["csv_filename"],
                    "s3_url": session["s3_url"],
                }
                requests.post(
                    WEBHOOK_REQUEST_URL,
                    data=json.dumps(data),
                    headers={"Content-Type": "application/json"},
                )
                logger.success("Posted to Webhook")
                logger.success("File uploaded successfully")
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
        with CONNECTION:
            with CONNECTION.cursor() as cursor:
                cursor.execute(SELECT_ACCOUNT_ID, (session["email"],))
                account_id = cursor.fetchone()[0]
                cursor.execute(SELECT_USERS_BOOKS, (account_id,))
                user_books = cursor.fetchall()
                cursor.execute(SELECT_MATCH_USER_BOOKS, (account_id,))
                match_user_books = cursor.fetchall()
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
