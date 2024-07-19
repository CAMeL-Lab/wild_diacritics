##### imports #####

import os
import sys
import csv
from pathlib import Path

##### main program #####

def main():
    in_path = ''
    out_original_path = ''
    out_annotated_path = ''

    # ensure correct argument count
    if (len(sys.argv) < 2):
        print("Usage: python aljazeera_praser.py in.txt out.txt")
        return

    # take script arguments
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    # to prevent field size limit exceeded errors
    csv.field_size_limit(sys.maxsize)

    # open files
    with in_path.open("r", encoding="utf-8") as in_fp, \
         out_path.open('w', encoding='utf-8') as out_fp:

        tsv_reader = csv.reader(in_fp, delimiter="\t")

        # skip the first row, which is the header
        next(tsv_reader)

        # loop on the rest of the rows
        line_number = 1
        for row in tsv_reader:
            line_number += 1

            # remove trailing empty entries
            while (len(row) > 4 and row[-1] == ''):
                row.pop()

            if (len(row) > 0):
                out_fp.write(row[-1] + '\n')

if __name__ == '__main__':
    main()
