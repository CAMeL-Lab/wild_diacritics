##### imports #####

import os
import sys
import csv
import re
from pathlib import Path

from camel_tools.utils.charsets import AR_CHARSET
from camel_tools.utils.charsets import AR_DIAC_CHARSET
from camel_tools.utils.charsets import AR_LETTERS_CHARSET
from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET
from camel_tools.utils.charsets import UNICODE_SYMBOL_CHARSET

# importing handlers
exec(open("wild_diacritics_utils/modules/token_handler/token_handler.py").read())
exec(open("wild_diacritics_utils/modules/diac_handler/diac_handler.py").read())

##### global variables #####

stats = {
    'line_count': {},
    'average_token_count_per_line': {},
    'token_count': {},
    'arabic_word_count': {},
    'average_arabic_word_length': {},
    'average_diac_group_per_word': {},
}
file_stats = {}

##### helper functions #####

# outputs and writes to tsv file all the statistics
def output_stats(out_fp):
    global stats

    tsv_writer = csv.writer(out_fp, dialect='excel-tab')

    # format values with commas
    def format_value(value):
        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return "{:,}".format(value)
        elif isinstance(value, list):
            return [format_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: format_value(v) for k, v in value.items()}
        return value

    # helper print and write function
    def log_row(row):
        # Format values before writing
        # row = [format_value(item) for item in row]
        tsv_writer.writerow(row)
        print(*row)

    # output all the final data in out_fp
    for key in stats.keys():
        log_row([])
        log_row([key])

        for file_path in stats[key].keys():
            log_row([file_path, stats[key][file_path]])

##### main program #####

def main():
    global stats
    global stats_files

    in_path = ''
    out_dir_path = ''
    out_stats_file_name = 'diac_stats.tsv'

    # ensure correct argument count
    if (len(sys.argv) < 2):
        print("Usage: python compare_diac_stats.py file1 [file2 ...]")
        return

    # take script arguments
    file_paths = sys.argv[1:]

    # get all file_stats
    for path in file_paths:
        file_token_stats = get_file_token_stats(path, {})
        file_diac_stats = get_file_diac_stats(path, {})
        file_stats[path] = {**file_token_stats, **file_diac_stats}        

        # pick out all the data we are interested in
        for stat in stats.keys():
            stats[stat][path] = file_stats[path][stat]

    # output stats
    out_path = Path('diac_stats_comparison.tsv')
    with out_path.open('w', encoding='utf-8') as out_fp:
        output_stats(out_fp)

if __name__ == '__main__':
    main()
