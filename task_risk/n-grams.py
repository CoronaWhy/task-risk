#!/usr/bin/env python
# coding: utf-8

import os
import nltk
import json
import gzip
import pickle
import pandas as pd

from glob import glob
from tqdm import tqdm

from nltk.util import ngrams # function for making ngrams
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

from common.text_utils import clean_text

base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_path, 'data/coronawhy/v6_text')
output_path = os.path.join(base_path, 'data/coronawhy/v6_ngrams')

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
        total=len(sentences_df), desc='Process sentence', unit='sentences'):
        sentence_text = sentence_row.get('sentence')
        sent_bigrams, sent_trigrams = process_sentence_text(stop_words, sentence_text)
        bigrams.append(sent_bigrams)
        trigrams.append(sent_trigrams)
    sentences_df = sentences_df.assign(bigrams=bigrams)
    sentences_df = sentences_df.assign(trigrams=trigrams)
    return sentences_df

def read_pickle_file(pickle_path):
    df = pd.read_pickle(pickle_path, compression="gzip")
    return df

def write_pickle_file(pickle_path, pickle_df):
    with gzip.open(pickle_path, 'wb') as pickle_file:
        pickle.dump(pickle_df, pickle_file)
    
os.makedirs(output_path, exist_ok=True)

customized_stop_words = [
  'doi', 'preprint', 'copyright', 'peer', 'reviewed', 'org', 'https', 'et', 'al', 'author', 'figure', 
  'rights', 'reserved', 'permission', 'used', 'using', 'biorxiv', 'fig', 'fig.', 'al.', 'q', 'license',
  'di', 'la', 'il', 'del', 'le', 'della', 'dei', 'delle', 'una', 'da',  'dell',  'non', 'si', 'holder',
  'p', 'h'
]

stop_words = list(stopwords.words('english')) + customized_stop_words
pickle_filelist = glob(os.path.join(data_path, '*.pkl'))
errors = []

for pickle_path in pickle_filelist:
    try:
        pickle_df = read_pickle_file(pickle_path)
        processed = process_pickle(stop_words, pickle_df)
        if processed is None:
            errors.append(str(pickle_path))
            continue
        pickle_filename = os.path.splitext(os.path.basename(pickle_path))[0] + '_ngrams.pkl'
        output = os.path.join(output_path, pickle_filename)
        write_pickle_file(output, processed)
    except Exception as e:
        print(f'Got exception with {pickle_path}, {e}')

print('Finish processing bi/trigrams with {} error(s)'.format(len(errors)))
with open(os.path.join(base_path, 'erorrs.json'), 'w') as json_file:
    json_file.write(json.dumps(obj=errors) + '\n')


