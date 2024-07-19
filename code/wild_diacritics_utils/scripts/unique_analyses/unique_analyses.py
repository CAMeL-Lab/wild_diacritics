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

def analyze(sentences):
    analyses = {}

    start_time = time.time()
    # Use tqdm to display a live progress bar and timer
    for sentence in tqdm(sentences, desc="Processing", unit=" sentence"):
        for word in sentence:
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

def output_analyses_list(analyses_list):
    csv_writer = csv.writer(sys.stdout, delimiter=' ')
    for analysis in analyses_list.keys():
        csv_writer.writerow([analysis, 'Yes'])

##### main program #####

def main():
    # ensure correct argument count
    if (len(sys.argv) < 3):
        print("Usage: python unique_analyses.py data_base.db input.txt")
        return

    db_path = sys.argv[1]
    in_path = sys.argv[2]

    # change database of disambiguator/analyzer
    global DISAMBIG
    DISAMBIG = BERTUnfactoredDisambiguator.pretrained('msa', top=99, pretrained_cache=False)
    S31_DB_PATH = db_path
    S31_DB = MorphologyDB(S31_DB_PATH, 'a')
    S31_AN = Analyzer(S31_DB, 'NONE')
    DISAMBIG._analyzer = S31_AN

    # output analyses
    sentences = input_sentences(in_path)
    analyses_list = analyze(sentences)
    output_analyses_list(analyses_list)

if __name__ == '__main__':
    main()
