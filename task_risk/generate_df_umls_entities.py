from task_risk.common.umls_linker import SimpleUmlsLinker
from argparse import ArgumentParser
import pandas as pd


def run():
    argument_parser = ArgumentParser()
    argument_parser.add_argument('-l', '--language_model', default='en_core_sci_lg')
    argument_parser.add_argument('-n', '--ngram_filepath')
    args = argument_parser.parse_args()
    umls_linker = SimpleUmlsLinker(args.language_model)

    df_ngrams = pd.read_csv(args.filepath)
    df_umls_entities = []
    for _, row in df_ngrams.iterrows():
        ngram = row['ngram']
        risk_factor = row['risk_factor']

        if not pd.isna(ngram):
            umls_entities = umls_linker.get_matched_umls_entities(ngram)
            for umls_entity in umls_entities:
                df_umls_entities.append({
                    'risk_factor': risk_factor,
                    'ngram': ngram,
                    'umls_term': umls_entity.canonical_name,
                    'umls_id': umls_entity.cui
                })
    df_umls_entities = pd.DataFrame(df_umls_entities)


if __name__ == '__main__':
    run()
