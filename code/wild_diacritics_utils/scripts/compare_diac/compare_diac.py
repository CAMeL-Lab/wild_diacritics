##### imports #####

import os
import sys
import csv
import re
from pathlib import Path
from pprint import pprint

from Levenshtein import editops
from camel_tools.utils.charmap import CharMapper
from camel_tools.utils.dediac import dediac_ar
from camel_tools.utils.charsets import AR_DIAC_CHARSET

# importing diac_handler
exec(open("wild_diacritics_utils/modules/token_handler/token_handler.py").read())
exec(open("wild_diacritics_utils/modules/diac_handler/diac_handler.py").read())

##### global variables #####

stats = {}

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
        if (key == 'orig_file' or key == 'new_file' or key == 'diac_group_map'):
            log_row([])
            log_row([key])

            if (key == 'diac_group_map'):
                log_row(['orig_diac_group', 'new_diac_group', 'freq'])
                d = sorted([(v, k) for k, v in stats[key].items()], reverse = True)
                # d = [(v, k) for k, v in sorted(stats[key].items())]
                for v, k in d:
                    log_row([TATWEEL + k[0], TATWEEL + k[1], v])
            else:
                for k, v in stats[key].items():
                    log_row([k, v])

            if (key == 'new_file'):
                log_row([])
        else:
            log_row([key, stats[key]])

##### main program #####

def main():
    global stats

    orig_file_path = ''
    new_file_path = ''
    out_file_path = ''

    # ensure correct argument count
    if (len(sys.argv) < 3):
        print("Usage: python compare_diac.py orig.txt diac.txt [out.tsv]")
        return

    # take script arguments
    orig_file_path = Path(sys.argv[1])
    new_file_path = Path(sys.argv[2])
    if (len(sys.argv) >= 4):
        out_file_path = Path(sys.argv[3])
    else:
        # remove the tokenized or diacritized at the end of the name
        file_name = os.path.splitext(orig_file_path)[0]
        file_name = re.sub(r'((_tokenized)|(_diacritized))$', '', file_name)
        out_file_path = file_name + "_diac_comp_stats.tsv"

    # generate data
    stats, agreement_rows, disagreement_rows = compare_file_diac(orig_file_path, new_file_path)

    # print and write stats to file
    out_file_path = Path(out_file_path)
    with out_file_path.open('w', encoding='utf-8') as out_fp:
        output_stats(out_fp)

if __name__ == '__main__':
    main()
