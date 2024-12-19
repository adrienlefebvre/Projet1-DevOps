from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float

DB_URL = "postgresql://admin:jKHNRXnqy4nUbl410Mky@localhost/db_books"

database = Database(DB_URL)
metadata = MetaData()

books = Table (
  "books",
  metadata,
  Column("id", Integer, primary_key=True, index=True),
  Column("title", String, index=True),
  Column("author", String, index=True),
  Column("price", Float),
)

engine = create_engine(DB_URL)
metadata.create_all(engine)