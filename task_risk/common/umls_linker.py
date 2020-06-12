from dataclasses import dataclass
import spacy
from scispacy.umls_linking import UmlsEntityLinker
from scispacy.abbreviation import AbbreviationDetector
from spacy_langdetect import LanguageDetector
import typing


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

    def get_matched_umls_entities(self, text: str) -> typing.List[UmlsEntity]:
        umls_entities = []
        ngram_nlp = self.nlp(text)
        for entity in ngram_nlp.ents:
            if len(entity._.umls_ents) > 0:
                umls_canonical_name = self.linker.umls.cui_to_entity[entity._.umls_ents[0][0]].canonical_name
                umls_cui = entity._.umls_ents[0][0]
                umls_entities.append(UmlsEntity(umls_canonical_name, umls_cui))
        return umls_entities
