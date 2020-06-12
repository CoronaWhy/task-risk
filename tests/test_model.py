from task_risk.context_model.model import ContextModel
from unittest import TestCase
import pandas as pd


class TestContextModel(TestCase):
    context_model = ContextModel(
        language_model='en_core_sci_sm',
        risk_factor_umls_ids={
            'heart disease': []
        })

    def test_predict_paper_relevance_from_raw_sentences(self):
        df_paper = pd.DataFrame({
            'sentence': ['heart disease causes coronavirus']
        })
        result = self.context_model.predict_paper_relevance_from_raw_sentences(
            df_paper,
            'heart disease')
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)


    def test_predict_paper_relevance_from_umls_terms(self):
        df_paper = pd.DataFrame({
            'UMLS': [['heart disease', 'cardiac arrest']]
        })
        result = self.context_model.predict_paper_relevance_from_umls_terms(
            df_paper,
            'heart disease')
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_predict_paper_relevance_from_umls_ids(self):
        df_paper = pd.DataFrame({
            'UMLS': [['heart disease', 'cardiac arrest']],
            'UMLS_IDS': [['C0002962', 'C0003811']]
        })
        result = self.context_model.predict_paper_relevance_from_umls_ids(
            df_paper,
            'heart disease')
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)
