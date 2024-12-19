from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from postgres_db import books, database
from fastapi.responses import HTMLResponse
from fastapi import HTTPException

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str
    price: float

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    price: float

class Config:
  orm_mode=True

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Book API</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                h1 { color: #4CAF50; }
                p { font-size: 18px; color: #555; }
                a { text-decoration: none; color: #4CAF50; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Welcome to the Book API</h1>
            <p>Manage your books with ease!</p>
            <p><a href="/docs">Explore the API Documentation</a></p>
        </body>
    </html>
    """
    return html_content

@app.post("/books/", response_model=BookResponse)
async def create_book(book: BookCreate):
    query = books.insert().values(title=book.title, author=book.author, price=book.price)
    last_book_id = await database.execute(query)

    query = books.select().where(books.c.id == last_book_id)
    inserted_book = await database.fetch_one(query)
    return inserted_book

@app.get("/books/", response_model=List[BookResponse])
async def get_books():
    query = books.select()
    return await database.fetch_all(query)

@app.delete("/books/{book_id}", response_model=BookResponse)
async def delete_book(book_id: int):
    # Vérifier si le livre existe
    query = books.select().where(books.c.id == book_id)
    book_to_delete = await database.fetch_one(query)

    if not book_to_delete:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found.")

    # Supprimer le livre
    delete_query = books.delete().where(books.c.id == book_id)
    await database.execute(delete_query)

    return book_to_delete


@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate):
    query = books.update().where(books.c.id == book_id).values(
        title=book.title, author=book.author, price=book.price
    )
    await database.execute(query)

    query = books.select().where(books.c.id == book_id)
    updated_book = await database.fetch_one(query)
    return updated_book
