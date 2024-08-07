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
    in_path = ''

    # ensure correct argument count
    if (len(sys.argv) < 2):
        print("Usage: python diac_checker.py input.txt")
        return

    # take script arguments
    in_path = sys.argv[1]

    # check diacritizations
    in_file = open(in_path, 'r')
    lines = [line.split('\t') for line in in_file.read().splitlines()]
    precontexts_list = None; words_list = None; postcontexts_list = None
    if (len(lines) > 0 and len(lines[0]) == 1):
        # rejoin tab separations
        lines = [' '.join(line) for line in lines]
        # split on spaces
        lines = [line.split() for line in lines]

        precontexts_list = []
        words_list = []
        postcontexts_list = []
        is_usable_list = []
        for line in lines:
            for i in range(len(line)):
                precontext = ''
                if (i > 0):
                    precontext = line[i - 1]
                precontexts_list.append(precontext)

                words_list.append(line[i])

                postcontext = ''
                if (i != len(line) - 1):
                    postcontext = line[i + 1]
                postcontexts_list.append(postcontext)

                is_usable_list.append(True)
        assert(len(words_list) == len(precontexts_list))
        assert(len(words_list) == len(postcontexts_list))
        assert(len(words_list) == len(is_usable_list))
    elif (len(lines) > 0 and len(lines[0]) == 10):
        precontexts_list = [line[2].strip() for line in lines]
        words_list = [line[8].strip() for line in lines]
        postcontexts_list = [line[0].strip() for line in lines]
        is_usable_list = [line[9].strip() == 'Yes' for line in lines]
    elif (len(lines) > 0 and len(lines[0]) == 2):
        precontexts_list = ['' for i in range(len(lines))]
        words_list = [line[0].strip() for line in lines]
        postcontexts_list = ['' for i in range(len(lines))]
        is_usable_list = [line[1].strip() == 'Yes' for line in lines]
    else:
        print("ERROR in format!!!")

    
    non_contextual_verdicts = are_valid_full_diacs(words_list, tanween_fath_form = True)

    # automatically make non arabic words not usable
    for i in range(len(non_contextual_verdicts)):
        if not is_arabic_word(words_list[i]):
            is_usable_list[i] = False

    usable_word_count = 0
    correct_count = 0
    shadda_error_count = 0
    tanween_error_count = 0
    context_error_count = 0
    moon_lam_error_count = 0
    bare_alef_error_count = 0
    unknown_error_count = 0
    for precontext, word, postcontext, is_usable, non_contextual_verdict in zip(precontexts_list, words_list, postcontexts_list, is_usable_list, non_contextual_verdicts):
        if not is_usable:
            print("")
            continue

        usable_word_count += 1
        contextual_verdict = is_valid_contextual_diac(precontext, word, postcontext)
        unknown_error_type = False

        if non_contextual_verdict and contextual_verdict:
            correct_count += 1
            print(f"TRUE") # : {precontext}\t{word}\t{postcontext}")
        else:
            print(f"FALSE") # : {precontext}\t{word}\t{postcontext}")
            unknown_error_type = True

        if has_shadda_error(word):
            assert(not non_contextual_verdict)
            shadda_error_count += 1
            # print(f"SHADDA_ERROR : {precontext}\t{word}\t{postcontext}")
            unknown_error_type = False
        if has_tanween_error(word, tanween_fath_form = True):
            assert(not non_contextual_verdict)
            tanween_error_count += 1
            # print(f"TANWEEN_ERROR : {precontext}\t{word}\t{postcontext}")
            unknown_error_type = False
        if has_bare_moon_lam(word):
            assert(not non_contextual_verdict)
            moon_lam_error_count += 1
            # print(f"MOON_LAM_ERROR : {precontext}\t{word}\t{postcontext}")
            unknown_error_type = False
        if has_bare_alef_error(word):
            assert(not non_contextual_verdict)
            bare_alef_error_count += 1
            # print(f"BARE_ALEF_ERROR : {precontext}\t{word}\t{postcontext}")
            unknown_error_type = False
        if not is_valid_contextual_diac(precontext, word, postcontext):
            context_error_count += 1
            # print(f"CONTEXT_ERROR : {precontext}\t{word}\t{postcontext}")
            unknown_error_type = False

        if unknown_error_type:
            unknown_error_count += 1
            # print(f"UNKOWN_ERROR : {precontext}\t{word}\t{postcontext}")

    mistake_count = usable_word_count - correct_count

    sys.stderr.write(f"Number of usable (arabic) words: {usable_word_count}\n")
    sys.stderr.write(f"Number of CORRECT: {correct_count} - {correct_count / usable_word_count} fraction\n")
    sys.stderr.write(f"Number of MISTAKE: {mistake_count} - {mistake_count / usable_word_count} fraction\n")
    sys.stderr.write(f"Number of SHADDA_ERROR: {shadda_error_count} - {shadda_error_count / usable_word_count} fraction\n")
    sys.stderr.write(f"Number of TANWEEN_ERROR: {tanween_error_count} - {tanween_error_count / usable_word_count} fraction\n")
    sys.stderr.write(f"Number of MOON_LAM_ERROR: {moon_lam_error_count} - {moon_lam_error_count / usable_word_count} fraction\n")
    sys.stderr.write(f"Number of BARE_ALEF_ERROR: {bare_alef_error_count} - {bare_alef_error_count / usable_word_count} fraction\n")
    sys.stderr.write(f"Number of CONTEXT_ERROR: {context_error_count} - {context_error_count / usable_word_count} fraction\n")
    sys.stderr.write(f"Number of UNKOWN_ERROR: {unknown_error_count} - {unknown_error_count / usable_word_count} fraction\n")

if __name__ == '__main__':
    main()
