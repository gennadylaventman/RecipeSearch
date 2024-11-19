# Recipe Search Application 

This repository contains recipe search demo application

How to run on local machine:

* `./create_new_bridge.sh` - creates new bridge network
* `./run_postgres.sh` - starts local postgres server inside docker
* `./run_qdrant.sh` - starts local Qdrant server inside docker
* `python load_recipes_to_db.py --dbhost localhost --dbport 5432 --dbname mydb --dbuser myuser --dbpwd mypassw0rd --inputfolder recipes_raw` - load recipes data from json files, clean it and store it to postgres
* `python load_recipes_to_qdrant.py --dbhost localhost --dbport 5432 --dbname mydb --dbuser myuser --dbpwd mypassw0rd --qdranthost localhost --qdrantport 6333` - create recipe title embedding and store all embeddings to Qdrant collection
* `python search_recipe.py --dbhost localhost --dbport 5432 --dbname mydb --dbuser myuser --dbpwd mypassw0rd --qdranthost localhost --qdrantport 6333 --host 0.0.0.0` - start recipe search server

Queries to search server examples:

* `http://localhost:8000/search/title?query=italian%20musaka` - returns top 5 recipes with title similar to "italian musaka"
* `http://localhost:8000/search/ingredient?query=olive%20oil%20pepper` - return all recipes that one of recipe ingredients has all three words "olive oil pepper" 