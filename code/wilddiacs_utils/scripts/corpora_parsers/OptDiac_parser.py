##### imports #####

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

##### main program #####

def main():
    in_path = ''
    out_original_path = ''
    out_annotated_path = ''

    # ensure correct argument count
    if (len(sys.argv) < 2):
        print("Usage: python OptDiac_parser.py in.txt out_orig.txt out_annotated.txt")
        return

    # take script arguments
    in_path = sys.argv[1]
    out_original_path = sys.argv[2]
    out_annotated_path = sys.argv[3]

    tree = ET.parse(in_path)
    root = tree.getroot()

    # create output files
    original_file = open(out_original_path, 'w', encoding='utf-8')
    annotated_file = open(out_annotated_path, 'w', encoding='utf-8')

    # loop on all annotations
    for annotation in root:
        # get sentences
        original_sent = annotation.find('SENTENCE_ORIGINAL').text
        annotated_sent = annotation.find('SENTENCE_ANNOTATED').text
        if (original_sent is None):
            original_sent = ''
        if (annotated_sent is None):
            annotated_sent = ''

        # write sentences in their respective files
        original_file.write(original_sent + '\n')
        annotated_file.write(annotated_sent + '\n')
    
    # close all files
    original_file.close()
    annotated_file.close()

if __name__ == '__main__':
    main()
