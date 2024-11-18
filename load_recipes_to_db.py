import argparse
import json
import os
import uuid

import psycopg2

from parse_ingredients import preprocess_ingredients, remove_advertisement


def convert_recipe_id_to_uuid(recipe_id):
    namespace = uuid.NAMESPACE_DNS
    return uuid.uuid5(namespace, recipe_id)


def reset_postgres_db(cursor):
    try:
        cursor.execute(
            """
            DROP TABLE IF EXISTS INGREDIENTS;
            """
        )
        cursor.execute(
            """
            DROP TABLE IF EXISTS RECIPES;
            """
        )
    except Exception as e:
        return


def create_postgresql_db(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS RECIPES (
            ID TEXT PRIMARY KEY,
            DOCUMENT TEXT NOT NULL
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS INGREDIENTS (
            ID SERIAL PRIMARY KEY,
            RECIPE_ID TEXT NOT NULL REFERENCES RECIPES(ID) ON DELETE CASCADE,
            INGREDIENT_WORDS TEXT[] NOT NULL
        );        
        """
    )


def insert_recipe_to_postgresql_db(recipe_id, recipe_document, recipe_ingredients, conn, cursor):
    insert_document_stmt = "INSERT INTO RECIPES (ID, DOCUMENT) VALUES(%s, %s)"
    cursor.execute(insert_document_stmt, (str(recipe_id), json.dumps(recipe_document),))
    insert_ingredient_stmt = "INSERT INTO INGREDIENTS (RECIPE_ID, INGREDIENT_WORDS) VALUES(%s, %s)"
    for ingredient in recipe_ingredients:
        cursor.execute(insert_ingredient_stmt, (str(recipe_id), ingredient.split(),))
    conn.commit()


def load_recipes_from_disk(input_dir):
    recipes = {}
    if os.path.exists(input_dir):
        for file_name in os.listdir(input_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(input_dir, file_name)
                print("Load file %s" % file_path)
                # Load each JSON file and append it to the list
                with open(file_path, 'r', encoding='utf-8') as file:
                    recipes_file = json.load(file)
                    print("Loaded %d recipes" % len(recipes_file))
                    recipes.update(recipes_file)
    return recipes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Loading recipes to database.")
    parser.add_argument("--dbhost", type=str, help="Database host", required=True)
    parser.add_argument("--dbport", type=str, help="Database port", required=True)
    parser.add_argument("--dbname", type=str, help="Database name", required=True)
    parser.add_argument("--dbuser", type=str, help="Database user", required=True)
    parser.add_argument("--dbpwd", type=str, help="Database password", required=True)
    parser.add_argument("--inputfolder", type=str, help="Recipe jsons folder", required=True)

    args = parser.parse_args()

    pg_conn = psycopg2.connect(database=args.dbname, user=args.dbuser, host=args.dbhost, port=args.dbport,
                               password=args.dbpwd)
    pg_cursor = pg_conn.cursor()

    reset_postgres_db(pg_cursor)
    create_postgresql_db(pg_cursor)

    recipes_dict = load_recipes_from_disk(args.inputfolder)

    processed_recipes_list = {}
    recipes_filtered_ingredients = {}

    print('Filtering recipes')
    counter = 0

    for key, value in recipes_dict.items():
        try:
            recipe = {'id': key, 'title': value['title'], 'instructions': remove_advertisement(value['instructions'])}
            ingredients = [ingredient for ingredient in
                           [remove_advertisement(ingredient) for ingredient in value['ingredients'] if
                            ingredient is not None] if len(ingredient) > 0]
            recipe['ingredients'] = ingredients
            recipe_uuid = convert_recipe_id_to_uuid(key)
            filtered_ingredients = preprocess_ingredients(ingredients)
            processed_recipes_list[recipe_uuid] = recipe
            recipes_filtered_ingredients[recipe_uuid] = filtered_ingredients
            counter += 1
            if counter % 1000 == 0:
                print(f"Processed {counter} recipes")
        except KeyError as e:
            continue
    print("Filtered %d recipes" % counter)

    print("Uploading recipes to DB")
    counter = 0

    for recipe_id, recipe in processed_recipes_list.items():
        insert_recipe_to_postgresql_db(recipe_id, recipe, recipes_filtered_ingredients[recipe_id], pg_conn, pg_cursor)
        counter += 1
        if counter % 1000 == 0:
            print(f"Processed {counter} recipes")
    print("Uploaded %d recipes" % counter)
