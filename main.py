# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 12:41:08 2021

@author: user
"""

from scraper import get_recipe_json
from co2_connect_obj import co2_add
from utilities import recipe_to_df
import sql_queries
import time
import pandas as pd
import json
import matplotlib.pyplot as plt




# file = open(r'C:\Users\user\OneDrive\Studium\MastersThesis\average_recipe.txt', 'r', encoding='utf-8') 
# string = file.read()
# string = 'https://www.chefkoch.de/rezepte/1679731276069495/Spezial-Spare-Ribs.html'


# recipe = get_recipe_json(string)

# recipe_co2 = co2_add(recipe)

recipe_co2 = sql_queries.get_recipe_by_id(188, True)


df = recipe_to_df(recipe_co2)

replace_candidates = df.loc[df['co2kg'] > 1].sort('co2')




# df = df.set_index('ingredient_clean')

# data = df.loc[df['co2_share'] > 0, 'co2_share']

# pie, ax = plt.subplots(figsize=[8,8])
# labels = data.keys()
# plt.pie(x=data, autopct="%.1f%%", explode=[0.03]*len(data), labels=labels, pctdistance=.5)
# plt.title("Share of total CO2 emissions", fontsize=14)

# ax = df[['co2_share', 'weight_share']].plot.bar(rot=0)


# with open('recipe.json', 'w') as f:
#     json.dump(recipe_co2, f)


# # get ingredient list
# appended_recipes = []

# for r in range(1, 100):
#     try:
#         recipe = sql_queries.get_recipe_by_id(r, True)
#         if recipe['language'] == 'de':
#             print(r)
#             df = recipe_to_df(recipe)
#             appended_recipes.append(df)
#     except:
#         pass
    
# appended_recipes = pd.concat(appended_recipes)
 
# # appended_recipes.to_csv('ingredients_de.csv', index = False, header=True)

