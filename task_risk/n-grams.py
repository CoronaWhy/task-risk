#!/usr/bin/env python
# coding: utf-8

import os
import nltk
import json
import time
import pickle
import pandas as pd
import concurrent.futures as cf

from glob import glob
from tqdm import tqdm
from functools import partial

from nltk.util import ngrams # function for making ngrams
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

from common.text_utils import clean_text

base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_path, 'data/coronawhy/v6_text')

def process_sentence_text(stop_words, sentence_text):
    # must match sentences_df size 
    bigrams, trigrams = [], []    
    if sentence_text != '':
        text_tokens = word_tokenize(clean_text(sentence_text))
        text_to_search = [word for word in text_tokens if not word in stop_words]
        bigrams = list(ngrams(text_to_search, n=2))
        trigrams = list(ngrams(text_to_search, n=3))
    return bigrams, trigrams

def process_pickle(stop_words, pickle_df):
    ret = None
    sentences_df = pickle_df.get(['sentence_id', 'sentence']).copy()
    sentences_df.fillna('', inplace=True)
    bigrams, trigrams = [], []
    for index, sentence_row in tqdm(sentences_df.iterrows(),
        total=len(sentences_df), desc='Reading sentences'):
        sentence_text = sentence_row.get('sentence')
        sent_bigrams, sent_trigrams = process_sentence_text(stop_words, sentence_text)
        bigrams.append(sent_bigrams)
        trigrams.append(sent_trigrams)
    sentences_df = sentences_df.assign(bigrams=bigrams)
    sentences_df = sentences_df.assign(trigrams=trigrams)
    return sentences_df

def read_pickle_file(pickle_path):
    start_time = time.time()
    print(f'Reading pickle from {pickle_path}', end='')
    df = pd.read_pickle(pickle_path, compression="gzip")
    elapsed_time = time.time() - start_time
    print(f' done in {round(elapsed_time, 2)} seconds')
    return df

customized_stop_words = [
  'doi', 'preprint', 'copyright', 'peer', 'reviewed', 'org', 'https', 'et', 'al', 'author', 'figure', 
  'rights', 'reserved', 'permission', 'used', 'using', 'biorxiv', 'fig', 'fig.', 'al.', 'q', 'license',
  'di', 'la', 'il', 'del', 'le', 'della', 'dei', 'delle', 'una', 'da',  'dell',  'non', 'si', 'holder',
  'p', 'h'
]

stop_words = list(stopwords.words('english')) + customized_stop_words
pickle_filelist = glob(os.path.join(data_path, '*.pkl'))
errors = []
# pickles = [read_pickle_file(pickle_path) for pickle_path in pickle_filelist]

for pickle_path in pickle_filelist:
    try:
        pickle_df = read_pickle_file(pickle_path)
        processed = process_pickle(stop_words, pickle_df)
        if processed is None:
            errors.append(str(pickle_path))
        else:
            output = os.path.splitext(pickle_path)[0] + '_ngrams.pkl'
            with open(output, 'wb') as ngrams_file:
                pickle.dump(processed, ngrams_file)
    except Exception as e:
        print(f'Got exception with {pickle_path}, {e})

print('Finish processing bi/trigrams with {} error(s)'.format(len(errors)))
with open(os.path.join(base_path, 'erorrs.json'), 'w') as json_file:
    json_file.write(json.dumps(obj=errors) + '\n')


