#!/bin/bash

### proces the raw data ###
for dir in ./*/
do
	(
		cd "$dir"
		pwd

		# unzip everything
		# gzip -d *.gz

		# this adds a .xml extension to all files
		# for file in ./*
		# do
		# 	mv -- "$file" "$file.xml"
		# done

		# this parses all the xml files into txt files
		# for file in ./*.xml
		# do
		# 	cat $file \
		# 		| sed '/<P>/{n;:l N;/<\/P>/b; s/\n/ /; bl}' \
		# 		| sed '/<HEADLINE>/{n;:l N;/<\/HEADLINE>/b; s/\n/ /; bl}' \
		# 		| sed '/<DATELINE>/{n;:l N;/<\/DATELINE>/b; s/\n/ /; bl}' \
		# 		| grep -hv '^<' \
		# 		> "${file%.xml}.txt"
		# done

		# delete all files not ending with .txt
		# find . -not -name "*.txt" -exec rm {} +

		# merge files
		# echo "$(basename $dir)" | bash ../../../../wild_diacritics_utils/scripts/corpora_parsers/sources_merger.sh *.txt

		# move merged files from parsed_data directory to sources
		# source=$(basename $dir)
		# mv "$source.txt" "../../sources/$source/."
		# mv "${source}_meta.tsv" "../../sources/$source/."
	)
done

### take 50k samples from each file ###
# for file_path in ./*/*.txt
# do
# 	echo $file_path
# 	suffix=".txt"
# 	sample_file_path="${file_path%$suffix}_50k.txt"
# 	echo $sample_file_path
# 
# 	shuf -n 50000 $file_path > $sample_file_path
# done

### tokenize all the sample files ###
# for file_path in ./*/*_50k.txt
# do
# 	echo $file_path
# 	suffix=".txt"
# 	tokenized_file_path="${file_path%$suffix}_tokenized.txt"
# 	echo $tokenized_file_path
# 
# 	python3 ../../../wild_diacritics_utils/scripts/normalize_tokenize/normalize_tokenize.py $file_path $tokenized_file_path
# done

### generate diacritic statistics for all the tokenized files ###
# for file_path in ./*/*_tokenized.txt
# do
# 	echo $file_path
# 	python3 ../../../wild_diacritics_utils/scripts/diac_stats/diac_stats.py $file_path
# done
