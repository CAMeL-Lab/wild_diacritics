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
        print("Usage: python atb_parser.py in.txt out.txt")
        return

    # open files
    in_file = open(sys.argv[1], 'r')
    out_file = open(sys.argv[2], 'w')

    words = []
    for line in in_file:
        tokens = line.split()

        # new sentence
        if (tokens[0] == ';;;'):
            assert(tokens[1] == 'SENTENCE')

            # print previous sentence
            if (len(words) > 0):
                out_file.write(' '.join(words) + '\n')

            # start new sentence
            words = []

        elif (tokens[0] == ';;PATB:'):
            assert(tokens[2] == '#')
            words.append(tokens[3])

    if (len(words) > 0):
        out_file.write(' '.join(words) + '\n')

    in_file.close()
    out_file.close()

if __name__ == '__main__':
    main()
