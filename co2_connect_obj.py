import re
from nltk.metrics.distance import jaccard_distance
from nltk.util import ngrams
from fuzzywuzzy import fuzz
import pandas as pd
import numpy as np
import time
from utilities import Quantity
from utilities import clean_text, find_words

# Fetching all relevant data
PATH = r'C:\Users\user\OneDrive\Studium\MastersThesis\python\data'

attributes = pd.read_csv(PATH + '\\attributes.csv').fillna('')

weights = pd.read_csv(PATH + '\\weights.csv').fillna('')
conv = pd.read_csv(PATH + '\\measurements.csv').fillna('').values.tolist()
density_list = pd.read_csv(PATH + '\\food_densities.csv').fillna('').values.tolist()


filler_lists = {'en': pd.read_csv(PATH + '\\filler_strings.csv')['en'].values.tolist(),
                'de': pd.read_csv(PATH + '\\filler_strings.csv')['de'].values.tolist(),
                'it': pd.read_csv(PATH + '\\filler_strings.csv')['it'].values.tolist()}

reference_lists = {'en': pd.read_csv(PATH + '\\reference_list_en.csv'),
                   'de': pd.read_csv(PATH + '\\reference_list_de.csv'),
                   'it': pd.read_csv(PATH + '\\reference_list_it.csv')}


def co2_add(recipe_json):
    # determine language of the selected recipe
    languages = {'en': 0,
                 'de': 1,
                 'it': 2
                 }

    try:
        lang = recipe_json['language'].lower()
    except KeyError:
        lang = input('Please specify the recipes language (en, de or it): ').lower()
        recipe_json['language'] = lang

    if lang == 'en-us' or lang == 'nan':
        lang = 'en'
        recipe_json['language'] = lang
    
    lang_code = None
    while lang_code == None:
        try:
            lang_code = languages[lang]
        except KeyError:
            print('language "' + lang + '" not supported')
            lang = input('Please specify the recipes language (en, de or it): ').lower()
            recipe_json['language'] = lang


    full_list = reference_lists[lang]

    # get list of filler strings
    filler_list = filler_lists[lang]
    filler_reg = re.compile(r'\b(%s)\S{0,1}\b' % '|'.join(filler_list), re.IGNORECASE)

    nomatchcount = 0
    noquantitycount = 0


    co2_values = []
    ingweights = []

    for r in recipe_json['ingredients']:

        # print(r)
        qty = r['quantity']
        ing = r['ingredient']
        
        qty_orig = qty
        ing_orig = ing

        warnings = []   
        nomatch = False
        noco2 = False

        # check if attribute is specified in the ingredient entry
        ing_attributes = []
        for index, row in attributes.iterrows():
            if row[lang] in ing:
                ing_attributes.append(row['en'])
                
                
        # remove filler strings from ingredient and quantity
        try:
            ing = re.sub(filler_reg, '', ing).strip()
        except TypeError:
            pass
        try:
            qty = re.sub(filler_reg, '', qty).strip()
        except TypeError:
            pass
        
        
        quantity_object_qty = Quantity(qty)

        unit = quantity_object_qty.unit
        count = quantity_object_qty.count
        qty = quantity_object_qty.qty_qty()

        # if quantity could not be determined look if quantity is specified in ingredients and set qty accordingly
        if qty is None:
            quantity_object_ing = Quantity(ing)
            unit = quantity_object_ing.unit
            count = quantity_object_ing.count

            if unit is not None:
                qty = quantity_object_ing.qty_ing()

        # final cleanup of ing 
        ing = re.sub(r'[0-9]', '', ing).strip()

        ing_split = ing

        # split ingredient at certain words, ',' and '('
        ing_split = re.sub(r'\b(or|oder)\b|([()])', ',', ing_split)

        ing_split = ing_split.split(',')
        ing_split = list(map(str.strip, ing_split))

        # Calculate Jaccard Distance
        # df_temp = pd.DataFrame()

        # for ing_part in ing_split:
        #     full_list['score'] = full_list.apply(lambda row: 1 - jaccard_distance(set(ngrams(ing_part, 2)),
        #                                                                           set(ngrams(row['ref'], 2))), axis=1)
        #     df_temp = df_temp.append(full_list)

        # final_df = df_temp.sort_values(by=['score'], ascending=False)

        # Calculate Levenshtein Distance
        full_list['score'] = full_list.apply(lambda row : (fuzz.partial_ratio(row['ref'], ing)*0.5 + 
                                                           fuzz.token_sort_ratio(row['ref'], ing)*0.5)/100, axis = 1)
        
        final_df = full_list.sort_values(by=['score'], ascending=False)
        
        # print(final_df)

        co2_calc = []
        for scr in range(10):

            if find_words(ing_orig, final_df.iloc[scr].ref):

                if final_df.iloc[scr]['attribute'] in ing_attributes:
                    match = final_df.iloc[scr]
                    break

                match = final_df.iloc[scr]
                if not pd.isna(final_df.iloc[scr].co2):
                    co2_calc.append(final_df.iloc[scr].co2)

                if match.ref == final_df.iloc[scr + 1].ref:
                    continue
                else:
                    # if multiple indendical entries take average co2
                    if len(co2_calc) > 1:
                        match.co2 = sum(co2_calc) / len(co2_calc)
                        warnings.append('avg')
                    break
                

        else:
            nomatch_data = {'en_key': 'nomatch',
                            'ref': ing,
                            'lang_key': ing,
                            'type': np.nan,
                            'co2': 'NaN',
                            'classification': np.nan,
                            'attribute': np.nan,
                            'variety': np.nan,
                            'score': np.nan}
            match = pd.Series(nomatch_data)

            nomatchcount = nomatchcount + 1
            warnings.append('nomatch')
            warnings.append('noco2')
            nomatch = True
            noco2 = True

        # if float(match.score) < 0.6:
        #     warnings.append('sim')
            
        if float(match.score) < 0.8:
            warnings.append('sim')

        if pd.isna(match.co2):
            warnings.append('noco2')
            noco2 = True
            match.co2 = None

        # print(match.score)

        ingre = match.en_key
        co2kg = match.co2
        ingweight = None

        if qty is None:
            ingweight = None

        if qty_orig == '':
            ingweight = 0

        # look up weight of measurement
        if unit is not None:
            for c in conv:
                for m in c[1].split(','):
                    if unit.lower() == m.strip().lower() and c[2] != '':
                        # qty = qty.replace(unit, c[0])
                        # for 'a little' etc
                        if count is None:
                            count = 1
                        density = None
                        # check if ingredient is in density list if volume measurement
                        if c[3] == 'volume':
                            for d in density_list:
                                if ingre == d[0]:
                                    # check if attribute is specified. If not take the average of all entries
                                    if d[1] in ing_attributes:
                                        density = d[2]
                                    else:
                                        density = d[3]
                            # standard density of one if no match
                            if density is None:
                                density = 1
                                if nomatch is False:
                                    warnings.append('nodensity')

                            ingweight = round(c[2] * float(density) * count, 5)
                            break

                        else:
                            ingweight = round(float(c[2]) * count, 5)
                            break

        # look up weights of single items
        if qty is not None and 'item' in qty:
            try:
                weight = weights.loc[weights['en'] == ingre]['weight'].values[0]
                ingweight = round(weight * count, 5)
            except IndexError:
                ingweight = None


        # Add weight to list for total weight calculation
        if ingweight is not None:
            ingweights.append(ingweight)

        # Calculate co2 value for given ingredient weight
        if ingweight is not None and noco2 is False:
            onegram = float(co2kg) / 1000
            co2 = round(onegram * float(ingweight), 5)

            co2_values.append(co2)

        # if weight in grams cannot determined add measure to missing quantity list
        elif ingweight is None:
            co2 = None

            noquantitycount = noquantitycount + 1
            warnings.append('noquantity')

        # quantity in grams determined but no match
        else:
            co2 = None

        if co2kg == 'NaN':
            co2kg = None

        # replace ingre with cleaned up ingredient if no match
        if ingre == 'nomatch':
            ingre = clean_text(ing_split[0])
            match.lang_key = ing_split[0]

        # Add new entries to the dictionary
        r['ingredient_clean'] = ingre
        r['ingredient_clean_lang'] = match.lang_key
        r['weight'] = ingweight
        r['co2kg'] = co2kg
        r['quantity_clean'] = qty
        r['co2'] = co2
        r['attributes'] = ing_attributes
        r['warnings'] = warnings
        
        # print(r)

    # calculate co2 and weight totals
    co2_total = round(sum(co2_values), 5)
    weight_total = round(sum(ingweights), 5)

    # Add new entries to the dictionary
    recipe_json['co2_total'] = co2_total
    recipe_json['weight_total'] = weight_total
    recipe_json['noquantity'] = noquantitycount
    recipe_json['nomatch'] = nomatchcount

    return recipe_json


# recipe = {'recipe_id': 1,
#  'URL': 'https://www.epicurious.com/recipes/food/views/the-ba-burger-deluxe-51179070',
#  'title': 'Burger Deluxe',
#  'ingredients': [{'ingredient': 'Bürgerbrot', 'quantity': '3.0 pounds'},
#   {'ingredient': 'Weißkohl x', 'quantity': '200 ml'},
#   {'ingredient': 'Käse ganze Stücke', 'quantity': '0.5 kg'},
#   {'ingredient': 'Öl, split and grilled', 'quantity': '8.0 liter'}],
#  'language': 'de',
#  'scraped': 'Sat Apr 24 17:46:03 2021'}

# x = co2_add(recipe)


# start = time.time()
# i = 0
# while i < 20:
#     x = co2_add(recipe)
#     i = i+1
# print(f'Time: {time.time() - start}')


