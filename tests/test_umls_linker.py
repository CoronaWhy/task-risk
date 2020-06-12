from task_risk.common.umls_linker import SimpleUmlsLinker, UmlsEntity
from unittest import TestCase


class TestSimpleUmlsLinker(TestCase):
    simple_umls_linker_small = SimpleUmlsLinker('en_core_sci_sm')

    def test_get_matched_umls_entities(self):
        expected = [UmlsEntity(canonical_name='Heart', cui='C0018787')]
        result = self.simple_umls_linker_small.get_matched_umls_entities('heart')
        self.assertEqual(expected, result)

    def test_get_matched_umls_entities_empty(self):
        expected = []
        result = self.simple_umls_linker_small.get_matched_umls_entities('ainavsnjsadladsn')
        self.assertEqual(expected, result)


if __name__ == '__main__':
    TestSimpleUmlsLinker()
