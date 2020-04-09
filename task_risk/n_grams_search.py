#!/usr/bin/env python

import os
import json
import pandas as pd
import concurrent.future as cf

from tqdm import tqdm
from collections import Counter
from n_grams_dataset import read_pickle_file
from config import base_path, data_path

def parse_ngram_files(filelist):
    dataset = pd.DataFrame()
    with cf.ThreadPoolExecutor as executor:
        for df in tqdm(executor.map(read_pickle_file, filelist)):
            dataset = pd.concat([dataset, df])
    return dataset

def search_in_ngrams(ngrams, search_terms):
    results = {}
    for term in search_terms:
        results[term] = []
        for ngram_tuple in ngrams:
            if any(map(lambda x: x == term, ngram_tuple)):
                results[term].append(ngram_tuple)
    return results

def search(search_terms=None, k=25):
    top_k = k
    input_path = os.path.join(base_path, 'data/coronawhy/v6_ngrams')
    ngrams_df = parse_ngram_files(input_path)

    # search sentence wide
    results = { term: { 'bigrams': [], 'trigrams': [] } for term in search_terms }
    for index, sentence in ngrams_df.iterrows():
        for ngram in ['bigrams', 'trigrams']:
            count = Counter(sentence[ngram])
            ngrams_with_freq = count.most_common(top_k)
            ngrams = [ngram for ngram, _ in ngrams_with_freq]

            search_results = search_in_ngrams(ngrams, search_terms)
            for term in search_terms:
                if len(search_results) > 0:
                    results[term][ngram].append((sentence['sentence_id'],
                      search_results[term]))

    for term in search_terms:
        print(term)
        print(results[term])

    with open(os.path.abspath('./results'), 'w') as json_file:
        json_file.write(json.dumps(obj=results) + '\n')

if __name__ == '__main__':
    main()

