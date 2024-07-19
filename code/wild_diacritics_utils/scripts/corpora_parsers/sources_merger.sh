#!/bin/bash

# This is a bash script that merges all the files given to it in a
# single file and creates a meta tsv file that has the file that
# each sentence is from and the sentence number in the file

# Ask the user for merged file name
echo "Enter merged file name without a file extension:"
read name

# file names
merged_file="$name.txt"
merged_file_meta="${name}_meta.tsv"

# create the files empty
cat /dev/null > $merged_file
cat /dev/null > $merged_file_meta

# loop on all the files to be merged
for file in "$@"
do
	echo $file
	cat $file >> $merged_file

	line_count=$(wc -l < "$file")
	escaped_file=$(printf '%s\n' "$file" | sed -e 's/[\/&]/\\&/g')
	seq $line_count | sed -e "s/^/$escaped_file\t/" >> $merged_file_meta
done
