# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 16:02:48 2020

@author: user
"""

import json
import sqlite3


def insert_recipe_URL(URL):
    with conn: 
        cursor.execute("""INSERT INTO recipes (URL) VALUES (?)""", (URL, ))

        
def update_recipe_URL(URL, recipe_id):
    with conn: 
        cursor.execute("""UPDATE recipes SET URL = (?) WHERE recipe_id = (?)""", (URL, recipe_id))
        
        
def update_recipe(recipe, recipe_id):
    with conn: 
        cursor.execute("""UPDATE recipes SET meta = (?) WHERE recipe_id = (?)""", (json.dumps(recipe), recipe_id))
        
        
def update_recipe_co2(recipe, recipe_id):
    with conn: 
        cursor.execute("""UPDATE recipes SET meta_co2 = (?) WHERE recipe_id = (?)""", (json.dumps(recipe), recipe_id))
    

def get_recipe_by_id(recipe_id, co2=False):
    
    if co2 == False:
        cursor.execute("SELECt meta FROM recipes WHERE recipe_id = {}".format(recipe_id))
        recipe = cursor.fetchone()[0]
        if recipe is not None:
            recipe = json.loads(recipe)
        else:
            recipe = 'No recipe'
    if co2 == True:
        cursor.execute("SELECt meta_co2 FROM recipes WHERE recipe_id = {}".format(recipe_id))
        recipe = cursor.fetchone()[0]
        if recipe is not None:
            recipe = json.loads(recipe)
        else:
            recipe = 'No recipe'
    return recipe


def get_URL_by_id(recipe_id):
    cursor.execute("SELECt URL FROM recipes WHERE recipe_id = {}".format(recipe_id))
    URL = cursor.fetchone()[0]
    return URL


def get_all_by_id(recipe_id):
    cursor.execute("SELECt * FROM recipes WHERE recipe_id = {}".format(recipe_id))
    URL = cursor.fetchone()
    return URL

def get_max_id():
    cursor.execute("SELECT COALESCE(MAX(recipe_id), 0) FROM recipes")
    max_id = cursor.fetchone()[0]
    return max_id


def delete_recipe():
    with conn: 
        cursor.execute("""UPDATE recipes SET meta = (?) WHERE recipe_id > 65000""", (None, ))

def update_autoincrement(x):
    with conn: 
        cursor.execute("""UPDATE sqlite_sequence SET seq = (?)""", (x, ))
  

def delete_enty(recipe_id):
    with conn: 
        cursor.execute("""DELETE FROM recipes WHERE recipe_id = ?""", (recipe_id, ))

      
def insert_URL(URL):
    with conn: 
        cursor.execute("""INSERT INTO recipes (URL) VALUES (?)""",(URL,))


conn = sqlite3.connect('recipe_DB.db')
cursor = conn.cursor()



 
