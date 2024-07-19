##### INSTRUCTIONS #####
# This is a module with some helper functions that work on tokens, these include:
# - is_arabic_word(token)   | checks if <token> is an arabic word
# - is_symbol(token)        | checks if <token> is a symbol
# - is_punctuation(token)   | checks if <token> is a punctuation mark
# - is_number(token)        | checks if <token> is a number
# - normalize_letters(token)| normalizes the letters of a token
# - get_file_token_stats(   | returns statistics about the tokens in
#       file_path,          | the file at <file_path> and classifies
#       [stats_files]       | tokens into files in <stats_files> if
#   )                       | provided
# 
# USAGE:
# exec(open("/PATH_TO_MODULES/token_handler.py").read())
# # and then use whatever function you like
#####

##### imports #####

import sys
import re
from pathlib import Path

from Levenshtein import editops
from camel_tools.utils.charmap import CharMapper
from camel_tools.utils.charsets import AR_CHARSET
from camel_tools.utils.charsets import AR_LETTERS_CHARSET
from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET
from camel_tools.utils.charsets import UNICODE_SYMBOL_CHARSET

##### global constants #####

ALEF = 'ا'
MAD_LETTERS = ['ا', 'ي', 'و']
TATWEEL = u'\u0640'

# remove tatweel from the arabic letters
AR_LETTERS = []
for char in AR_LETTERS_CHARSET:
    if (char != TATWEEL):
        AR_LETTERS.append(char)

##### functions #####

def is_number(token):
    return token.isnumeric()

def is_punctuation(token):
    for char in token:
        if (char not in UNICODE_PUNCT_CHARSET):
            return False
    return True

def is_symbol(token):
    for char in token:
        if (char not in UNICODE_SYMBOL_CHARSET):
            return False
    return True

def is_arabic_word(token):
    has_arabic_letters = False
    for char in token:
        if (char not in AR_CHARSET):
            return False
        elif (char in AR_LETTERS):
            has_arabic_letters = True
    return has_arabic_letters

# this, CharMapper, acts like a function
normalize_letters = CharMapper({
    u'\u0625': u'\u0627',
    u'\u0623': u'\u0627',
    u'\u0622': u'\u0627',
    u'\u0671': u'\u0627',
    u'\u0649': u'\u064a',
    u'\u0629': u'\u0647',
    u'\u0640': u''
})

def get_file_token_stats(file_path, stats_files = {}):
    ### local variables ###
    # statistics object
    stats = {
        'line_count' : 0,
        'token_count' : 0,
        'average_token_count_per_line' : 0,
        'arabic_word_count' : 0,
        'number_count' : 0,
        'punctuation_count' : 0,
        'symbol_count' : 0,
        'other_tokens_count' : 0,
        'arabic_letter_count' : 0,
        'average_arabic_word_length' : 0,
    }

    ### helper inner functions ###
    # log word to file if file exists
    def conditional_word_log(word, file_key):
        if (file_key in stats_files):
            stats_files[file_key].write(word + '\n')

    # processes a single token
    def process_token(token):
        stats['token_count'] += 1

        # log token types
        if (is_number(token)):
            stats['number_count'] += 1
            conditional_word_log(token, 'numbers')
        elif (is_punctuation(token)):
            stats['punctuation_count'] += 1
            conditional_word_log(token, 'punctuations')
        elif (is_symbol(token)):
            stats['symbol_count'] += 1
            conditional_word_log(token, 'symbols')
        elif (is_arabic_word(token)):
            stats['arabic_word_count'] += 1
            conditional_word_log(token, 'arabic_words')
        else:
            stats['other_tokens_count'] += 1
            conditional_word_log(token, 'other_tokens')

        # loop through characters
        for char in token:
            # count arabic letters
            if (char in AR_LETTERS):
                stats['arabic_letter_count'] += 1

    # process an entire line
    def process_line(line):
        line = line.strip().split()
        stats['line_count'] += 1

        for token in line:
            # process token
            process_token(token)

    ### function main body ###
    file_path = Path(file_path)
    with file_path.open('r', encoding='utf-8') as input_file:
        for line in input_file:
            process_line(line)

    # calculate post processing stats
    stats['average_token_count_per_line'] = stats['token_count'] / stats['line_count']
    stats['average_arabic_word_length'] = stats['arabic_letter_count'] / stats['arabic_word_count']

    return stats
