from elasticsearch import Elasticsearch
from task_risk.context_model.prediction.pipeline import create_pipeline_with_dense_transformer
from task_risk.context_model.preprocessing import df_sentences_umls_ids_to_str_without_n_gram_umls_ids
from task_risk.common.data_utils import download_annotations
from task_risk.common.umls_linker import SimpleUmlsLinker
from argparse import ArgumentParser
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
import pandas as pd

def query_paper_from_cord_uid(es, cord_uid, index='v9sentences'):
    results = es.search(
            index=index,
            size=10000,
            body={
                "query": {
                            "match": {
                              'cord_uid': cord_uid
                            }
                        }
                }
            )
    results = [hit['_source'] for hit in results['hits']['hits']]
    results = pd.DataFrame(results)
    return results


def run():
    argument_parser = ArgumentParser()
    argument_parser.add_argument('-l', '--language_model', default='en_core_sci_lg')
    argument_parser.add_argument('-m', '--metadata_filepath')
    argument_parser.add_argument('-umls', '--umls_filepath')

    args = argument_parser.parse_args()
    umls_linker = SimpleUmlsLinker(args.language_model)
    df_umls = pd.read_csv(args.umls_filepath)

    df_metadata = pd.read_csv(
        args.metadata_filepath,
        compression='zip')

    df_annotations = download_annotations()
    df_annotations = df_annotations.merge(df_metadata, on='url')

    es = Elasticsearch("http://elastic:changeme@search.coronawhy.org:80/", Port=80)
    x_train = []
    y_train = []
    df_papers = {}
    for _, row in df_annotations.iterrows():
        cord_uid = row['cord_uid']
        risk_factor = row['risk_factor']
        label = row['label']

        umls_ids = df_umls[df_umls['risk_factor'] == risk_factor]['umls_id'].tolist()

        if cord_uid not in df_papers:
            df_paper = query_paper_from_cord_uid(es, cord_uid)
            df_papers[cord_uid] = df_paper
        df_paper = df_papers[cord_uid]
        if 'UMLS' not in df_paper and 'UMLS_IDS' not in df_paper:
            df_paper = umls_linker.df_paper_raw_sentences_to_umls_ids(df_paper)
        if 'UMLS_IDS' not in df_paper and 'UMLS' in df_paper:
            df_paper = umls_linker.df_paper_umls_terms_to_umls_ids(df_paper)

        sentences = df_sentences_umls_ids_to_str_without_n_gram_umls_ids(df_paper, umls_ids)
        x_train.append(sentences)
        y_train.append(label)

    x_train = pd.DataFrame(x_train)
    y_train = pd.DataFrame(y_train)
    tfidf_vectorizer_1_3_gram = TfidfVectorizer(
        max_df=0.95,
        min_df=2,
        max_features=5000,
        ngram_range=(1, 3)
    )
    xgb_model = XGBClassifier(max_depth=3, learning_rate=0.01, n_estimators=500, n_jobs=-1)
    pipeline_components=[
        ('tfidf_vectorizer', tfidf_vectorizer_1_3_gram),
        ('clf', xgb_model)]

    pipe = create_pipeline_with_dense_transformer(pipeline_components, 1)
    pipe.fit(x_train, y_train)


if __name__ == '__main__':
    run()
