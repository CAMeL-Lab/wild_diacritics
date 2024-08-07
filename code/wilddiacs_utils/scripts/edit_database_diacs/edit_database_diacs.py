# USAGE: python analyze.py in.txt

##### imports #####

# importing packages
import os
import re
import csv
import sys
import time
from tqdm import tqdm
from pathlib import Path

# personal packages
from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.disambig.bert import BERTUnfactoredDisambiguator
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.normalize import normalize_unicode

# importing handlers
exec(open("wild_diacritics_utils/modules/token_handler/token_handler.py").read())
exec(open("wild_diacritics_utils/modules/diac_handler/diac_handler.py").read())

##### globals #####

diac_separation_regex = re.compile(r'^(.*diac:)(\S*)(.*)$')
NON_MAD_GROUP = r'(' + NON_MAD_LETTER + SHADDA + r'?(?<!' + KASRA + YAA + r')' + r'(?<!' + DAMMA + WAW + r'))'

edits_metas = [
    { # alef lam to alef wasla fatha lam
        'detection_regex': re.compile(r'.*diac:\S*' + ALEF + LAM + r'#\s*.*' + ALEF + LAM + r'/DET'),
        'replacement_regex': re.compile(ALEF + r'(' + LAM + r'#)'),
        'replacement': ALEF_WASLA + FATHA + r'\1',
    }, { # standalone alef lam to alef wasla fatha lam
        'detection_regex': re.compile(r'((?!Pref).)*diac:' + ALEF + LAM + r'\s.*'),
        'replacement_regex': re.compile(ALEF + LAM),
        'replacement': ALEF_WASLA + FATHA + LAM,
    },

    { # alef Al~a*y to alef wasla fatha, with shadda
        'detection_regex': re.compile(r'.*lex:' + ALEF + LAM + SHADDA + FATHA + u'\u0630' + KASRA + YAA + r'_1.*'),
        'replacement_regex': re.compile(ALEF + LAM + SHADDA),
        'replacement': ALEF_WASLA + FATHA + r'#' + LAM,
    }, { # alef Al~a*y to alef wasla fatha, with no shadda
        'detection_regex': re.compile(r'.*lex:' + ALEF + LAM + SHADDA + FATHA + u'\u0630' + KASRA + YAA + r'_1.*'),
        'replacement_regex': re.compile(ALEF + LAM + NON_MAD_LETTER + SHADDA),
        'replacement': ALEF_WASLA + FATHA + LAM + r'#' + LAM,
    }, { # lil in Al~a*y to alef wasla fatha with shadda
        'detection_regex': re.compile(r'.*lex:' + ALEF + LAM + SHADDA + FATHA + u'\u0630' + KASRA + YAA + r'_1.*'),
        'replacement_regex': re.compile(LAM + KASRA + LAM + SHADDA),
        'replacement': LAM + KASRA + r'#' + LAM,
    },

    { # starting alef to alef wasla fatha, except in suffixes
        'detection_regex': re.compile(r'((?!Suff).)*diac:' + ALEF),
        'replacement_regex': re.compile(r'^' + ALEF),
        'replacement': ALEF_WASLA,
    },

    { # alef fariqa, add sukun after alef
        'detection_regex': re.compile(r'.*diac:\S*' + WAW + SINGLE_NON_SHADDA_DIAC + r'?' + ALEF + r'.*SUFF_SUBJ:(3|2)MP'),
        'replacement_regex': re.compile(r'^(\S*' + WAW + SINGLE_NON_SHADDA_DIAC + r'?' + ALEF + r')$'),
        'replacement': r'\1' + SUKUN,
    },

    ### FATHAS BEFORE ALEFS

    { # fatha before other alefs and alef maqsura that are not followed by tanween and not alef fariqa
        'detection_regex': re.compile(r'.*diac:\S*' + AR_LETTER + SHADDA + r'?(' + ALEF + r'(?!' + SUKUN + r')|' + ALEF_MAQSURA + r')(?!' + TANWEEN_FATH + r')'),
        'replacement_regex': re.compile(r'(?P<ar>' + AR_LETTER + SHADDA + r'?)(?P<alef>' + ALEF + r'(?!' + SUKUN + r')|' + ALEF_MAQSURA + r')(?!' + TANWEEN_FATH + r')'),
        'replacement': '\\g<ar>' + FATHA + '\\g<alef>',
    },

    { # fatha before suffixes that start with alef, and no tanween fath afterwards
        'detection_regex': re.compile(r'.*Suff.*diac:' + SHADDA + r'?' + ALEF + r'(?!' + TANWEEN_FATH + r')'),
        'replacement_regex': re.compile(r'^(' + SHADDA + r'?)(' + ALEF + r')'),
        'replacement': r'\1' + FATHA + r'\2',
    },

    { # dagger alef should take a fatha before it
        'detection_regex': re.compile(r'.*diac:\S*' + DAGGER),
        'replacement_regex': re.compile(r'(?!' + FATHA + r')(' + DAGGER + r')'),
        'replacement': FATHA + DAGGER,
    },

    ### SUKUNS

    { # ta altaneeth should have sukun
        'detection_regex': re.compile(r'.*diac:' + FATHA + TAA + r'\s.*PVSUFF_SUBJ:3FS'),
        'replacement_regex': re.compile(r'^(' + FATHA + TAA + r')$'),
        'replacement': r'\1' + SUKUN,
    },

    { # add sukun on non-mad group with no diacritic, can't be alef lam /DET, can't have any alef afterwards, and that is not at the end
        'detection_regex': re.compile(r'.*diac:\S*' + NON_MAD_GROUP + r'(?!' + AR_DIAC + r'|#)' + r'(?=\S)(?!' + ALEF + r'|' + ALEF_MAQSURA + r')'),
        'replacement_regex': re.compile(r'(?P<letter_group>' + NON_MAD_GROUP + r')' + r'(?!' + AR_DIAC + r'|#)' + r'(?=\S)'),
        'replacement': '\\g<letter_group>' + SUKUN,
    },

    ### Contextual elteqa2 Sakenayn Exceptions

    { # add percentage after min
        'detection_regex': re.compile(r'.*FW-Wa(?!-n).*diac:' + u'\u0645' + KASRA + u'\u0646' + r'\s.*'),
        'replacement_regex': re.compile(r'^(?P<min>.*)$'),
        'replacement': '\\g<min>%n',
    },

    { # add percentage after 2MP and 3MP dama2er that end with meem
        'detection_regex': re.compile(r'.*diac:\S*' + u'\u0645' + r'\s.*(2|3)MP.*'),
        'replacement_regex': re.compile(r'^(?P<group>.*)$'),
        'replacement': '\\g<group>%m',
    },

    { # add percentage after *a`likum, tilokum and >uwlaA}ikum
        'detection_regex': re.compile(r'.*diac:\S*' + u'\u0643' + DAMMA + u'\u0645' + r'\s.*DEM_PRON.*'),
        'replacement_regex': re.compile(r'^(?P<group>.*)$'),
        'replacement': '\\g<group>%m',
    },
]

##### main program #####

def main():
    # ensure correct argument count
    if (len(sys.argv) < 3):
        print("Usage: python edit_database_diacs.py old_database.db new_database.db")
        return

    # take parameters
    in_file_path = sys.argv[1]
    out_file_path = sys.argv[2]

    # open input database file
    in_file = open(in_file_path, 'r')

    # read database
    in_db_lines = in_file.readlines()
    sys.stderr.write('[*] Database Lines Read\n')

    # open new database file for writing
    out_file = open(out_file_path, 'w')

    # loop through lines
    for line in in_db_lines:
        new_line = line
        for i, edit_meta in enumerate(edits_metas):
            # skip edits that do not match detection regex
            if edit_meta['detection_regex'].match(new_line) is None:
                continue

            # print(new_line)
            match = diac_separation_regex.match(new_line)
            pre_line = match[1]
            diac = match[2]
            post_line = match[3]
            
            new_diac, count = edit_meta['replacement_regex'].subn(edit_meta['replacement'], diac)
            # print(f'count: {count}')
            # print(f'diac: {diac}, new_diac: {new_diac}')
            new_line = pre_line + new_diac + post_line + '\n'
            # print(new_line)

            # if (i == 13):
            #     print(new_line)
        
        # output new_line
        out_file.write(new_line)
    sys.stderr.write('[*] New Database Written\n')

    # close files
    in_file.close()
    out_file.close()

if __name__ == '__main__':
    main()
