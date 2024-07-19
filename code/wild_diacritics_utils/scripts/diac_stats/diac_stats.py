##### imports #####

# importing packages
import os
import sys
import csv
import re
from pathlib import Path

# importing camel tools
from camel_tools.utils.charsets import AR_CHARSET
from camel_tools.utils.charsets import AR_DIAC_CHARSET
from camel_tools.utils.charsets import AR_LETTERS_CHARSET
from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET
from camel_tools.utils.charsets import UNICODE_SYMBOL_CHARSET

# importing handlers
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
        if (key == 'diac_group_freqs' or key == 'diac_freqs'):
            log_row([])
            log_row([key])

            if (key == 'diac_group_freqs'):
                log_row(['diac_group', 'is_canonical', 'freq'])
            elif (key == 'diac_freqs'):
                log_row(['diac', 'freq'])

            # only sort for diac_group_freqs
            if (key == 'diac_group_freqs'):
                d = sorted([(v, k) for k, v in stats[key].items()], reverse = True)
            else:
                d = [(v, k) for k, v in stats[key].items()]

            for v, k in d:
                if (key == 'diac_group_freqs'):
                    log_row([TATWEEL + k, *v])
                else:
                    log_row([TATWEEL + k, v])
            if (key != 'diac_group_freqs'):
                log_row([])
        elif (key == 'diac_group_at_index_count'):
            log_row([])
            log_row(['diac_group_at_index_count'])
            log_row(['index', 'freq'])
            for i in range(len(stats[key]) - 1):
                log_row([i, stats[key][i]])
            log_row([str(len(stats[key]) - 1) + '+', stats[key][-1]])
            log_row([])
        else:
            if (key == 'diac_count' or
                key == 'diac_group_count' or
                key == 'leading_diac_group_count' or
                key == 'tanween_fath_on_letter_before_last' or
                key == 'average_diac_per_letter' or
                key == 'canonical_diac_group_count' or
                key == 'shadda_errors_count' or
                key == 'shadda_then_diac_count'):
                log_row([])
                if (key == 'tanween_fath_on_letter_before_last' or
                    key == 'shadda_errors_count' or
                    key == 'shadda_then_diac_count'):
                    log_row([])
            log_row([key, stats[key]])

##### main program #####

def main():
    global stats

    in_path = ''
    out_path = ''

    # ensure correct argument count
    if (len(sys.argv) < 2):
        print("Usage: python diac_stats.py input.txt [output.tsv]")
        return

    # take script arguments
    in_path = sys.argv[1]
    if (len(sys.argv) >= 3):
        out_path = Path(sys.argv[2])
    else:
        out_path = os.path.splitext(in_path)[0] + "_diac_stats.tsv"

    # get statistics
    token_stats = get_file_token_stats(in_path)
    diac_stats = get_file_diac_stats(in_path)
    stats = {**token_stats, **diac_stats}

    # output statistics
    out_path = Path(out_path)
    with out_path.open('w', encoding='utf-8') as out_fp:
        output_stats(out_fp)

if __name__ == '__main__':
    main()
