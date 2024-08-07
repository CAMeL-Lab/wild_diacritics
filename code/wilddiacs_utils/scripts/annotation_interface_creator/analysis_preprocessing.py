from wild_diacritics_utils.modules.token_handler.token_handler import is_arabic_word
from wild_diacritics_utils.modules.diac_handler.diac_handler import has_diac
import csv
from pathlib import Path

def analyze_sentences_with_diacritics(input_file):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        sentences = file.readlines()

    sentences_with_diacritics = []
    num_sentences = len(sentences)
    num_words_with_diacritics = 0
    num_total_words = 0
    words_with_diacritics_per_sentence = []

    # Process each sentence
    for sentence in sentences:
        words = sentence.split()
        has_diacritics = False
        words_with_diacritics = 0

        # Check if any word in the sentence has diacritics
        for word in words:
            if is_arabic_word(word) and has_diac(word):
                has_diacritics = True
                words_with_diacritics += 1

        if has_diacritics:
            sentences_with_diacritics.append(sentence)
            num_words_with_diacritics += words_with_diacritics

        num_total_words += len(words)
        words_with_diacritics_per_sentence.append(words_with_diacritics)

    return {
        'sentences_with_diacritics': sentences_with_diacritics,
        'num_sentences': num_sentences,
        'num_words_with_diacritics': num_words_with_diacritics,
        'num_total_words': num_total_words,
        'words_with_diacritics_per_sentence': words_with_diacritics_per_sentence
    }


def write_file(output_file, sentences_with_diacritics):
    # Write the sentences with diacritics to a new file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(sentences_with_diacritics)


def calculate_sentences_needed(desired_num_words_with_diacritics, analysis_result):
    words_with_diacritics_per_sentence = analysis_result['words_with_diacritics_per_sentence']

    sentences_needed = 0
    words_found = 0

    # Iterate over the words with diacritics per sentence list
    for words_in_sentence in words_with_diacritics_per_sentence:
        if words_found >= desired_num_words_with_diacritics:
            # If the desired number is already reached, break the loop
            break

        sentences_needed += 1
        words_found += words_in_sentence

    return sentences_needed

def process_text_files(input_files, output_file):
    with open(output_file, mode='w', newline='') as csv_file:
        fieldnames = ['File', 'Number of sentences', 'Number of words', 'Number of words with diacritics', 'Number of sentences with diacritics']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for file in input_files:
            analyses = analyze_sentences_with_diacritics(file)
            sentences_with_diacritics = analyses['sentences_with_diacritics']
            write_file(file.replace('.txt', '_sentences_with_diacritics.txt'), sentences_with_diacritics)
            writer.writerow({
                'File': file,
                'Number of sentences': analyses['num_sentences'],
                'Number of words': analyses['num_total_words'],
                'Number of words with diacritics': analyses['num_words_with_diacritics'],
                'Number of sentences with diacritics': len(analyses['sentences_with_diacritics'])
            })

            desired_words = 1000
            sentences_needed = calculate_sentences_needed(desired_words, analyses)
            print(f"Number of sentences needed for {file}: {sentences_needed}")

# Example usage
# input_files = ['corpora/Hindawi/hindawi_adlt/hindawi_adlt_randomized_sentences.txt']
# for input_file in input_files:
#     output_file = Path(input_file).parent / (Path(input_file).stem + '_stats.csv')
# 
# process_text_files(input_files, output_file)
# print("Analysis results saved to '"+ Path(input_file).stem + "_stats.csv'")
