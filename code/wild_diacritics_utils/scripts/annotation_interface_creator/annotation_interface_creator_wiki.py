from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.disambig.bert import BERTUnfactoredDisambiguator
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.normalize import normalize_unicode
from wild_diacritics_utils.modules.token_handler.token_handler import is_arabic_word
from wild_diacritics_utils.modules.diac_handler.diac_handler import has_diac
from pathlib import Path
from analysis_preprocessing import analyze_sentences_with_diacritics, calculate_sentences_needed
import time
from tqdm import tqdm
import pandas as pd
import sys

#USAGE: python annotation_interface_creator.py corpus.txt corpus_meta.txt

#------****Corpus****------

# Read the corpus
corpus_path = Path(sys.argv[1]) 
interface_name = '_'.join(corpus_path.parts[-1].split("_")[0:2])
# Create the output file name
annotation_interface_file_name = f"{interface_name}_annotation_interface.tsv"
desired_words_with_diacritics = 99999 # 1500  # Replace with your desired number of words with diacritics
analyses = analyze_sentences_with_diacritics(corpus_path)
target_num_sentences = calculate_sentences_needed(desired_words_with_diacritics, analyses)
print(f"Target number of sentences: {target_num_sentences}")

corpus = []
with corpus_path.open('r', encoding='utf-8') as corpus_file:
    corpus = corpus_file.readlines()[:target_num_sentences]

    # normalize and tokenize
    # corpus = [' '.join(simple_word_tokenize(normalize_unicode(sent), split_digits = True)) for sent in corpus]
    # tokenize only
    corpus = [' '.join(simple_word_tokenize(sent, split_digits = True)) for sent in corpus]

#------****Functions****------

def write_camel_choices_to_excel(array):
    # Initialize the DataFrame with the required columns
    df = pd.DataFrame(columns=['Top1', 'Top2', 'Top3'])
    for i, row in enumerate(array):
        if len(row) < 3:
            # Fill in empty cells with empty strings
            row += [''] * (3 - len(row))
        if len(row) >= 3:
            # Append to DataFrame
            df = df._append({
                'Top1': row[0],  # Top1
                'Top2': row[1],  # Top2
                'Top3': row[2]   # Top3
            }, ignore_index=True)
        else:
            assert(0)

    return df

def write_word_and_meta_to_excel(sentences, meta_file):
    # Initialize the DataFrames with the required columns
    word_df = pd.DataFrame(columns=['Index', 'Sentence Number', 'Context After', 'Word', 'Context Before'])
    meta_df = pd.DataFrame(columns=['File Name', 'Original Sentence Number'])
    with open(meta_file, 'r') as m_file:
        meta_data = m_file.readlines()
    for i, (sentence, meta_line) in enumerate(zip(sentences, meta_data)):
        sentence = sentence.strip()
        file_name, sentence_number = meta_line.strip().split('\t')
        if sentence:
            words = sentence.split()
            for j, word in enumerate(words):
                # Filter the word to keep only Arabic characters
                if is_arabic_word(word):
                    if has_diac(word):
                        # Get index and sentence number
                        index = j + 1
                        # Get context after the word
                        context_after_words = words[j + 1:]
                        context_after = ' '.join(context_after_words)
                        # Get context before the word in reverse order
                        context_before_words = words[:j]
                        context_before = ' '.join(context_before_words)
                        # Append to DataFrame
                        word_df = word_df._append({
                            'Index': index,
                            'Sentence Number': i + 1,
                            'Context After': context_after,
                            'Word': word,
                            'Context Before': context_before
                        }, ignore_index=True)
                        # Append to DataFrame
                        meta_df = meta_df._append({'File Name': file_name, 'Original Sentence Number': int(sentence_number)}, ignore_index=True)
    
    return meta_df, word_df 

def is_diacritic(char):
    diacritic_chars = ['َ', 'ً', 'ُ', 'ٌ', 'ِ', 'ٍ', 'ْ']
    return char in diacritic_chars

def add_fatha_before_alif(word):
    diacritic = 'َ'
    modified_word = ''

    for i, char in enumerate(word):
        if char == 'ا' and i > 0 and not is_diacritic(word[i-1]):
            modified_word += diacritic + char
        else:
            modified_word += char

    return modified_word

def add_kasra_after_hamza(word):
    diacritic = 'ِ'
    modified_word = ''

    for i, char in enumerate(word):
        if char == 'إ' and i < len(word) - 1 and not is_diacritic(word[i + 1]):
            modified_word += char + diacritic
        else:
            modified_word += char
    return modified_word

# ------****Disambiguation****------

def disambiguation(corpus):
    S31_DB_PATH = 'calima-msa-s31.db'
    DISAMBIG = BERTUnfactoredDisambiguator.pretrained('msa', top=3, pretrained_cache=False)
    S31_DB = MorphologyDB(S31_DB_PATH, 'a')
    S31_AN = Analyzer(S31_DB, 'ADD_PROP')
    DISAMBIG._analyzer = S31_AN
    top_3_choices_list = []

    start_time = time.time()
    # Use tqdm to display a live progress bar and timer
    for sentence in tqdm(corpus, desc="Processing", unit=" sentence"):
        if (not has_diac(sentence)):
            continue

        disambig = DISAMBIG.disambiguate(sentence.split())
        filtered_words = [word for word in disambig if (is_arabic_word(word.word) and has_diac(word.word))]
        top_3_choices = [[(analysis.diac) for analysis in word.analyses] for word in filtered_words]
        top_3_choices_list.extend(top_3_choices)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Disambiguation Elapsed Time: {minutes} minutes {seconds} seconds")
    return top_3_choices_list

#------****Main Execution****------

meta_file = Path(sys.argv[2]) 
df1, df2 = write_word_and_meta_to_excel(corpus, meta_file)
top_3_choices_list = disambiguation(corpus)
df3 = write_camel_choices_to_excel(top_3_choices_list)
# Combine the columns into one DataFrame
df1.info(); df2.info(); df3.info()
df4 = pd.DataFrame(columns=['Salman', 'Tameem', 'Final Choice', 'Usable', 'Final Choice Source', 'Final Choice Debug', 'Comment'])
df = pd.concat([df1, df2, df3, df4], axis=1)
df.to_csv(annotation_interface_file_name, sep='\t', index=False)
