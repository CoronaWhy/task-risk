#!/usr/bin/env python
# coding: utf-8

import os
import nltk
import json
import pickle
import pandas as pd
import concurrent.futures as cf
from multiprocessing import Pool, cpu_count

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
NUM_WORKERS = cpu_count()

def process_sentence_text(stop_words, sentence_text):
    # must match sentences_df size 
    bigrams, trigrams = [], []    
    if sentence_text != '':
        text_tokens = word_tokenize(clean_text(sentence_text))
        text_to_search = [word for word in text_tokens if not word in stop_words]
        bigrams = list(ngrams(text_to_search, n=2))
        trigrams = list(ngrams(text_to_search, n=3))
    return bigrams, trigrams

def process_pickle(stop_words, pickle_file):
    ret = True
    # try:
    output = os.path.join(os.path.splitext(pickle_file)[0], '_ngrams.pkl')
    df = pd.read_pickle(pickle_file, compression="gzip")
    sentences_df = df.get(['sentence_id', 'sentence'])
    sentences_df.fillna('', inplace=True)
    del df
    bigrams, trigrams = [], []
    for index, sentence_row in sentences_df.iterrows():
        sentence_text = sentence_row['sentence']
        sent_bigrams, sent_trigrams = process_sentence_text(sentence_text)
        bigrams.append(sent_bigrams)
        trigrams.append(sent_trigrams)
        if (index +1 % 1000) == 0:
            print(f'Processed {index}/{len(sentences_df)}')
    sentences_df.assign('bigrams', bigrams)
    sentences_df.assign('trigrams', trigrams)
    with open(output, 'wb') as ngrams_file:
        pickle.dump(sentences, ngrams_file)
    del sentences_df, bigrams, trigrams
    return ret
    # except Exception as e:
    #     ret = e
    # finally:
    #     print('Pickle: {} success: {}'.format(pickle_file, ret is None))
    #     return ret

customized_stop_words = [
  'doi', 'preprint', 'copyright', 'peer', 'reviewed', 'org', 'https', 'et', 'al', 'author', 'figure', 
  'rights', 'reserved', 'permission', 'used', 'using', 'biorxiv', 'fig', 'fig.', 'al.', 'q', 'license',
  'di', 'la', 'il', 'del', 'le', 'della', 'dei', 'delle', 'una', 'da',  'dell',  'non', 'si', 'holder',
  'p', 'h'
]

stop_words = list(stopwords.words('english')) + customized_stop_words
pickle_filelist = glob(os.path.join(data_path, '*.pkl'))
errors = []
# with cf.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
with Pool(NUM_WORKERS) as executor:
    for error in tqdm(
        executor.map(partial(process_pickle, stop_words), pickle_filelist),
        total=len(pickle_filelist)):
        if error is not None:
            errors.append(str(error))

print('Finish processing bi/trigrams with {} error(s)'.format(len(errors)))
with open(os.path.join(base_path, 'erorrs.json'), 'w') as json_file:
    json_file.write(json.dumps(obj=errors) + '\n')


