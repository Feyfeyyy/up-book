CREATE_ACCOUNTS_TABLE = "CREATE TABLE IF NOT EXISTS accounts (id SERIAL PRIMARY KEY, email TEXT, password TEXT, created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"

CREATE_BOOKS_TABLE = (
    "CREATE TABLE IF NOT EXISTS books (id SERIAL PRIMARY KEY, title TEXT, isbn TEXT, account_id INTEGER, created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE);"
)

CREATE_PUBLISHERS_TABLE = "CREATE TABLE IF NOT EXISTS publishers (books_id INTEGER, author TEXT, publisher_name TEXT, publisher_date TEXT, FOREIGN KEY (books_id) REFERENCES books(id) ON DELETE CASCADE);"

CREATE_S3_TABLE = "CREATE TABLE IF NOT EXISTS aws_s3 (id SERIAL PRIMARY KEY, bucket_name TEXT, file_name TEXT, file_path TEXT, account_id INTEGER, uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE);"

INSERT_ACCOUNTS = "INSERT INTO accounts (email, password) VALUES (%s, %s) RETURNING id;"

INSERT_BOOKS = "INSERT INTO books (title, isbn, account_id) VALUES (%s, %s, %s) RETURNING id;"

INSERT_PUBLISHERS = "INSERT INTO publishers (books_id, author, publisher_name, publisher_date) VALUES (%s, %s, %s, %s);"

INSERT_S3_TABLE = "INSERT INTO aws_s3 (bucket_name, file_name, file_path, account_id) VALUES (%s, %s, %s, %s) RETURNING id;"

CHECK_ACCOUNTS = "SELECT email FROM accounts WHERE email = %s;"

SELECT_ACCOUNT_ID = "SELECT id FROM accounts WHERE email = %s;"

SELECT_USERS_BOOKS = "SELECT account_id, file_name, uploaded_date FROM aws_s3 INNER JOIN accounts acc ON account_id = acc.id WHERE acc.id = %s;"

SELECT_MATCH_USER_BOOKS = "SELECT account_id, title, author, publisher_name, publisher_date FROM books INNER JOIN publishers pb ON pb.books_id = id INNER JOIN accounts acc ON acc.id = account_id WHERE account_id = %s ORDER BY books.id DESC LIMIT 1;"

