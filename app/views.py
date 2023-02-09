import csv
import hashlib
import os
import json
import uuid
import pandas as pd

import boto3
import psycopg2
from flask import redirect, render_template, request, session
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
    SELECT_ACCOUNT_ID
)

SESSION = boto3.Session(
    aws_access_key_id="",
    aws_secret_access_key="",
)
S3 = SESSION.resource("s3")

connection = psycopg2.connect(app.config["DATABASE_URI"])

BUCKET_NAME = "ubiquity-rest-api"


@app.route("/", methods=["GET", "POST"])
def homepage():
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
        mimetype='application/json'
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    login: This function is used to render the login page of the application.
    """
    if request.method == "POST":
        session["email"] = request.form.get("email")
        session["password"] = request.form.get("password")
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_ACCOUNTS_TABLE)
                cursor.execute(CHECK_ACCOUNTS, (session["email"],))
                account = cursor.fetchone()
                if account:
                    logger.success("Account Logged In successfully!")
                    return render_template(
                        "public//dashboard.html", email=session["email"]
                    )
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
        mimetype='application/json'
    )


@app.route("/register", methods=["GET", "POST"])
def register():
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
        with connection:
            with connection.cursor() as cursor:
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
        mimetype='application/json'
    )


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """
    upload: This function is used to render the upload page of the application.
    """
    if request.method == "POST":
        if request.files:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(CREATE_BOOKS_TABLE)
                    cursor.execute(CREATE_PUBLISHERS_TABLE)
            csv_file = request.files["uploaded-file"]
            csv_file.save(os.path.join(app.config["UPLOAD_FOLDER"], csv_file.filename))
            session["csv_filename"] = csv_file.filename
            s3_file_name = f"{str(uuid.uuid4())}_{str(csv_file.filename)}"
            session["s3_file_name"] = s3_file_name
            session["uploaded_data_file_path"] = os.path.join(
                app.config["UPLOAD_FOLDER"], csv_file.filename
            )
            with open(
                os.path.join(app.config["UPLOAD_FOLDER"], csv_file.filename), mode="r"
            ) as csv_file_content:
                csv_reader = csv.DictReader(csv_file_content)
                for row in csv_reader:
                    if not validate_isbn(row["ISBN"]):
                        logger.error("Invalid ISBN Detected")
                        message = "Invalid ISBN Detected"
                        return render_template(
                            "public/fail_upload.html", message=message
                        )
                    with connection:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                INSERT_BOOKS, (row["ï»¿Book Title"], row["ISBN"])
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
                Filename=os.path.join(app.config["UPLOAD_FOLDER"], csv_file.filename),
                Bucket=BUCKET_NAME,
                Key=s3_file_name,
            )
            location = S3.meta.client.get_bucket_location(Bucket=BUCKET_NAME)[
                "LocationConstraint"
            ]
            session["s3_url"] = f"https://{BUCKET_NAME}.s3.{location}.amazonaws.com/{s3_file_name}"
            session["uploaded_data_file_path"] = os.path.join(
                app.config["UPLOAD_FOLDER"], csv_file.filename
            )
            logger.success("File uploaded successfully")
            return redirect("/filedata")
    elif request.method == "GET":
        return render_template("public/csv_upload.html")
    return app.response_class(
        response=json.dumps({"message": "Internal Server Error"}),
        status=500,
        mimetype='application/json'
    )


@app.route("/filedata", methods=["GET", "POST"])
def file_data():
    """
    file_data: This function is used to render the file data page of the application.
    """
    data_file_path = session.get("uploaded_data_file_path", None)
    csv_filename = session.get("csv_filename", None)
    data = pd.read_csv(data_file_path, header=0)
    datelist = list(data.values)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_S3_TABLE)
            cursor.execute(SELECT_ACCOUNT_ID, (session["email"],))
            account_id = cursor.fetchone()[0]
            cursor.execute(
                INSERT_S3_TABLE,
                (
                    BUCKET_NAME,
                    session["s3_file_name"],
                    session["s3_url"],
                    account_id
                ),
            )
    if request.method == "POST":
        return render_template("public/dashboard.html", email=session["email"])
    elif request.method == "GET":
        return render_template("public/book_data.html", title=csv_filename, datelist=datelist)
    return app.response_class(
        response=json.dumps({"message": "Internal Server Error"}),
        status=500,
        mimetype='application/json'
    )


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """
    dashboard: This function is used to render the dashboard page of the application.
    """
    return render_template("public/dashboard.html", email=session["email"])
