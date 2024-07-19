##### instructions #####
# This is a module with some helper functions that work on diacritics, these include:
# - singular_of_tanween(tanween)     | returns the singular form of <tanween>
# - has_diac(word)                   | checks if <word> has a diac
# - has_full_diac(word)              | checks if the diacritizatoin on <word> is full
# - remove_contextual_diac_flags(w)  | removes contextual flags
# - get_leading_diac_group(word)     | returns the diacs before the first letter in <word>
# - separate_letters_and_diacs(word) | returns one list of letters and one of diac groups
# - is_canonical_diac_group(grp)     | checks if the diac group <grp> is canonical
# - is_canonical_word_diac(word)     | checks if all <word> diacritization is canonical
# - is_valid_full_diac(word)         | checks if the full diacritization of a word is valid
# - are_valid_full_diac(words)       | checks if full diacritization of some words are valid
# - fix_shadda_order(word)           | bring shadda before other diacritics
# - has_shadda_error(word)           | checks if the word has a shadda error
# - reorder_tanween_fath(word, form) | normalize tanween fath to the given form
# - has_tanween_error(word)          | checks if the word has a tanween fath order error
# - normalize_diac(word)             | normalizes the diacritization of <word>, see below
# - compare_diac(orig, new)          | normalizes both, and compares their diacritics
# - get_file_diac_stats(             | returns a dictionary of all the statistical data
#       file_path,                   | related to the diacritics of the text inside the
#       [stats_files]                | file at <file_path>, and puts the different token
#   )                                | categories in <stats_files> if provided
# - compare_word_diac(orig, new)     | returns statistics about the diacritization changes
#                                    | going from the word <orig> to <new>
# - compare_file_diac(orig, new)     | returns statistics about the diacritization changes
#                                    | going from the file <orig> to <new>
# 
# The way normalize_diac works is as follows
# > non-arabic words are left as they are
# > all tatweels, dagger alefs, and maddas are removed
# > non-shadda-diac before the word is removed
# > sukuns are all removed
# > if multiple non-shadda-diacs were given only the first is considered
# > if another single non-shadda-diac or tanween reminicent of the first non-shadda-diac, the non-shadda-diac was
#   placed is turned to a tanween and the tanween is tested based on the tanween criteria below
# > if there are diacritics on an alef they are removed except for tanween-fath if at the end
# > if shadda is placed on an alef-mad preceded by a letter it is moved to the letter
# > if a non-shadda-diac is on the letter before an alef-mad, non-shadda-diac is removed
# > if shaddas are given, one shadda is placed before any non-shadda-diac on that letter
# > if a tanween is in the middle of the word it is reduced to its single non-shadda-diac if valid
# > if a tanween fath is placed at the end of the word and the ending letter is not one of the
#   TANWEEN_FATH_LETTERS then an alef is added afterwards
# > if a tanween fath is on the letter before the last letter and the last letter is alef
#   it is moved to the alef
# 
# USAGE:
# exec(open("/PATH_TO_MODULES/diac_handler.py").read())
# # and then use whatever function you like
#####

##### imports #####

import sys
import re
from pathlib import Path

from Levenshtein import editops
from camel_tools.utils.charsets import AR_CHARSET
from camel_tools.utils.charsets import AR_DIAC_CHARSET
from camel_tools.utils.charsets import AR_LETTERS_CHARSET

##### global constants #####

ALEF = '\u0627'; WAW = '\u0648'; YAA = '\u064a'
ALEF_WASLA = '\u0671'
ALEF_MAQSURA = '\u0649'
ALEF_MADDA = '\u0622'
MAD_LETTERS = [ALEF, ALEF_MAQSURA, ALEF_MADDA, WAW, YAA]
BAA = '\u0628'; TAA = '\u062a'; LAM = '\u0644'; FAA = '\u0641'; KAF = '\u0643'
TAA_MARBUTA = '\u0629'
HAMZA = '\u0621'; HAMZA_ON_ALEF = '\u0623'; HAMZA_UNDER_ALEF = '\u0625'
HAMZA_ON_NABRA = '\u0626'; HAMZA_ON_WAW = '\u0624'

TATWEEL = u'\u0640'

FATHA = u'\u064e'
DAMMA = u'\u064f'
KASRA = u'\u0650'
SUKUN = u'\u0652'
SHADDA = u'\u0651'
TANWEEN_FATH = u'\u064b'
TANWEEN_DAM = u'\u064c'
TANWEEN_KASR = u'\u064d'
DAGGER = u'\u0670'
MADDA = u'\u0653'

SINGLE_NON_SUKUN_DIACS = [FATHA, DAMMA, KASRA]
SINGLE_NON_SHADDA_DIACS = SINGLE_NON_SUKUN_DIACS + [SUKUN]
TANWEENS = [TANWEEN_FATH, TANWEEN_DAM, TANWEEN_KASR]
NON_SHADDA_DIACS = SINGLE_NON_SHADDA_DIACS + TANWEENS
AR_DIACS = NON_SHADDA_DIACS + [SHADDA, DAGGER]

# remove tatweel from the arabic letters
AR_LETTERS = []
for char in AR_LETTERS_CHARSET:
    if (char != TATWEEL):
        AR_LETTERS.append(char)

NON_MAD_LETTERS = []
for char in AR_LETTERS:
    if (char != ALEF and char != ALEF_MAQSURA and char != ALEF_MADDA):
        NON_MAD_LETTERS.append(char)

# SUN_LETTERS = ['ن', 'ل', 'ظ', 'ط', 'ض', 'ص', 'ش', 'س', 'ز', 'ر', 'ذ', 'د', 'ث', 'ت']
NON_WORD_STARTING_LETTERS = [TAA_MARBUTA, HAMZA, HAMZA_ON_NABRA, HAMZA_ON_WAW, ALEF_MAQSURA]
NON_ALEF_WASL_FOLLOWING_LETTERS = [ALEF, ALEF_MADDA, TAA_MARBUTA, HAMZA, HAMZA_ON_ALEF, HAMZA_UNDER_ALEF, ALEF_MAQSURA]
SUN_LETTERS = ['\u0646', '\u0644', '\u0638', '\u0637', '\u0636', '\u0635', '\u0634', '\u0633', '\u0632', '\u0631', '\u0630', '\u062f', '\u062b', '\u062a']
MOON_LETTERS = [letter for letter in AR_LETTERS if (letter not in SUN_LETTERS and letter not in NON_WORD_STARTING_LETTERS)]

# alef wasl following letters
ALEF_WASL_FOLLOWING_LETTERS = []
for char in AR_LETTERS:
    if (char not in NON_ALEF_WASL_FOLLOWING_LETTERS):
        ALEF_WASL_FOLLOWING_LETTERS.append(char)

WORD_STARTING_LETTERS = []
for char in AR_LETTERS:
    if (char not in NON_WORD_STARTING_LETTERS):
        WORD_STARTING_LETTERS.append(char)

# compare_file_diac constant
DIAC_COMPARISON_TSV_FIELDS = [
    'orig_after_scope',
    'orig_token',
    'orig_prev_scope',
    'new_token',
    'insertion_count',
    'deletion_count',
    'substitution_count',
    'word_length_changed',
]

# number of tokens to capture in the before and after scopes
WORD_SCOPE_RADIUS = 5

# regular expressions
HAS_DIAC_REGEX = re.compile(r'[' + ''.join(AR_DIACS) + r']')
IS_CANONICAL_DIAC_GROUP_REGEX = re.compile( \
        r'^(' + \
        SHADDA + r'?' + \
        r'[' + ''.join(NON_SHADDA_DIACS) + r']?' + \
        DAGGER + r'?' + \
        r')$')

##### regexes #####

AR_LETTER = r'(' + r'|'.join(AR_LETTERS) + r')'
MAD_LETTER = r'(' + r'|'.join(MAD_LETTERS) + r')'
NON_MAD_LETTER = r'(' + r'|'.join(NON_MAD_LETTERS) + r')'
SUN_LETTER = r'(' + r'|'.join(SUN_LETTERS) + r')'
MOON_LETTER = r'(' + r'|'.join(MOON_LETTERS) + r')'
WORD_STARTING_LETTER = r'(' + r'|'.join(WORD_STARTING_LETTERS) + r')'
ALEF_WASL_FOLLOWING_LETTER = r'(' + r'|'.join(ALEF_WASL_FOLLOWING_LETTERS) + r')'

AR_DIAC = r'(' + r'|'.join(AR_DIACS) + r')'
SINGLE_NON_SUKUN_DIAC = r'(' + r'|'.join(SINGLE_NON_SUKUN_DIACS) + r')'
SINGLE_NON_SHADDA_DIAC = r'(' + r'|'.join(SINGLE_NON_SHADDA_DIACS) + r')'
NON_SHADDA_DIAC = r'(' + r'|'.join(NON_SHADDA_DIACS) + r')'

WRONG_SHADDA_ORDER_REGEX = re.compile(r'(?P<non_shadda_diac>' + NON_SHADDA_DIAC + r')' + SHADDA)
TANWEEN_FATH_BEFORE_ALEFS_REGEX = re.compile(TANWEEN_FATH + r'(?P<alef>('+ ALEF + r'|' + ALEF_MAQSURA + r'))')
TANWEEN_FATH_AFTER_ALEFS_REGEX = re.compile(r'(?P<alef>('+ ALEF + r'|' + ALEF_MAQSURA + r'))' + TANWEEN_FATH)

FULL_DIAC_GENERAL_EXCEPTIONS = [r'عَمْرَو', r'عَمْرِو', r'عَمْرٌو', r'عَمْرٍو', r'اللهَ', r'اللهِ', r'اللهُ', r'للهِ']
# FULL_DIAC_END_EXCEPTIONS = [r'عَمْرْو']
FULL_DIAC_END_EXCEPTIONS = [u'\u0639\u064e\u0645\u0652\u0631\u0652\u0648']
MIDDLE_DIAC_GROUP = r'(' + \
                        r'(?# optional shadda)' + \
                        SHADDA + r'?' + \
                        r'(?# prevent sukun then shadda on two consecutive letters mid word)' + \
                        r'(?<!' + SUKUN + AR_LETTER + SHADDA + r')' + \
                        r'(?# fatha with optional dagger, damma, kasra, or sukun without a shadda)' + \
                        r'(' + FATHA + DAGGER + r'?|' + DAMMA + r'|' + KASRA + r'|(?<!' + SHADDA + r')' + SUKUN + r')' + \
                        r'(?# prevent two sukuns on two consecutive letters mid word)' + \
                        r'(?<!' + SUKUN + AR_LETTER + SUKUN + r')' + \
                    r')'
IS_VALID_FULL_DIAC_EXCEPTION_REGEX = re.compile(r'^(' + \
                                                    r'(' + \
                                                        r'(\?|\^|<)(' + r'|'.join(FULL_DIAC_GENERAL_EXCEPTIONS) + r')(\?|<|>)(\?|\$|>)'
                                                    r')|(' + \
                                                        r'(\?|\^|<)(' + r'|'.join(FULL_DIAC_END_EXCEPTIONS) + r')(\?|<|>)(\?|\$)'
                                                    r')' + \
                                                r')$')
IS_VALID_FULL_DIAC_REGEX = re.compile(r'^(' + \
                                        r'(\?|\^|<)' + \

                                        r'(?# pre-context conditions)' + \
                                        r'((' + \
                                            r'(?# enforce diac on hamzat kat3)' + \
                                            r'(?<=(\?|\^))(?=' + ALEF + SINGLE_NON_SUKUN_DIAC + r')' + \
                                        r')|(' + \
                                            r'(?# other letters)' + \
                                            r'(?<=(\?|\^))(?!' + ALEF + r')' + \
                                        r')|(' + \
                                            r'(?# enforce no diac on alef wasl)' + \
                                            r'(?<=(\?|<))(?=' + ALEF + r'(?!' + AR_DIAC + r'))' + \
                                        r')|(' + \
                                            r'(?# other letters)' + \
                                            r'(?<=(\?|<))(?!' + ALEF + r')' + \
                                        r')|(' + \
                                            r'(?# allow alef with madda anywhere)' + \
                                            r'(?<=(\?|\^|<))(?=' + ALEF_MADDA + r')' + \
                                        r'))' + \

                                        r'(?# starting patterns)' + \
                                        r'(' + \
                                            r'(' + \
                                                r'(?# alef wasl with optional diac and followed by a saken or shadda)' + \
                                                ALEF + \
                                                SINGLE_NON_SUKUN_DIAC + r'?' + \
                                                r'(?=' + ALEF_WASL_FOLLOWING_LETTER + r'(' + SUKUN + r'|' + SHADDA + r'))' + \
                                            r')|(' + \
                                                r'(?# alef madda with no diacritic)' + \
                                                ALEF_MADDA + \
                                            r')|(' + \
                                                r'(?# lam shamseya with no prefixes and with fatha)' + \
                                                ALEF + FATHA + \
                                                LAM + r'(?=' + SUN_LETTER + SHADDA + r')' + \
                                            r')|(' + \
                                                r'(?# lam shamseya with prefixes)' + \
                                                r'((' + FAA + FATHA + r')|(' + WAW + FATHA + r'))?' + \
                                                r'((' + \
                                                    r'((' + BAA + KASRA + r')|(' + KAF + FATHA + r'))' + r'?' + ALEF + \
                                                r')|(' + \
                                                    LAM + KASRA + \
                                                r'))' + \
                                                LAM + r'(?=' + SUN_LETTER + SHADDA + r')' + \
                                            r')|(' + \
                                                r'(?# lam qamareya maksura followed by alef wasl)' + \
                                                ALEF + FATHA + LAM + KASRA + ALEF + \
                                                r'(?=' + ALEF_WASL_FOLLOWING_LETTER + r'(' + SUKUN + r'|' + SHADDA + r'))' + \
                                            r')|(' + \
                                                r'(?# lam qamareya maksura followed by alef wasl and preceded by prefixes)' + \
                                                r'((' + FAA + FATHA + r')|(' + WAW + FATHA + r'))?' + \
                                                r'((' + \
                                                    r'((' + BAA + KASRA + r')|(' + KAF + FATHA + r'))' + r'?' + ALEF + \
                                                r')|(' + \
                                                    LAM + KASRA + \
                                                r'))' + \
                                                LAM + KASRA + ALEF + \
                                                r'(?=' + ALEF_WASL_FOLLOWING_LETTER + r'(' + SUKUN + r'|' + SHADDA + r'))' + \
                                            r')|(' + \
                                                r'(?# prefixes and optional alef wasl)' + \
                                                r'((' + FAA + FATHA + r')|(' + WAW + FATHA + r'))?' + \
                                                r'((' + BAA + KASRA + r')|(' + KAF + FATHA + r')|(' + LAM + KASRA + r'))' + r'?' + \
                                                r'(' + ALEF + r'(?=' + ALEF_WASL_FOLLOWING_LETTER + r'(' + SUKUN + r'|' + SHADDA + r'))?)' + \
                                            r')' + \
                                        r')?' + \

                                        r'(?# middle patterns)' + \
                                        r'(' + \
                                            r'(' + \
                                                NON_MAD_LETTER + \
                                                MIDDLE_DIAC_GROUP + \
                                            r')|(' + \
                                                r'(' + \
                                                    r'(?<=' + FATHA + r')' + ALEF + \
                                                r')|(' + \
                                                    r'(?<=' + KASRA + r')' + YAA + \
                                                r')|(' + \
                                                    r'(?<=' + DAMMA + r')' + WAW + \
                                                r')|(' + \
                                                    ALEF_MADDA + \
                                                r')' + \
                                            r')' + \
                                        r')*' + \

                                        r'(?# ending patterns)' + \
                                        r'(' + \
                                            r'(' + \
                                                NON_MAD_LETTER + SHADDA + r'?' + \
                                                r'(?<!' + SUKUN + NON_MAD_LETTER + SHADDA + r')' + \
                                                r'((' + \
                                                    r'(' + SUKUN + r'|' + TANWEEN_DAM + r'|' + TANWEEN_KASR + r')' + \
                                                r')|(' + \
                                                    TANWEEN_FATH + r'(' + ALEF + r'|' + ALEF_MAQSURA + r')' + \
                                                    r'(?=(\?|<))' + \
                                                r')|(' + \
                                                    r'(' + ALEF + r'|' + ALEF_MAQSURA + r')' + TANWEEN_FATH + \
                                                    r'(?=(\?|>))' + \
                                                r'))' + \
                                            r')|(' + \
                                                r'(' + HAMZA + r'|' + HAMZA_ON_ALEF + r'|' + TAA_MARBUTA + r')' + TANWEEN_FATH + \
                                            r')|(' + \
                                                WAW + SUKUN + r'?' + ALEF + \
                                            r')|(' + \
                                                r'(?<=' + FATHA + r')' + ALEF_MAQSURA + \
                                            r')' + \
                                        r')?' + \


                                        r'(?# post-context conditions)' + \
                                        r'((' + \
                                            r'(?=(\?|<|>)(\?|\$))?' + \
                                        r')|(' + \
                                            r'(?<!' + NON_MAD_LETTER + SHADDA + SUKUN + r')(?=(\?|<|>)(>))?' + \
                                            r'(?<!' + NON_MAD_LETTER + SUKUN + NON_MAD_LETTER + SUKUN + r')(?=(\?|<|>)(>))?' + \
                                        r'))' + \

                                        r'(\?|<|>)' + \
                                        r'(\?|\$|>)' + \
                                    r')$')

##### functions #####

def singular_of_tanween(diac):
    if (diac == TANWEEN_FATH):
        return FATHA
    elif (diac == TANWEEN_DAM):
        return DAMMA
    elif (diac == TANWEEN_KASR):
        return KASRA
    else:
        return diac

def has_diac(word):
    return HAS_DIAC_REGEX.search(word) is not None

def has_full_diac(word):
    letters, diac_groups = separate_letters_and_diacs(word)

    non_shadda_diac_count = 0

    index = 0
    while (index < len(letters)):
        group = diac_groups[index]
        letter = letters[index]

        # check for non-shadda-diac if a letter is not a mad
        has_non_shadda_diac = False
        # check for a non-shadda-diac
        for diac in group:
            if (diac in NON_SHADDA_DIACS):
                has_non_shadda_diac = True
                non_shadda_diac_count += 1

        # if a letter doesn't have a non-shadda-diac and is not a mad
        if (letter not in MAD_LETTERS and not has_non_shadda_diac):
                return False

        index += 1

    if (non_shadda_diac_count == 0):
        return False

    return True

CONTEXTUAL_DIACS_FLAG_RE = re.compile('%.+')
def remove_contextual_diac_flags(word):
    return CONTEXTUAL_DIACS_FLAG_RE.sub('', word)

def get_leading_diac_group(word):
    leading_diac_group = ''
    for char in word:
        if (char == TATWEEL):
            continue
        elif (char in AR_DIAC_CHARSET):
            leading_diac_group = leading_diac_group + char
        elif (char in AR_LETTERS_CHARSET):
            break

    return leading_diac_group

def separate_letters_and_diacs(word):
    letters = []
    diac_groups = []
    for char in word:
        if (char == TATWEEL):
            continue
        elif (char in AR_DIAC_CHARSET):
            if (len(diac_groups) != 0):
                diac_groups[-1] = diac_groups[-1] + char
        elif (char in AR_LETTERS_CHARSET):
            letters.append(char)
            diac_groups.append('')
        else:
            # foreign character
            # print("foreign character '", char, "' passed to separate_letters_and_diacs")
            pass

    return letters, diac_groups

def is_canonical_diac_group(diac_group):
    return IS_CANONICAL_DIAC_GROUP_REGEX.match(diac_group) is not None

# !!! DEPRECATED !!!
# criteria:
# no leading diac group
# all diac groups are canonical
# tanween only at the end of word 
# tanween fath can be before alef or alef maksurah
# shadda sukun can only occur at the end
def is_canonical_word_diac(word):
    leading_diac_group = get_leading_diac_group(word)
    if (leading_diac_group != ''):
        return False
    
    letters, diac_groups = separate_letters_and_diacs(word)
    assert(len(letters) == len(diac_groups))

    for i, diac_group in enumerate(diac_groups):
        if (not is_canonical_diac_group(diac_group)):
            return False

        non_shadda_diac = None
        shadda = False
        dagger = False
        for diac in diac_group:
            if (diac in NON_SHADDA_DIACS):
                non_shadda_diac = diac
            elif (diac == SHADDA):
                shadda = True
            elif (diac == DAGGER):
                dagger = True

        # tanween
        if (non_shadda_diac in TANWEENS):
            # tanween fath
            if (non_shadda_diac == TANWEEN_FATH):
                if (i != len(letters) - 1 and
                        not (i == len(letters) - 2 and letters[-1] == ALEF)):
                    return False
            # tanween dam or kasr
            else:
                if (i != len(letters) - 1):
                    return False

        # shadda sukun
        if (shadda and non_shadda_diac == SUKUN):
            if (i != len(letters) - 1):
                return False

    return True

def is_valid_full_diac(word, has_pre_context = None, has_post_context = None, tanween_fath_form = None):
    # remove tatweels
    new_word = ''
    for char in word:
        if char != TATWEEL:
            new_word += char
    word = new_word

    # regex parameters
    prefix_parameter = r'?'
    if (has_pre_context == True):
        prefix_parameter = r'<'
    elif (has_pre_context == False):
        prefix_parameter = r'^'

    tanween_parameter = r'?'
    if (tanween_fath_form == True):
        tanween_parameter = r'<'
    elif (tanween_fath_form == False):
        tanween_parameter = r'>'

    suffix_parameter = r'?'
    if (has_post_context == True):
        suffix_parameter = r'>'
    elif (has_post_context == False):
        suffix_parameter = r'$'

    pattern = prefix_parameter + word + tanween_parameter + suffix_parameter

    # validity testing
    is_valid = False

    # run through exceptions regex
    if (IS_VALID_FULL_DIAC_EXCEPTION_REGEX.match(pattern) is not None):
        is_valid = True

    # run through standard regex
    if (IS_VALID_FULL_DIAC_REGEX.match(pattern) is not None):
        is_valid = True

    return is_valid

def are_valid_full_diacs(words, tanween_fath_form = None):
    return [is_valid_full_diac(word, tanween_fath_form = tanween_fath_form)
            for word in words]

def is_valid_contextual_diac(precontext, word, postcontext):
    ignored_characters = [' ', '\t']

    ### get pre and post context characters
    precontext_char = None
    for char in precontext[::-1]:
        found = False
        for ignored_char in ignored_characters:
            if char == ignored_char:
                found = True

        if not found:
            precontext_char = char
            break

    postcontext_char = None
    for char in postcontext[:]:
        found = False
        for ignored_char in ignored_characters:
            if char == ignored_char:
                found = True

        if not found:
            postcontext_char = char
            break

    ### pre-context checks
    if word[0] == ALEF:
        if precontext_char is None or is_punctuation(precontext_char):
            if len(word) < 2 or word[1] not in SINGLE_NON_SUKUN_DIACS:
                return False
        else:
            if len(word) >= 2 and word[1] in SINGLE_NON_SUKUN_DIACS:
                return False

    ### post-context checks
    if postcontext_char == ALEF:
        if word[-1] == SUKUN:
            return False

    return True

def fix_shadda_order(word):
    new_word,_ = WRONG_SHADDA_ORDER_REGEX.subn(SHADDA + '\\g<non_shadda_diac>', word)
    return new_word

def has_shadda_error(word):
    return (word != fix_shadda_order(word))

def reorder_tanween_fath(word, tanween_fath_form):
    new_word = word
    # tanween before alefs form
    if tanween_fath_form == True:
        new_word,_ = TANWEEN_FATH_AFTER_ALEFS_REGEX.subn(TANWEEN_FATH + '\\g<alef>', word)
    # tanween after alefs form
    elif tanween_fath_form == False:
        new_word,_ = TANWEEN_FATH_BEFORE_ALEFS_REGEX.subn('\\g<alef>' + TANWEEN_FATH, word)
    return new_word

def has_tanween_error(word, tanween_fath_form):
    return (word != reorder_tanween_fath(word, tanween_fath_form))

BARE_MOON_LAM_REGEX = re.compile(r'^' + AR_DIAC + r'?' + ALEF + LAM + MOON_LETTER)
def has_bare_moon_lam(word):
    return BARE_MOON_LAM_REGEX.search(word) is not None

BARE_ALEF_REGEX = re.compile(r'(?!' + WAW + ALEF + r'$)' + AR_LETTER + SHADDA + r'?' + ALEF + r'(?!' + TANWEEN_FATH + r')')
def has_bare_alef_error(word):
    return BARE_ALEF_REGEX.search(word) is not None

def normalize_diac(word):
    # leave non arabic words
    for char in word:
        if (char not in AR_CHARSET and char != MADDA):
            return word

    stack = []

    # moves shaddas on alef-mad to the previous letter
    letter = None
    diacs = []
    for char in [*word, 'ض']: # 'ض' is terminator
        if (char in AR_LETTERS):
            if (letter is not None):
                stack.append(letter)
                stack.extend(diacs)

            letter = char
            diacs = []
        else:
            if (letter == ALEF and char == SHADDA):
                stack.append(char)
            else:
                diacs.append(char)

    stack = list(reversed(stack))
    # print('stack :', stack)
    norm = []

    letters = []
    for char in word:
        if (char in AR_LETTERS):
            letters.append(char)
    # print('letters:', letters)

    letter_ind = -1
    curr_letter = None
    curr_non_shadda_diac = None
    has_shadda = False

    while (len(stack) > 0):
        char = stack.pop()
        if (char in AR_LETTERS):
            # place previous letter with it's diacritics
            if (curr_letter is not None):
                norm.append(curr_letter)
                if (has_shadda):
                    norm.append(SHADDA)
                # don't put non-shadda-diacs before alef-mad
                if (curr_non_shadda_diac is not None and (letter_ind == len(letters) - 1 or letters[letter_ind + 1] != ALEF)):
                    norm.append(curr_non_shadda_diac)

            # reset for next letter
            letter_ind += 1
            curr_non_shadda_diac = None
            has_shadda = False
            curr_letter = char

            # print(letter_ind)
            # print(letters)
            # print(curr_letter)
            assert(letters[letter_ind] == curr_letter)

        # deal with tatweel, madda, shadda and dagger alefs
        if (char == TATWEEL or char == MADDA or char == DAGGER):
            continue
        if (char == SHADDA):
            has_shadda = True

        # ignore non-shadda-diacs before alef-mad which are not fatha or tanween fath
        if (char in NON_SHADDA_DIACS and char != FATHA and char != TANWEEN_FATH \
            and letter_ind < len(letters) - 1 and letters[letter_ind + 1] == ALEF):
            continue

        # ignore non-shadda-diacs on alef-mad which are not tanween fath
        if (char in NON_SHADDA_DIACS and char != TANWEEN_FATH and letter_ind >= 0 and letters[letter_ind] == ALEF):
            continue

        # ignore all sukuns
        if (char == SUKUN):
            continue

        # deal with single non-shadda-diacs
        if (char in SINGLE_NON_SHADDA_DIACS):

            if (curr_non_shadda_diac is None):
                curr_non_shadda_diac = char

            # turn two non-shadda-diacs to a tanween and place it back into the stack
            elif (char == curr_non_shadda_diac):
                curr_non_shadda_diac = None
                if (char == FATHA):
                    stack.append(TANWEEN_FATH)
                if (char == DAMMA):
                    stack.append(TANWEEN_DAM)
                if (char == KASRA):
                    stack.append(TANWEEN_KASR)

            # other single non-shadda-diacs are just ignored

        # deal with tanween
        if (char in TANWEENS):
            # add tanween
            if (curr_non_shadda_diac is None or curr_non_shadda_diac == singular_of_tanween(char)):
                curr_non_shadda_diac = char

                # if a tanween-fath is placed before the last alef
                if (char == TANWEEN_FATH \
                    and letter_ind == len(letters) - 2 \
                    and letters[-1] == ALEF):
                    stack.insert(0, curr_non_shadda_diac)
                    curr_non_shadda_diac = None

                # if a tanween-fath is on a last letter that is not from TANWEEN_FATH_LETTERS
                elif (char == TANWEEN_FATH \
                    and letter_ind == len(letters) - 1 \
                    and letters[-1] not in TANWEEN_FATH_LETTERS):
                    stack.insert(0, ALEF)
                    letters.append(ALEF)
                    stack.insert(0, TANWEEN_FATH)
                    curr_non_shadda_diac = None

                # if a tanween is in the middle of the word change it to a single non-shadda-diac
                elif (letter_ind < len(letters) - 1):
                    stack.append(singular_of_tanween(curr_non_shadda_diac))
                    curr_non_shadda_diac = None

    # place last letter
    if (curr_letter is not None):
        norm.append(curr_letter)
        if (has_shadda):
            norm.append(SHADDA)
        if (curr_non_shadda_diac is not None):
            norm.append(curr_non_shadda_diac)
                
    return ''.join(norm)

def compare_diac(orig_word, new_word):
    # normalize letters
    orig_word = normalize_letters(orig_word)
    new_word = normalize_letters(new_word)

    # separate letters and diacs
    orig_letters, orig_diac_groups = separate_letters_and_diacs(orig_word)
    new_letters, new_diac_groups = separate_letters_and_diacs(new_word)

    stats = {
        'removal_count' : 0,
        'shadda_removal_count' : 0,
        'non_shadda_diac_removal_count' : 0,
        'non_shadda_diac_change_count' : 0,
        'last_non_shadda_diac_removal_count' : 0,
        'last_non_shadda_diac_change_count' : 0,
    }

    # loop through diacs
    for i in range(min(len(orig_letters), len(new_letters))):
        # find shaddas
        orig_has_shadda = (SHADDA in orig_diac_groups[i])
        new_has_shadda = (SHADDA in new_diac_groups[i])

        # shadda removal
        if (orig_has_shadda and not new_has_shadda):
            stats['removal_count'] += 1
            stats['shadda_removal_count'] += 1


        # get orig and new non-shadda-diac
        orig_non_shadda_diac = None
        for diac in orig_diac_groups[i]:
            if (diac in NON_SHADDA_DIACS):
                orig_non_shadda_diac = diac
        new_non_shadda_diac = None
        for diac in new_diac_groups[i]:
            if (diac in NON_SHADDA_DIACS):
                new_non_shadda_diac = diac

        # if there is a change in non-shadda-diac
        if (orig_non_shadda_diac != new_non_shadda_diac):
            # if orig is None, then a non-shadda-diac was just added
            if (orig_non_shadda_diac is None):
                continue

            # if it became nunated
            if (orig_non_shadda_diac == singular_of_tanween(new_non_shadda_diac)):
                continue

            # then definitely a non-shadda-diac was removed
            stats['removal_count'] += 1
            stats['non_shadda_diac_removal_count'] += 1
            if (i == len(orig_letters) - 1):
                stats['last_non_shadda_diac_removal_count'] += 1

            # if the non-shadda-diac was changed
            if (new_non_shadda_diac is not None and
                new_non_shadda_diac != singular_of_tanween(orig_non_shadda_diac)):
                stats['non_shadda_diac_change_count'] += 1
                if (i == len(orig_letters) - 1):
                    stats['last_non_shadda_diac_change_count'] += 1

    return stats

def get_file_diac_stats(file_path, stats_files = {}):
    ### local variables ###
    # statistics object
    stats = {
        # diacs data
        'diac_count' : 0,
        'diac_freqs' : {
            FATHA : 0,
            DAMMA : 0,
            KASRA : 0,
            SUKUN : 0,
            TANWEEN_FATH : 0,
            TANWEEN_DAM : 0,
            TANWEEN_KASR : 0,
            SHADDA : 0,
            DAGGER : 0,
        },
        # diac words data
        'some_diac_word_count' : 0,
        'some_diac_line_count' : 0,
        'full_diac_word_count' : 0,
        # diac groups data
        'diac_group_count' : 0,
        'diac_group_at_index_count' : [0] * 11,
        'leading_diac_group_count' : 0,
        'first_diac_group_count' : 0,
        'middle_diac_group_count' : 0,
        'last_diac_group_count' : 0,
        'first_and_last_diac_group_count' : 0,
        # tanween fath specific data
        'tanween_fath_on_letter_before_last' : 0,
        'tanween_fath_on_last_letter' : 0,
        'tanween_fath_on_letter_before_ending_alef' : 0,
        'tanween_fath_on_ending_alef' : 0,
        # word diac checks
        # 'shadda_errors_count' : 0,
        # 'tanween_fath_errors_count' : 0,
        # 'context_errors_count' : 0,
        # shadda haraka order
        'shadda_then_diac_count': 0,
        'diac_then_shadda_count': 0,
        # averages
        'average_diac_per_letter' : 0,
        'average_diac_per_word' : 0,
        'average_diac_per_diac_word' : 0,
        'average_diac_per_line' : 0,
        'average_diac_group_per_letter' : 0,
        'average_diac_group_per_word' : 0,
        'average_diac_group_per_diac_word' : 0,
        'average_diac_group_per_line' : 0,
        # canonicality
        'canonical_diac_group_count' : 0,
        'canonical_diac_word_count' : 0,
        # diac groups
        'diac_group_freqs' : {},
    }

    ### helper inner functions ###
    # log word to file if file exists
    def conditional_word_log(word, file_key, index = -1):
        if (file_key in stats_files):
            # if logging in an array of files
            if index >= 0:
                stats_files[file_key][index].write(word + '\n')
            else:
                stats_files[file_key].write(word + '\n')

    # processes a single token
    def process_token(precontext, word, postcontext):
        # skip non arabic words
        if (not is_arabic_word(word)):
            return

        # process word diac data
        if (has_diac(word)):
            stats['some_diac_word_count'] += 1
            conditional_word_log(word, 'some_diac_words')
            
            # check for canonicality
            if (is_canonical_word_diac(word)):
                stats['canonical_diac_word_count'] += 1

            if (is_valid_full_diac(word, tanween_fath_form = True) and is_valid_contextual_diac(precontext, word, postcontext)):
                stats['full_diac_word_count'] += 1
                conditional_word_log(word, 'full_diac_words')
            # if has_shadda_error(word):
            #     stats['shadda_errors_count'] += 1
            # if has_tanween_error(word, tanween_fath_form = True):
            #     stats['tanween_fath_errors_count'] += 1
            # if is_valid_contextual_diac(precontext, word, postcontext):
            #     stats['context_errors_count'] += 1

        # adding leading diac
        letters, diac_groups = separate_letters_and_diacs(word)
        letters.insert(0, '')
        diac_groups.insert(0, get_leading_diac_group(word))

        is_word_canonical = True
        for i in range(len(letters)):
            # skip letters with no diacs
            if (diac_groups[i] == ''):
                continue

            # increment diac_group count
            stats['diac_group_count'] += 1

            # if diac group is before the first letter
            if (i == 0):
                stats['leading_diac_group_count'] += 1
                conditional_word_log(word, 'leading_diac_group_words')
            # if diac group on the first letter
            if (i == 1):
                stats['first_diac_group_count'] += 1
                conditional_word_log(word, 'first_diac_group_words')
            # if diac group on the last letter
            if (i == len(letters) - 1):
                stats['last_diac_group_count'] += 1
                conditional_word_log(word, 'last_diac_group_words')
            # if diac group on a middle letter
            if (i > 1 and i < len(letters) - 1):
                stats['middle_diac_group_count'] += 1
                conditional_word_log(word, 'middle_diac_group_words')
            # if diac group is simultaneously on first and last letter
            if (i == 1 and i == len(letters) - 1):
                stats['first_and_last_diac_group_count'] += 1
                conditional_word_log(word, 'first_and_last_diac_group_words')

            # count and log indexed diac groups
            ind = min(i, len(stats['diac_group_at_index_count']) - 1)
            stats['diac_group_at_index_count'][ind] += 1
            conditional_word_log(word, 'diac_group_at_index', ind)

            # canonicality data
            is_group_canonical = is_canonical_diac_group(diac_groups[i])
            if (is_group_canonical):
                stats['canonical_diac_group_count'] += 1
            else:
                is_word_canonical = False

            # increment this diac_group frequency
            if (diac_groups[i] not in stats['diac_group_freqs']):
                stats['diac_group_freqs'][diac_groups[i]] = [is_group_canonical, 1]
            else:
                stats['diac_group_freqs'][diac_groups[i]][1] += 1

            # update shadda diac order stats
            if (SHADDA in diac_groups[i] and len(diac_groups[i]) > 1):
                if (diac_groups[i][0] == SHADDA):
                    stats['shadda_then_diac_count'] += 1
                else:
                    stats['diac_then_shadda_count'] += 1

            # process diacs in diac_group
            for diac in diac_groups[i]:
                # increment diac count
                stats['diac_count'] += 1

                # increment this diac frequency
                if (diac not in stats['diac_freqs']):
                    assert(False)
                else:
                    stats['diac_freqs'][diac] += 1

                # count both of tanween fath positions
                if (diac == TANWEEN_FATH):
                    # before the alef
                    if (i == len(letters) - 2):
                        stats['tanween_fath_on_letter_before_last'] += 1
                        if (letters[-1] == ALEF or letters[-1] == ALEF_MAQSURA):
                            stats['tanween_fath_on_letter_before_ending_alef'] += 1
                    # on the alef
                    elif (i == len(letters) - 1):
                        stats['tanween_fath_on_last_letter'] += 1
                        if (letters[-1] == ALEF or letters[-1] == ALEF_MAQSURA):
                            stats['tanween_fath_on_ending_alef'] += 1

    # process an entire line
    def process_line(line):
        line = line.strip().split()

        prev_some_diac_word_count = stats['some_diac_word_count']
        for i in range(len(line)):
            precontext = ''
            if (i > 0):
                precontext = line[i - 1]
            postcontext = ''
            if (i < len(line) - 1):
                postcontext = line[i + 1]
            process_token(precontext, line[i], postcontext)
        new_some_diac_word_count = stats['some_diac_word_count']

        # if there is a diac in this line
        if (prev_some_diac_word_count != new_some_diac_word_count):
            stats['some_diac_line_count'] += 1

    ### function main body ###
    # get token stats
    token_stats = get_file_token_stats(file_path)

    # process data
    file_path = Path(file_path)
    with file_path.open('r', encoding='utf-8') as input_file:
        for line in input_file:
            process_line(line)

    # calculate post processing stats
    stats['average_diac_per_letter'] = stats['diac_count'] / token_stats['arabic_letter_count']
    stats['average_diac_per_word'] = stats['diac_count'] / token_stats['arabic_word_count']
    stats['average_diac_per_diac_word'] = stats['diac_count'] / stats['some_diac_word_count']
    stats['average_diac_per_line'] = stats['diac_count'] / token_stats['line_count']
    stats['average_diac_group_per_letter'] = stats['diac_group_count'] / token_stats['arabic_letter_count']
    stats['average_diac_group_per_word'] = stats['diac_group_count'] / token_stats['arabic_word_count']
    stats['average_diac_group_per_diac_word'] = stats['diac_group_count'] / stats['some_diac_word_count']
    stats['average_diac_group_per_line'] = stats['diac_group_count'] / token_stats['line_count']

    return stats

def compare_word_diac(orig_word, new_word):
    ### local variables ###
    stats = {
        'word_length_changed' : False,
        'diac_group_insertion_count' : 0,
        'diac_group_deletion_count' : 0,
        'diac_group_substitution_count' : 0,
        'diac_group_map' : {},
    }

    ### helper inner functions ###
    def log_diac_group_change(orig_diac_group, new_diac_group):
        key = (orig_diac_group, new_diac_group)

        # update diac group change frequency map
        if (key not in stats['diac_group_map']):
            stats['diac_group_map'][key] = 1
        else:
            stats['diac_group_map'][key] += 1
    
        # same diac group
        if (orig_diac_group == new_diac_group):
            pass
        # insertion
        elif (orig_diac_group == ''):
            stats['diac_group_insertion_count'] += 1
        # deletion
        elif (new_diac_group == ''):
            stats['diac_group_deletion_count'] += 1
        # substitution
        else:
            stats['diac_group_substitution_count'] += 1

    ### function main body ###
    # process leading diac groups
    orig_leading_diac_group = get_leading_diac_group(orig_word)
    new_leading_diac_group = get_leading_diac_group(new_word)
    log_diac_group_change(orig_leading_diac_group, new_leading_diac_group)

    orig_letters, orig_diac_groups = separate_letters_and_diacs(orig_word)
    new_letters, new_diac_groups = separate_letters_and_diacs(new_word)

    # if the length of the word changed
    if (len(orig_letters) != len(new_letters)):
        stats['word_length_changed'] = True

    # process other diac groups
    for i in range(min(len(orig_diac_groups), len(new_diac_groups))):
        orig_diac_group = orig_diac_groups[i]
        new_diac_group = new_diac_groups[i]
        log_diac_group_change(orig_diac_group, new_diac_group)

    return stats

def compare_file_diac(orig_file_path, new_file_path):
    ### local variables ###
    stats = {
        'arabic_word_count' : 0,

        'orig_file' : {
            'diac_group_count' : 0,
            'some_diac_word_count' : 0,
            'full_diac_word_count' : 0,
        },
        'new_file' : {
            'diac_group_count' : 0,
            'some_diac_word_count' : 0,
            'full_diac_word_count' : 0,
        },

        'word_length_change_count' : 0,

        'diac_group_insertion_count' : 0,
        'diac_group_deletion_count' : 0,
        'diac_group_substitution_count' : 0,
        'diac_group_map' : {},
    }
    agreement_rows = []
    disagreement_rows = []

    ### helper inner functions ###
    def process_line(orig_line, new_line):
        word_index = 0
        prev_scope = []
        after_scope = [orig_line[i] for i in range(1, min(WORD_SCOPE_RADIUS + 1, len(orig_line)))]
        for orig_tok, new_tok in zip(orig_line, new_line):
            # get comparison stats
            word_stats = compare_word_diac(orig_tok, new_tok)

            # update line stats
            for key in word_stats:
                # add dictionaries key by key
                if (isinstance(word_stats[key], dict)):
                    for subkey in word_stats[key]:
                        # if subkey doesn't exist
                        if (subkey not in stats[key]):
                            stats[key][subkey] = word_stats[key][subkey]
                        # if subkey exists
                        else:
                            stats[key][subkey] += word_stats[key][subkey]
                # count word length changes
                elif (key == 'word_length_changed'):
                    if (word_stats[key]):
                        stats['word_length_change_count'] += 1
                # everything else, just add
                else:
                    stats[key] += word_stats[key]

            # current row
            row = (
                " ".join(after_scope),
                orig_tok,
                " ".join(prev_scope),
                new_tok,
                word_stats['diac_group_insertion_count'],
                word_stats['diac_group_deletion_count'],
                word_stats['diac_group_substitution_count'],
                word_stats['word_length_changed']
            )

            # if compatible
            if (word_stats['diac_group_deletion_count'] == 0 and
                word_stats['diac_group_substitution_count'] == 0 and
                not word_stats['word_length_changed']):
                agreement_rows.append(row)
            # if not compatible
            else:
                disagreement_rows.append(row)

            # update prev_scope
            if (len(prev_scope) == WORD_SCOPE_RADIUS):
                prev_scope.pop(0)
            prev_scope.append(orig_tok)

            # update after_scope
            if (len(after_scope) > 0):
                after_scope.pop(0)
            if (word_index + WORD_SCOPE_RADIUS + 1 < len(orig_line)):
                after_scope.append(orig_line[word_index + WORD_SCOPE_RADIUS + 1])

            word_index += 1

    ### function main body ###
    # get file specific statistics
    orig_token_stats = get_file_token_stats(orig_file_path)
    orig_diac_stats = get_file_diac_stats(orig_file_path)
    orig_stats = {**orig_token_stats, **orig_diac_stats}
    new_token_stats = get_file_token_stats(new_file_path)
    new_diac_stats = get_file_diac_stats(new_file_path)
    new_stats = {**new_token_stats, **new_diac_stats}

    assert orig_stats['arabic_word_count'] == new_stats['arabic_word_count']

    stats['arabic_word_count'] = orig_stats['arabic_word_count']

    for key in stats['orig_file']:
        stats['orig_file'][key] = orig_stats[key]
    for key in stats['new_file']:
        stats['new_file'][key] = new_stats[key]

    # store original and new lines
    orig_lines = []
    new_lines = []

    with orig_file_path.open('r', encoding='utf-8') as input_file:
        for line in input_file:
            line = line.strip().split()
            if len(line) > 0:
                orig_lines.append(line)

    with new_file_path.open('r', encoding='utf-8') as input_file:
        for line in input_file:
            line = line.strip().split()
            if len(line) > 0:
                new_lines.append(line)

    assert len(orig_lines) == len(new_lines)

    # process lines
    for orig_line, new_line in zip(orig_lines, new_lines):
        assert len(orig_line) == len(new_line)
        process_line(orig_line, new_line)

    return stats, agreement_rows, disagreement_rows
