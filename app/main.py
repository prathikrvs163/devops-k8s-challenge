import os

import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="DevOps Kubernetes Challenge")


DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:5432/{DB_NAME}"
)


class Item(BaseModel):
    name: str


def get_connection():
    return psycopg2.connect(DATABASE_URL)


@app.on_event("startup")
def startup():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/items")
def get_items():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM items ORDER BY id")

    items = cursor.fetchall()

    cursor.close()
    connection.close()

    return [{"id": item[0], "name": item[1]} for item in items]


@app.post("/api/items")
def create_item(item: Item):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO items (name) VALUES (%s) RETURNING id",
        (item.name,),
    )

    item_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return {"id": item_id, "name": item.name}