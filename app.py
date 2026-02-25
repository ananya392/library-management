from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

# Create table if not exists
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200),
            author VARCHAR(200),
            genre VARCHAR(100),
            quantity INTEGER
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books ORDER BY id ASC")
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", books=books)

@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        quantity = request.form["quantity"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO books (title, author, genre, quantity) VALUES (%s, %s, %s, %s)",
            (title, author, genre, quantity)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        quantity = request.form["quantity"]

        cur.execute("""
            UPDATE books
            SET title=%s, author=%s, genre=%s, quantity=%s
            WHERE id=%s
        """, (title, author, genre, quantity, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.execute("SELECT * FROM books WHERE id=%s", (id,))
    book = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit.html", book=book)

@app.route("/delete/<int:id>")
def delete_book(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()