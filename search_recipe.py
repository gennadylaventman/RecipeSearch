import argparse
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from psycopg2.pool import SimpleConnectionPool
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


def search_ingredients_in_db(query_words, cursor):
    cursor.execute(
        """
        WITH QUERY_WORDS AS (
            SELECT %s::TEXT[] AS WORDS
        )
        SELECT DISTINCT R.ID, R.DOCUMENT
        FROM RECIPES R
        JOIN INGREDIENTS I ON R.ID = I.RECIPE_ID
        JOIN QUERY_WORDS Q ON I.INGREDIENT_WORDS @> Q.WORDS;
        """, (query_words,))

    return cursor.fetchall()


def fetch_recipe_from_db(recipe_id, cursor):
    cursor.execute(
        """
        SELECT R.ID, R.DOCUMENT
        FROM RECIPES R
        WHERE R.ID = %s;
        """, (recipe_id,))
    return cursor.fetchall()


def search_recipe_by_ingredient(query, conn):
    cursor = conn.cursor()
    query_words = query.split()
    results = search_ingredients_in_db(query_words, cursor)

    formated_results = []
    if results:
        for row in results:
            formated_results.append(row[1])
            print(f"Recipe ID: {row[0]}, Recipe: {row[1]}")
    else:
        print("No recipes found.")

    return formated_results


def search_recipe_by_title(query, conn):
    cursor = conn.cursor()
    query_embedding = model.encode([query]).tolist()[0]
    results = client.search(
        collection_name="titles_collection",
        query_vector=query_embedding,
        limit=3
    )

    formated_results = []
    for result in results:
        recipe_result = fetch_recipe_from_db(result.id, cursor)
        if recipe_result:
            formated_result = {'title': result.payload['title'], 'score': result.score, 'recipe': recipe_result[0][1]}
            formated_results.append(formated_result)
            print(f"Title: {result.payload['title']}, Score: {result.score}, Recipe: {recipe_result[0][1]}")

    return formated_results


def search_recipe_by_ingredient_vector(query, conn):
    cursor = conn.cursor()
    query_embedding = model.encode([query]).tolist()[0]

    results = client.search(
        collection_name="ingredients_collection",
        query_vector=query_embedding,
        limit=10
    )

    # Fix multiple returns of same report, although they can have different score
    for result in results:
        recipe_result = fetch_recipe_from_db(result.id, cursor)
        if recipe_result:
            print(f"Title: {result.payload['title']}, Score: {result.score}, Recipe: {recipe_result[0][1]}")


db_pool = None


def get_db_connection():
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool

    # Initialize the connection pool
    db_pool = SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        dbname=args.dbname,
        user=args.dbuser,
        password=args.dbpwd,
        host=args.dbhost,
        port=args.dbport,
    )
    print("Database connection pool created.")

    try:
        yield  # Application is running
    finally:
        db_pool.closeall()
        print("Database connection pool closed.")


# Create the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)


@app.get("/search/title")
def search_title(query: str, db=Depends(get_db_connection)):
    return search_recipe_by_title(query, db)


@app.get("/search/ingredient")
def search_title(query: str, db=Depends(get_db_connection)):
    return search_recipe_by_ingredient(query, db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a FastAPI application.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--dbhost", type=str, help="Database host", required=True)
    parser.add_argument("--dbport", type=str, help="Database port", required=True)
    parser.add_argument("--dbname", type=str, help="Database name", required=True)
    parser.add_argument("--dbuser", type=str, help="Database user", required=True)
    parser.add_argument("--dbpwd", type=str, help="Database password", required=True)

    args = parser.parse_args()
    client = QdrantClient(host="localhost", port=6333)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)
