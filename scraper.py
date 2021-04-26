# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 22:13:16 2021

@author: user
"""


import re

from allrecipes import AllRecipes
from fooby import Fooby
from chefkoch import Chefkoch
from recipe_scrapers import scrape_me
from local_file_parser import ParseString
from utilities import Quantity

import requests

import time


SCRAPERS = {
    AllRecipes.host(): AllRecipes,
    Fooby.host(): Fooby,
    Chefkoch.host(): Chefkoch,
    ParseString.host(): ParseString
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
}


def url_path_to_dict(path):
    pattern = (r'^'
               r'((?P<schema>.+?)://)?'
               r'(?P<host>.*?)'
               r'(?P<path>/.*?)?'
               r'(?P<query>[?].*?)?'
               r'$'
               )
    regex = re.compile(pattern)
    matches = regex.match(path)
    url_dict = matches.groupdict() if matches is not None else None

    return url_dict


def recipe_scraper(url_path):
    try:
        requests.get(url_path, headers = HEADERS)
        is_url = True
    except:
        is_url = False
        
    if is_url is True:
        url_path = url_path.replace('://www.', '://')
        host = url_path_to_dict(url_path)['host']
        try:
            return SCRAPERS[host](url_path)
        except KeyError:
            return scrape_me(url_path)
    else:
        x = url_path_to_dict('string_parser')
        soup = url_path
        return SCRAPERS[x['host']](soup)
    
    
def get_recipe_json(url_path):
    
    try:
        recipe_obj = recipe_scraper(url_path)
    except:
        recipe_obj = scrape_me(url_path, wild_mode=True)
    
    recipe = {}
    recipe['recipe_id'] = 1
    recipe['URL'] = url_path
    recipe['title'] = recipe_obj.title()
    ingredients = recipe_obj.ingredients()
    
    ingredients_qty = []
    for ing in ingredients:
        if type(ing) is not dict:
            quantity_obj = Quantity(ing)
            ing_dict = {'ingredient': quantity_obj.ing(),
                        'quantity': quantity_obj.qty_ing()}
            ingredients_qty.append(ing_dict)
        else:
            ingredients_qty.append(ing)     
        
    recipe['ingredients'] = ingredients_qty
    recipe['instructions'] = recipe_obj.instructions()
    recipe['image'] = recipe_obj.image()
    recipe['totalTime'] = recipe_obj.total_time()
    recipe['recipeYield'] = recipe_obj.yields()
    recipe['nutrients'] = recipe_obj.nutrients()
    recipe['language'] = recipe_obj.language()
    recipe['scraped'] = time.ctime(time.time())
    
    return recipe

    
