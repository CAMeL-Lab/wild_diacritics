##### instructions #####
# This takes a txt file of text, normalizes and tokenizes the input and then rewrites it into
# an output file so that it is ready to be diacritized by the camel tools
#
# USAGE:
# python normalize_tokenize.py input.txt output.txt
#####

##### imports #####

import sys
from pathlib import Path

from camel_tools.tokenizers.word import simple_word_tokenize as tokenize
from camel_tools.utils.normalize import normalize_unicode as normalize

##### main program #####

def main():

    # ensure valid number of arguments
    if (len(sys.argv) < 2):
        print("USAGE: python3 normalize_tokenize.py in.txt out.txt")
        return

    # take script arguments
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    # take input
    with input_path.open('r', encoding='utf-8') as in_fp, \
         output_path.open('w', encoding='utf-8') as out_fp:

        for sent in in_fp:
            # normalize then tokenize sent
            sent = normalize(sent)
            sent = ' '.join(tokenize(sent, split_digits = True))

            # write the data back to a txt file
            out_fp.write(sent + '\n')

if __name__ == '__main__':
    main()
