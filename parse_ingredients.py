import sys
import unicodedata

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

MEASURE_TOKENS = [
    'cup', 'can', 'teaspoon', 'teaspoons', 'tsp', 'tablespoon', 'tablespoons', 'tbsp', 'pound', 'lb', 'jar', 'bottle', 'stick', 'about', 'pounds', 'cups',
    'pinch', 'appx', 'half', 'optional', 'milliter', 'micro', 'ounce', 'small', 'large', 'medium', 'envelope',
    'ear', 'piece', 'drops', 'oz', 'bunch', 'slice', 'spoonful', 'advertisement', 'inch', 'one', 'two', 'box', 'ounces', 'bag', 'container',
    'grams', 'quart', 'inch', 'slices', 'cans', 'g', 'count', 'package', 'pint', 'shot', 'bags', 'pan', 'quarts', 'tbs']

PREP_TOKENS = [
    'diced', 'stewed', 'chopped', 'crumbled', 'peeled', 'minced', 'fresh', 'divided', 'cooked', 'washed', 'softened',
    'sliced', 'deveined', 'shaken', 'finely', 'toasted', 'frozen', 'mixed', 'cut', 'squeezed', 'cracked', 'halved',
    'roasted', 'grilled','dried', 'freshly', 'ground', 'coarse', 'beaten', 'blend', 'blended', 'seeded',
    'grated', 'chilled', 'garnish', 'discarded', 'powdered', 'cooled', 'sifted', 'drained', 'granulated', 'crushed', 'thinly', 'choice', 'size', 'remove',
    'plus', 'needed', 'turns', 'greasing', 'brush', 'brushing', 'top', 'taste', 'turn', 'drizzling']

def remove_advertisement(text):
    if text is not None:
        return text.replace("ADVERTISEMENT", "").strip()
    return None


def remove_stop_words(s):
    return ' '.join([i for i in s.split(' ') if i not in stop_words])

def remove_measure_prep(s):
    return ' '.join([i for i in s.split(' ') if i not in MEASURE_TOKENS and i not in PREP_TOKENS ])

def replace_plurals(s):
    stemmer = PorterStemmer()
    return ' '.join([stemmer.stem(i) for i in s.split(' ')])

tbl = dict.fromkeys(i for i in range(sys.maxunicode)
                    if unicodedata.category(chr(i)).startswith('P'))

def remove_punctuation(s):
    return s.translate(tbl)

def remove_digits(s):
    return re.sub(r'[\d]','',s)

def remove_trailing_s(token):
    if token.endswith('s'):
        return token[:-1]
    else:
        return token

def preprocess_ingredient(ingredient):
    ingredient = ingredient.lower()
    ingredient = remove_punctuation(ingredient)
    ingredient = remove_digits(ingredient)
    ingredient = remove_measure_prep(ingredient)
    ingredient = remove_stop_words(ingredient)
    return re.sub(r"\s+", " ", ingredient).strip()


def preprocess_ingredients(ingredients_list):
    return [preprocess_ingredient(ingredient) for ingredient in ingredients_list]
