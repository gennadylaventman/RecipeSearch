#!/bin/bash

# Exit on any error
set -e

# Step 1: Initialize PostgreSQL database
echo "Starting PostgreSQL database initialization..."
python load_recipes_to_db.py \
    --dbhost postgres \
    --dbport 5432 \
    --dbname "${POSTGRES_DB}" \
    --dbuser "${POSTGRES_USER}" \
    --dbpwd "${POSTGRES_PASSWORD}" \
    --inputfolder recipes_raw

echo "PostgreSQL database initialization completed."

# Step 2: Initialize Qdrant
echo "Starting Qdrant initialization..."
python load_recipes_to_qdrant.py \
    --dbhost postgres \
    --dbport 5432 \
    --dbname "${POSTGRES_DB}" \
    --dbuser "${POSTGRES_USER}" \
    --dbpwd "${POSTGRES_PASSWORD}" \
    --qdranthost qdrant \
    --qdrantport 6333

echo "Qdrant initialization completed."
