#!/usr/bin/env python
# coding: utf-8

import nltk
import pickle
import pandas as pd
import concurrent.futures as cf

from tqdm import tqdm
from functools import partial

from nltk.util import ngrams # function for making ngrams
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

from task_risk.common.text_utils import clean_text

base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_path, 'raw')
data_path = os.path.join(base_path, 'data/dataset_v6/v6_text')
NUM_WORKERS = 32

def process_pickle(pickle_file, stop_words):
    ret = True
    try:
        output = os.path.join(os.path.splitext(pickle_file)[0], '_ngrams.pkl')
        df = pd.read_pickle(data_file, compression="gzip")
        sentences = df.concat([df['sentence_id'], df['sentence'].astype(str)])
        del df
        bigrams = []
        trigrams = []
        for sentence in sentences.iterows():
            text_tokens = word_tokenize(clean_text(sentence))
            text_to_search = [word for word in text_tokens if not word in stop_words]
            bigrams.extend(ngrams(text_to_search, n=2))
            trigrams.extend(ngrams(text_to_search, n=3))
        sentences['bigrams'] = bigrams
        sentences['trigrams'] = trigrams
        with open(os.path.join(data_path, 'classification_dataset.pickle'), 'wb') as f:
            pickle.dump(sentences, output)
        del sentences, bigrams, trigrams
    except Exception as e:
        ret = e
    finally:
        print('Pickle: {} success: {}'.format(pickle_file, ret is None))
        return ret

customized_stop_words = [
  'doi', 'preprint', 'copyright', 'peer', 'reviewed', 'org', 'https', 'et', 'al', 'author', 'figure', 
  'rights', 'reserved', 'permission', 'used', 'using', 'biorxiv', 'fig', 'fig.', 'al.', 'q', 'license',
  'di', 'la', 'il', 'del', 'le', 'della', 'dei', 'delle', 'una', 'da',  'dell',  'non', 'si', 'holder',
  'p', 'h'
]

stop_words = list(stopwords.words('english')) + customized_stop_words
pickle_filelist = glob(os.path.join(data_path, 'v6_text/*.pkl'))
errors = []
with cf.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    for error in tqdm(
        executor.map(partial(process_pickle, pickle_filelist), stop_words),
        total=len(pickle_filelist)):
        if error is not None:
            errors.append((error))

print('Finish processing bi/trigrams with {} error(s)'.format(len(errors)))
with open(os.path.join(base_path, 'erorrs.json'), 'w') as json_file:
    json_file.write(json.dumps(obj=errors) + '\n')