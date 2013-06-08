#! /bin/bash/python


MIN_WINDOW_LENGTH = 3
MAX_WINDOW_LENGTH = 6


import functools
import math
import MicrosoftNgram as MS

def memo(f):
    "Memoize function f."
    table = {}
    def fmemo(*args):
        if args not in table:
            table[args] = f(*args)
        return table[args]
    fmemo.memo = table
    return fmemo


class OneGramDist(dict):

    def __init__(self):
        self.gramCount = 0
        for line in open('one-grams.txt'):
            (word, count) = line[:-1].split('\t')
            self[word] = int(count)
            self.gramCount += self[word]

    def __call__(self, word):
        if word in self:
            return float(self[word]) / self.gramCount
        else:
            return 1.0 / (self.gramCount * 10**(len(word) - 2))


def wordSeqFitness(words):
        return functools.reduce(lambda x,y: x+y,
            ((MS.lookup.GetConditionalProbability(w)) for w in words))

def splitPairs(word):
   return [(word[:i+1], word[i+1:]) for i in range(len(word))]

@memo
def segment(word):
    if not word: return []
    allSegmentations = [[first] + segment(rest)
                            for (first, rest) in splitPairs(word)]
    selected = max(allSegmentations, key = wordSeqFitness)
    print allSegmentations, selected, wordSeqFitness(selected)
    return max(allSegmentations, key = wordSeqFitness)

singleWordProb = OneGramDist()







''' This function exploits the fact that most of the
tweets contain words that are of length 3-5. This function
returns a list of 3-tuples that have been created by sliding window.
The middle element would be the element under inspection here.
'''
def window_splits(word, length_window=MIN_WINDOW_LENGTH):
    return [(word[:i], word[i:i+length_window], word[i+length_window:])
        for i in range(len(word)-length_window + 1)]


'''Wrapper on top of window_splits
'''
def all_window_splits(word):
    output = []
    for i in range(MIN_WINDOW_LENGTH, MAX_WINDOW_LENGTH+1):
        output = output + window_splits(word, i)
    return output


def query(word):
    inputs = all_window_splits(word)
    for input in inputs:
        print segment(input[0]), input, segment(input[2])








