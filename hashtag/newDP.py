
MIN_WINDOW_LENGTH = 2
MAX_WINDOW_LENGTH = 6

MAX_CONSIDER_UNIGRAM = 3

import functools
import math
import operator

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
        for line in open('./one-grams.txt'):
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
            # (MS.lookup.GetConditionalProbability(w) for w in words))
            (math.log10(singleWordProb(w)) for w in words))


def splitPairs(word):
   return [(word[:i+1], word[i+1:]) for i in range(len(word))]


@memo
def segment(word):
    if not word: return []
    allSegmentations = [[first] + segment(rest)
                            for (first, rest) in splitPairs(word)]
    return max(allSegmentations, key = wordSeqFitness)


singleWordProb = OneGramDist()


'''This function is used to normalise the hashtag
'''
def normalise(word):
	import re
	word = re.sub('[^A-Za-z0-9]+', '', word)
	if(word[0] =='#'):
		word = word[1:]
	return word.lower()


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


''' This method collects the most probable segmentations
considering the unigram data model
'''
def query(word):
    inputs = all_window_splits(word)
    dic = {}
    for input in inputs:
        dic[tuple(segment(input[0])+[input[1]]+segment(input[2]))
        ] = wordSeqFitness(segment(input[0])+[input[1]]+segment(input[2]))
    dic[tuple(segment(word))] = wordSeqFitness(segment(word))
    sorted_dic = sorted(dic.iteritems(), key=operator.itemgetter(1))[::-1]
    return sorted_dic


''' This method returns the final segmentations
keeping in mind the bigram data model from Microsoft
'''
def bigram(word):
    sorted_dic = query(word)
    chosen_segmentations = sorted_dic[:MAX_CONSIDER_UNIGRAM]
    final_dict = {}
    for segments in chosen_segmentations:
        sentence = ''
        for el in segments[0]:
            sentence += el
            sentence += ' '
        sentence = sentence[:-1]
        final_dict[sentence] = MS.lookup_bi.GetJointProbability(sentence)
    final_dict = sorted(final_dict.iteritems(), key=operator.itemgetter(1))[::-1]
    return final_dict


'''This function limits the output depending on the
probability difference between the best and the worst
segmentations returned by bigram function.
'''
def result(word):
    '''This method has some hardcoded probabilities
    that need to be cleaned up
    '''
    word = normalise(word)
    best_segmentations = bigram(word)
    benchmark_bi = best_segmentations[0][1]
    benchmark_uni = wordSeqFitness(best_segmentations[0][0])
    ans = []
    # print best_segmentations, benchmark_bi
    for el in best_segmentations:
        if(el[1] + 2.0 >= benchmark_bi):
            ans.append(el)
        elif ((benchmark_uni- wordSeqFitness(list(el[0])) < 1.5) and (el[1] + 3.5 >=benchmark_bi)):
            ans.append(el)
    return ans





