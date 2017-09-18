
import argparse

from random import shuffle

def shuffle_lines_in_file(input_filename):
    with open(input_filename, mode="r") as myFile:
        lines = list(myFile)
    shuffle(lines)
    return lines

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data", help="location of text data to use as input")
parser.add_argument("-o", "--output", help="where to output the results", default=0)
args = parser.parse_args()

shuffled_lines = shuffle_lines_in_file(args.data)

file = open(args.output, 'w')
for item in shuffled_lines:
  file.write("%s" % item)
  