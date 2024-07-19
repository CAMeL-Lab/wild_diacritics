##### imports #####

# importing packages
import os
import sys
import csv
import re
from pathlib import Path

# importing handlers
exec(open("wild_diacritics_utils/modules/token_handler/token_handler.py").read())
exec(open("wild_diacritics_utils/modules/diac_handler/diac_handler.py").read())

##### main program #####

def main():
    global stats

    in_path = ''

    # ensure correct argument count
    if (len(sys.argv) < 2):
        print("Usage: python diac_checker.py input.txt")
        return

    # take script arguments
    in_path = sys.argv[1]

    # check diacritizations
    in_file = open(in_path, 'r')
    lines = [line.split() for line in in_file.read().splitlines()]
    words_list = [line[0].strip() for line in lines]
    is_usable_list = [line[1].strip() == 'Yes' for line in lines]
    
    verdicts = [is_valid_full_diac(word, tanween_fath_form=True) for word in words_list]

    # automatically make non arabic words not usable
    for i in range(len(verdicts)):
        if not is_arabic_word(words_list[i]):
            is_usable_list[i] = False

    for word, is_usable, verdict in zip(words_list, is_usable_list, verdicts):
        if not is_usable:
            print(word)
            continue

        word = re.sub(r'(' + r'|'.join(NON_SHADDA_DIACS) + r'|' + DAGGER + r')' + SHADDA, SHADDA + r'\1', word)
        word = re.sub(r'(' + ALEF + r'|' + ALEF_MAQSURA + r')' + TANWEEN_FATH, TANWEEN_FATH + r'\1', word)
        print(word)

if __name__ == '__main__':
    main()
