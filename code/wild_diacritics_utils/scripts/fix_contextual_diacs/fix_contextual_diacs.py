##### imports #####

import sys
import re
from pathlib import Path

from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET

##### globals #####

STARTING_WASLA_RE = re.compile(u'^\u0671')
MIDDLE_WASLA_WITH_DIAC_RE = re.compile(u'^\u0671[\u064e\u064f\u0650\u0652]?')
ENDING_SUKUN_RE = re.compile(u'\u0652$')

CONTEXTUAL_DIACS_FLAG_RE = re.compile('%.+')
MEEM_FLAG_RE = re.compile('%m')
MIN_FLAG_RE = re.compile('%n')

##### helper functions #####

def is_punct(token):
    for char in token:
        if (char not in UNICODE_PUNCT_CHARSET):
            return False
    return True

def remove_contextual_diac_flags(word):
    return CONTEXTUAL_DIACS_FLAG_RE.sub('', word)

def fix_contextual_diacs(diacs):
    n = len(diacs)
    for i in range(n):
        ### pre-context fixes
        is_context_beginning = True
        if i != 0 and not is_punct(diacs[i - 1]):
            is_context_beginning = False

        if not is_context_beginning:
            diacs[i] = MIDDLE_WASLA_WITH_DIAC_RE.sub(u'\u0671', diacs[i])

        ### post-context fixes
        is_followed_by_wasla = False
        if i != (n - 1) and diacs[i + 1][0] == u'\u0671':
            is_followed_by_wasla = True

        replacement = u'\u0650' # KASRA
        if MEEM_FLAG_RE.search(diacs[i]) is not None:
            diacs[i] = MEEM_FLAG_RE.sub('', diacs[i])
            replacement = u'\u064f' # DAMMA
        elif MIN_FLAG_RE.search(diacs[i]) is not None:
            diacs[i] = MIN_FLAG_RE.sub('', diacs[i])
            if len(diacs) - 1 >= i + 1:
                replacement = diacs[i + 1][1] # take wasla diac

        if is_followed_by_wasla:
            if diacs[i][-1] == u'\u0652':
                diacs[i] = ENDING_SUKUN_RE.sub(replacement, diacs[i])

        ### general fixes
        diacs[i] = STARTING_WASLA_RE.sub(u'\u0627', diacs[i])

    return diacs

##### main program #####

def main():
    # ensure valid number of arguments
    if (len(sys.argv) < 2):
        print("USAGE: python fix_contextual_diacs.py in.txt out.txt")
        return

    # take script arguments
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    # take input
    with input_path.open('r', encoding='utf-8') as in_fp, \
         output_path.open('w', encoding='utf-8') as out_fp:

        for sent in in_fp:
            # tokenize sent
            words = sent.split()

            # testing flag removal
            # for word in words:
            #     print(f'{word} -> {remove_contextual_diac_flags(word)}')

            # fix context aware diacritics
            out_sent = ' '.join(fix_contextual_diacs(words))

            # write the data back to a txt file
            out_fp.write(out_sent + '\n')

if __name__ == '__main__':
    main()
