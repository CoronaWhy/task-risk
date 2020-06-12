from task_risk.common.umls_linker import SimpleUmlsLinker
from task_risk.context_model.preprocessing import df_sentences_umls_ids_to_str_without_n_gram_umls_ids
from dataclasses import dataclass
from sklearn.pipeline import Pipeline
from joblib import load
import pandas as pd
import typing
import pathlib
import os


@dataclass
class ContextModel:
    classifier_model_path: str = None
    language_model: str = None
    df_umls_entities_path: str = None
    simple_umls_linker: SimpleUmlsLinker = None
    classifier: Pipeline = None
    risk_factor_umls_ids: typing.Dict[str, typing.List[str]] = None

    def __post_init__(self):
        if self.classifier_model_path is None:
            file_directory = pathlib.Path(__file__).parent.absolute()
            self.classifier_model_path = os.path.join(
                file_directory,
                'tfidf_xgb_umls_trigram.joblib')
        if self.classifier is None:
            self.classifier = load(self.classifier_model_path)

        if self.language_model is None:
            self.language_model = 'en_core_sci_lg'
        if self.simple_umls_linker is None:
            self.simple_umls_linker = SimpleUmlsLinker(self.language_model)

        if self.df_umls_entities_path is None:
            file_directory = pathlib.Path(__file__).parent.absolute()
            self.df_umls_entities_path = os.path.join(
                file_directory,
                'df_umls_entities.csv')
        if self.risk_factor_umls_ids is None:
            df_umls_entities = pd.read_csv(self.df_umls_entities_path)
            risk_factor_umls_ids = {}
            for risk_factor, df_risk_factor_umls_entities in df_umls_entities.groupby('risk_factor'):
                risk_factor_umls_ids[risk_factor] = df_risk_factor_umls_entities['umls_id'].tolist()
            self.risk_factor_umls_ids = risk_factor_umls_ids

    def predict_paper_relevance_from_raw_sentences(
            self,
            df_paper: pd.DataFrame,
            risk_factor: str) -> float:
        assert 'sentence' in df_paper
        assert risk_factor in self.risk_factor_umls_ids

        df_paper_with_ulms = []
        for _, row in df_paper.iterrows():
            sentence = str(df_paper['sentence'])
            umls_entities = self.umls_entity_linker.get_matched_umls_entities(sentence)
            row['UMLS'] = [entity.canonical_name for entity in umls_entities]
            row['UMLS_IDS'] = [entity.cui for entity in umls_entities]
            df_paper_with_ulms.append(row)
        df_paper_with_ulms = pd.DataFrame(df_paper_with_ulms)

        return self.predict_paper_relevance_from_umls_ids(df_paper_with_ulms, risk_factor)

    def predict_paper_relevance_from_umls_terms(
            self,
            df_paper: pd.DataFrame,
            risk_factor: str) -> float:
        assert 'UMLS' in df_paper
        assert risk_factor in self.risk_factor_umls_ids

        df_paper_with_ulms = []
        for _, row in df_paper.iterrows():
            umls_terms = row['UMLS']
            umls_ids = []
            for umls_term in umls_terms:
                umls_entities = self.umls_entity_linker.get_matched_umls_entities(umls_term)
                if len(umls_entities) == 0:
                    umls_ids.append(None)
                else:
                    umls_ids.append(umls_entities[0].cui)
            row['UMLS_IDS'] = umls_ids
            df_paper_with_ulms.append(row)
        df_paper_with_ulms = pd.DataFrame(df_paper_with_ulms)

        return self.predict_paper_relevance_from_umls_ids(df_paper_with_ulms, risk_factor)

    def predict_paper_relevance_from_umls_ids(
            self,
            df_paper_with_ulms: pd.DataFrame,
            risk_factor: str) -> float:
        assert 'UMLS' in df_paper_with_ulms
        assert 'UMLS_IDS' in df_paper_with_ulms
        assert risk_factor in self.risk_factor_umls_ids
        risk_factor_umls_ids = self.risk_factor_umls_ids[risk_factor]

        df_umls_ids = df_sentences_umls_ids_to_str_without_n_gram_umls_ids(
            df_paper_with_ulms,
            risk_factor_umls_ids)
        if len(df_umls_ids) == 0:
            return 0.0

        new_paper_score = self.classifier.predict_proba([df_umls_ids])[0][1]
        return new_paper_score
