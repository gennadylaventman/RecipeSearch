import argparse
import json
from datetime import datetime, timedelta

import psycopg2
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams
from sentence_transformers import SentenceTransformer


def create_qdrant_db(client):
    if not client.collection_exists(collection_name="titles_collection"):
        client.create_collection("titles_collection", VectorParams(size=384, distance="Cosine"))

def fetch_recipes_from_db(cursor):
    cursor.execute(
        """
        SELECT R.ID, R.DOCUMENT
        FROM RECIPES R
        """)
    result = cursor.fetchall()
    return [(row[0], json.loads(row[1])) for row in result if row[1] is not None]

def update_qdrant_db(recipe_id, recipe_title, title_embedding, client):
    client.upsert(
        collection_name="titles_collection",
        points=[{"id": str(recipe_id), "vector": title_embedding, "payload": {"title": recipe_title}}],
    )

def embedding_from_service(all_recipe_title):
    response = requests.post(api_url, headers=headers, json={"inputs": all_recipe_title, "options":{"wait_for_model":True}})
    return response.json()

def process_titles(recipes_chunk):
    all_recipe_title = [title for _, title in recipes_chunk]
    start_time = datetime.now()
    all_titles_embedding = model.encode(all_recipe_title)
    # all_titles_embedding = embedding_from_service(all_recipe_title)
    end_time = datetime.now()

    embedding_execution_times.append(end_time - start_time)

    for recipe_id_title, title_embedding in zip(recipes_chunk, all_titles_embedding):
        update_qdrant_db(recipe_id_title[0], recipe_id_title[1], title_embedding, qdrant_client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Loading recipes to database.")
    parser.add_argument("--dbhost", type=str, help="Database host", required=True)
    parser.add_argument("--dbport", type=str, help="Database port", required=True)
    parser.add_argument("--dbname", type=str, help="Database name", required=True)
    parser.add_argument("--dbuser", type=str, help="Database user", required=True)
    parser.add_argument("--dbpwd", type=str, help="Database password", required=True)
    parser.add_argument("--qdranthost", type=str, help="Qdrant server host", required=True)
    parser.add_argument("--qdrantport", type=str, help="Qdrant server port", required=True)

    args = parser.parse_args()

    pg_conn = psycopg2.connect(database=args.dbname, user=args.dbuser, host=args.dbhost, port=args.dbport,
                               password=args.dbpwd)
    pg_cursor = pg_conn.cursor()

    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    hf_token = "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"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}

    qdrant_client = QdrantClient(host=args.qdranthost, port=args.qdrantport)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    create_qdrant_db(qdrant_client)

    recipes = fetch_recipes_from_db(pg_cursor)

    recipe_id_title = [(row[0], row[1]['title']) for row in recipes if row[1]['title'] is not None]

    embedding_execution_times = []

    chunk_size = 5000
    recipe_id_title_chunks = [recipe_id_title[i:i + chunk_size] for i in range(0, len(recipe_id_title), chunk_size)]
    print(f"Total recipe titles to process {len(recipe_id_title)}, chunk size {chunk_size}")

    for i, chunk in enumerate(recipe_id_title_chunks):
        print(f"Processing chunk {i}")
        process_titles(chunk)

    total_embedding_execution_times = sum(embedding_execution_times, timedelta())
    print("Total Embedding Execution Time:", total_embedding_execution_times)




