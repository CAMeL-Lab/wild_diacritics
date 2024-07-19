# USAGE: python unique_analyses.py in.txt

##### imports #####

# importing packages
import os
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

DISAMBIG = None

##### helper functions #####

def analyze_arabic_words(sentences):
    analyses = {}

    start_time = time.time()
    # Use tqdm to display a live progress bar and timer
    for sentence in tqdm(sentences, desc="Processing", unit=" sentence"):
        for word in sentence:
            if not is_arabic_word(word):
                continue

            curr_analyses = DISAMBIG._analyzer.analyze(word)
            for analysis in curr_analyses:
                analyses[analysis['diac']] = None

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    sys.stderr.write(f"Disambiguation Elapsed Time: {minutes} minutes {seconds} seconds\n")
    return analyses

def input_sentences(in_path):
    in_file = open(in_path, 'r')
    sentences = [sent for sent in in_file.read().splitlines()]
    sentences = [simple_word_tokenize(normalize_unicode(sent), split_digits = True) for sent in sentences]
    in_file.close()
    return sentences

def output_csv(file_path, rows):
    with open(file_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')
        csv_writer.writerows(rows)

##### main program #####

def main():
    # ensure correct argument count
    if (len(sys.argv) < 4):
        print("Usage: python diac_check_unique_analyses.py data_base.db input.txt out.tsv")
        return

    db_path = sys.argv[1]
    in_path = sys.argv[2]
    out_path = sys.argv[3]

    # change database of disambiguator/analyzer
    global DISAMBIG
    DISAMBIG = BERTUnfactoredDisambiguator.pretrained('msa', top=99, pretrained_cache=False)
    S31_DB_PATH = db_path
    S31_DB = MorphologyDB(S31_DB_PATH, 'a')
    S31_AN = Analyzer(S31_DB, 'NONE')
    DISAMBIG._analyzer = S31_AN

    # output analyses
    sentences = input_sentences(in_path)
    analyses_list = analyze_arabic_words(sentences)
    unique_arabic_analyses_count = len(analyses_list)

    # get diac verdicts
    correct_count = 0
    shadda_error_count = 0
    tanween_error_count = 0
    mistake_count = 0
    verdicts = []
    for analysis in analyses_list:
        if is_valid_full_diac(analysis, has_pre_context = False, has_post_context = False, tanween_fath_form = True):
            verdicts.append("CORRECT")
            correct_count += 1
            continue

        fixed_shaddas_analysis = fix_shadda_order(analysis)
        if is_valid_full_diac(fixed_shaddas_analysis, has_pre_context = False, has_post_context = False, tanween_fath_form = True):
            verdicts.append("SHADDA_ERROR")
            shadda_error_count += 1
            continue

        reordered_tanween_analysis = reorder_tanween_fath(analysis, True)
        if is_valid_full_diac(reordered_tanween_analysis, has_pre_context = False, has_post_context = False, tanween_fath_form = True):
            verdicts.append("TANWEEN_ERROR")
            tanween_error_count += 1
            continue

        verdicts.append("MISTAKE")
        mistake_count += 1

    assert(len(verdicts) == len(analyses_list))
    assert(unique_arabic_analyses_count == correct_count + shadda_error_count + tanween_error_count + mistake_count)

    analyses_verdict_list = [[a, v] for a, v in zip(analyses_list, verdicts)]
    output_csv(out_path, analyses_verdict_list)

    sys.stderr.write(f"Number of unique arabic analyses: {unique_arabic_analyses_count}\n")
    sys.stderr.write(f"Number of CORRECT: {correct_count} - {correct_count / unique_arabic_analyses_count} fraction\n")
    sys.stderr.write(f"Number of MISTAKE: {mistake_count} - {mistake_count / unique_arabic_analyses_count} fraction\n")
    sys.stderr.write(f"Number of SHADDA_ERROR: {shadda_error_count} - {shadda_error_count / unique_arabic_analyses_count} fraction\n")
    sys.stderr.write(f"Number of TANWEEN_ERROR: {tanween_error_count} - {tanween_error_count / unique_arabic_analyses_count} fraction\n")

if __name__ == '__main__':
    main()
