# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 17:05:51 2021

@author: user
"""

from utilities import Quantity
import pandas as pd


PATH = r'C:\Users\user\OneDrive\Studium\MastersThesis\python\data'
conv = pd.read_csv(PATH + '\\measurements.csv').fillna('').values.tolist()

# get list of measurements
meas = []
for c in conv:
    for m in c[1].split(','):
        meas.append(m.strip())
all_units = ('|'.join(meas))



class ParseString():
    
    def __init__(self, string):
        self.string_split = string.replace('\n', ';').split(';')
        
    
    @classmethod
    def host(self):
        return 'string_parser'
    
    
    def ingredients(self):
        
        ingredients = []
        for i in self.string_split:
            
            if len(i) > 1:
                ingredients.append(i)
        
        return ingredients
            
    
    def title(self):
        return 'not specified'

    
    def total_time(self):
        return 'not specified'
    

    def instructions(self):
        return 'no instructions'


    def image(self):
        return 'not specified'
    
    
    def nutrients(self):              
        return {}


    def language(self):
        return 'not specified'


    def yields(self):
        return 'not specified'





# file = open(r'C:\Users\user\OneDrive\Studium\MastersThesis\ExampleRecipe.txt', 'r', encoding='utf-8')
# string = file.read()


# x = ParseString(string)

# unit = x.ingredients()




