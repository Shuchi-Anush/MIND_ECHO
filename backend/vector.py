from langchain_ollama import OllamaEmbeddings
from langchain_postgres import Postgres
from langchain_core.vectorstores import PostgresVectorStore
import os
import pandas as pd

embeddings = OllamaEmbeddings(model="mxbai-embed-large")
db = PostgresVectorStore(
    postgres=Postgres(
        host="localhost",
        port=5432,
        user="postgres",
        password="your_password",
        dbname="your_database"
    ),
    embedding_function=embeddings.embed_query,
)

