##### imports #####

# importing packages
import os
import sys
import random
from pathlib import Path

##### main program #####

def main():
    in_paths = []
    out_paths = []

    # ensure correct argument count
    if (len(sys.argv) < 2):
        print("Usage: python parallel_shuffle.py file1 [file2 ...]")
        return

    # take input paths and generate output paths
    in_paths = sys.argv[1:]
    out_paths = [os.path.splitext(p)[0] + '_shuffled' + os.path.splitext(p)[1] for p in in_paths]
    assert(len(in_paths) > 0)

    # ensure same file lengths
    lines_count = sum(1 for _ in open(in_paths[0]))
    for in_path in in_paths:
        curr_lines_count = sum(1 for _ in open(in_path))
        if (curr_lines_count != lines_count):
            # differences in lines count!
            print('ERROR: All files should have the same number of lines!')
            return
   
    # generate a random seed to use in all shuffles
    seed = random.randrange(sys.maxsize)
    # print(f'seed: {seed}')

    # loop through files
    for i in range(len(in_paths)):
        in_path = in_paths[i]
        out_path = out_paths[i]

        # read lines
        in_file = open(in_path)
        lines = in_file.readlines()

        # shuffle
        # print('---')
        # print(lines)
        random.seed(seed)
        random.shuffle(lines)
        # print(lines)

        # write lines
        out_file = open(out_path, 'w')
        out_file.writelines(lines)
        out_file.close()

if __name__ == '__main__':
    main()
