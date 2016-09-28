#!/usr/bin/env python
import unittest
import util_catpeople
import catpeople_preprocessor
from shelve import DbfilenameShelf
import rasengan

def get(lst, i, f=None):
    if f is None:
        return [e[i] for e in lst]
    else:
        return [f(e[i]) for e in lst]

def convert(parse):
    parse = [_.strip().split('\t') for _ in parse.strip().split('\n')]
    f = lambda x: x.lower().replace('-lrb-', '(').replace('-rrb-', ')')
    sentence = TM(get(parse, 1, f=f))
    parent = get(parse, 6, f=int)
    label = LABELMAP(get(parse, 7))
    ctags = CTMAP(get(parse, 3))
    return sentence, parent, label, ctags

class TestEntityDescriptors(unittest.TestCase):
    def setUp(self):
        global TM
        global LABELMAP
        global CTMAP
        self.cpfn = (util_catpeople.get_pfx() + '/catpeople_clean_segmented_context.shelf')
        self.catpeople = DbfilenameShelf(self.cpfn, protocol=-1, flag='r')
        TM = self.catpeople['__TOKEN_MAPPER__']
        TM.finalize()
        LABELMAP = util_catpeople.get_labelmap()
        CTMAP = util_catpeople.get_coarse_tagmap()
        # Inject global variables to module's namespace.
        catpeople_preprocessor.TM = TM
        catpeople_preprocessor.LABELMAP = LABELMAP
        catpeople_preprocessor.CTMAP = CTMAP
        self.testid = 1

    def assertEqual(self, a, b):
        print 'Running Test', self.testid
        try:
            assert a==b
        except AssertionError:
            print 'Failure:', str([a, b])
        self.testid += 1
        return

    @unittest.skip
    def test_entity_descriptors(self):
        with rasengan.debug_support():
            entity_descriptors = catpeople_preprocessor.entity_descriptors
            from test_identify_governors import l
            def decode(s, idi):
                return TM[[s[_] for _ in idi]]
            sentence, parent, label, ctags = (
                # 0,            1,        2,       3,     4,      5,      6,      7,      8,       9,       10,    11,     12,        13,      14,   15,       16,    17,     18,     19,      20,       21,      22,   23,     24,
                TM(['the',      'musical','august','30th',',',    '2009', '|',    'author',':', 'operator','shrek','the',  'musical','is',     'a',  'musical','with','music','by',  'jeanine','tesori','and',   'a',   'book', 'and', 'lyrics','by',  'david','lindsay-abaire','.']),
                (4,             4,        4,       16,     4,      4,      4,     4,       4,     11,       4,     13,     16,        16,      16,   0,        16,    17,     18,     21,      19,       18,      24,    18,     24,    24,      24,    29,     27,             16),
                LABELMAP(['det','amod',   'amod',  'dep', 'punct','amod','punct','appos','punct', 'nn',    'dep',  'det',  'nsubj',   'cop',   'det','ROOT',   'prep','pobj', 'prep', 'nn',    'pobj',   'cc',    'det','conj', 'cc',  'conj',  'prep', 'nn',  'pobj',          'punct']),
                CTMAP(['DET',   'ADJ',    'ADJ',   'NOUN','.',    'NUM', '.',    'NOUN',  '.',    'NOUN',  'VERB', 'DET',  'NOUN',    'VERB',  'DET','ADJ',    'ADP', 'NOUN', 'ADP',  'NOUN',  'NOUN',   'CONJ',  'DET','NOUN', 'CONJ','NOUN',  'ADP',  'NOUN','NOUN',          '.']))
            referents = [27, 28]
            self.assertEqual(decode(sentence, entity_descriptors(sentence, parent, label, ctags, referents)), ['book'])
            referents = [19,20]
            self.assertEqual(decode(sentence, entity_descriptors(sentence, parent, label, ctags, referents)), ['music'])
            referents = [10,11,12]
            self.assertEqual(decode(sentence, entity_descriptors(sentence, parent, label, ctags, referents)), ['music', 'jeanine', 'tesori', 'musical'])
            expected_output = [['executive'],
                               ['family', 'book'],
                               ['lied'],
                               ['missing'],
                               ['66th', 'united', 'states', 'secretary', 'state'],
                               ['left'],
                               ['efforts', '750-page', 'book'],
                               ['ousted', 'board', 'directors', 'hp'],
                               [],
                               ['stressed', 'points', 'book'],
                               ['dabbled', 'politics', 'dismissed', 'board'],
                               [],
                               ['attended', 'dinner'],
                               ['told', 'ceo', 'troops', 'hewlett', 'packard'],
                               ['looks', 'beautiful'],
                               ['knew'],
                               ['writes', 'career'],]
            for referents, parse, ep in zip(l[0::2], l[1::2], expected_output):
                sentence, parent, label, ctags = convert(parse)
                self.assertEqual(decode(sentence, entity_descriptors(sentence, parent, label, ctags, referents)), ep)


    def test_entity_list_to_dsctok_csr_mat(self):
        cfg = rasengan.NamespaceLite('mock')
        mention = self.catpeople[self.catpeople['__URL_LIST__'][0]][0]
        for bc in [0, 1]:
            for oeb in [0, 1]:
                cfg.binarize_counts = bc
                cfg.only_entity_bearer = oeb
                print catpeople_preprocessor.get_dsctok_from_catpeople_entity(0, [mention], cfg)
                print catpeople_preprocessor.get_dsctok_from_catpeople_entity(1, [mention], cfg)
        pass

    def test_get_ngrams_from_catpeople_entity(self):
        cfg = rasengan.NamespaceLite('mock')
        mention = self.catpeople[self.catpeople['__URL_LIST__'][0]][0]
        for bc in [0, 1]:
            for oeb in [0, 1]:
                cfg.binarize_counts = bc
                cfg.only_entity_bearer = oeb
                print catpeople_preprocessor.get_ngrams_from_catpeople_entity(0, [mention], cfg)
                print catpeople_preprocessor.get_ngrams_from_catpeople_entity(1, [mention], cfg)
        pass

if __name__ == '__main__':
    unittest.main()
