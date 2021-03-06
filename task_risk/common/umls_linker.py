from dataclasses import dataclass
import spacy
from scispacy.umls_linking import UmlsEntityLinker
from scispacy.abbreviation import AbbreviationDetector
from spacy_langdetect import LanguageDetector
import typing
import pandas as pd


@dataclass(frozen=True)
class UmlsEntity:
    canonical_name: str
    cui: str


@dataclass
class SimpleUmlsLinker:
    language_model: str = None

    def __post_init__(self):
        self.nlp = spacy.load(self.language_model)
        self.nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)

        # Add the abbreviation pipe to the spacy pipeline. Only need to run this once.
        abbreviation_pipe = AbbreviationDetector(self.nlp)
        self.nlp.add_pipe(abbreviation_pipe)

        # Our linker will look up named entities/concepts in the UMLS graph and normalize the data
        # for us.
        self.linker = UmlsEntityLinker(resolve_abbreviations=True)
        self.nlp.add_pipe(self.linker)

    def df_paper_raw_sentences_to_umls_ids(self, df_paper: pd.DataFrame) -> pd.DataFrame:
        assert 'sentence' in df_paper

        df_paper_with_ulms = []
        for _, row in df_paper.iterrows():
            sentence = str(df_paper['sentence'])
            umls_entities = self.get_matched_umls_entities(sentence)
            row['UMLS'] = [entity.canonical_name for entity in umls_entities]
            row['UMLS_IDS'] = [entity.cui for entity in umls_entities]
            df_paper_with_ulms.append(row)
        df_paper_with_ulms = pd.DataFrame(df_paper_with_ulms)
        return df_paper_with_ulms

    def df_paper_umls_terms_to_umls_ids(self, df_paper: pd.DataFrame) -> pd.DataFrame:
        assert 'UMLS' in df_paper

        df_paper_with_umls = []
        for _, row in df_paper.iterrows():
            umls_terms = row['UMLS']
            umls_ids = []
            for umls_term in umls_terms:
                umls_entities = self.get_matched_umls_entities(umls_term)
                if len(umls_entities) == 0:
                    umls_ids.append(None)
                else:
                    umls_ids.append(umls_entities[0].cui)
            row['UMLS_IDS'] = umls_ids
            df_paper_with_umls.append(row)
        df_paper_with_umls = pd.DataFrame(df_paper_with_umls)
        return df_paper_with_umls

    def get_matched_umls_entities(self, text: str) -> typing.List[UmlsEntity]:
        umls_entities = []
        ngram_nlp = self.nlp(text)
        for entity in ngram_nlp.ents:
            if len(entity._.umls_ents) > 0:
                umls_canonical_name = self.linker.umls.cui_to_entity[entity._.umls_ents[0][0]].canonical_name
                umls_cui = entity._.umls_ents[0][0]
                umls_entities.append(UmlsEntity(umls_canonical_name, umls_cui))
        return umls_entities
