# diac\_stats.py

## Description

This is a python script that takes a text file containing (tokenized and normalized) arabic text and outputs data about the words and more importantly about the diacritization of the arabic words in the text by running `get_file_diac_stats()` from [diac\_handler.py](../../modules/diac_handler) module and `get_file_token_stats()` from [token\_handler.py](../../modules/token_handler) module

Here is the full list of the data generated:

- number of tokens
- number of arabic words
	- and a file with all of them on separate lines
- number of numbers
	- and a file with all of them on separate lines
- number of punctuations
	- and a file with all of them on separate lines
- number of symbols
	- and a file with all of them on separate lines
- number of other tokens (not arabic, numeric, punct or symbolic)
- number of arabic words with any number of diacritical marks
	- and a file with all of them on separate lines
- number of arabic words with full diacritisation
	- and a file with all of them on separate lines
- number of diacritical marks
- number of occurances of each diacritical mark present
- number of diac groups (diac combinations on one letter)
- number of diac groups at each letter index
	(i.e. number of diac groups that occured on the zero'th letter of
	a word, and the same for the first letter, second, third, etc)
	- and a file with all of them on separate lines
- number of diac groups that occured on the first letter of a word
	- and a file with all of them on separate lines
- number of diac groups that occured on the last letter of a word
	- and a file with all of them on separate lines
- number of occurances of each diac group

> our definition of full diacritization is that each letter must have
> a fatha, damma, kasra, sukoon, or any kind of tanween on them except
> the mad letters which are the `ا`, `و`, `ي` which can have no diacs
> however, for a word to be fully diacritized must have at least a one
> letter that has some of the previously mentioned diacritical marks

> note that the zero'th index diac group is the diac group before the
> first letter of the word

## Usage

The script can be used by running the following line in the terminal

```bash
python diac_stats.py input.txt [output_dir]
```

The script takes 1 required input which is the path to the text file with the arabic text to calculate the statistics of, and the second is an optional argument that is the path to the directory that the script will create (if not already created) and put all the output data inside

## Input/Output Specifications

**Input**

The input file `input.txt` must be tokenized using the simple word tokenizer and letter-normalized, and the script tokenize\_normalize.py can be used to perform both tasks. Running the `diac_stats.py` script on untokenized data will most probably yield wrong data.

**Output**

The data previously mentioned is in two categories, the statistics and files with all different categories of words. The statistics will be printed in the terminal and will also be written in a tsv file in the `output_dir` with the other files with compilations of different words in each category as outlined in the Description section above.
