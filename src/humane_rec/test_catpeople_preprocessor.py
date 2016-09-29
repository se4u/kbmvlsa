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
    @classmethod
    def setUpClass(cls):
        super(TestEntityDescriptors, cls).setUpClass()
        global TM
        global LABELMAP
        global CTMAP
        cls.cpfn = (util_catpeople.get_pfx() + '/catpeople_clean_segmented_context.shelf')
        cls.parsefn = (util_catpeople.get_pfx() + '/catpeople.parse.pkl')
        cls.catpeople = DbfilenameShelf(cls.cpfn, protocol=-1, flag='r')
        TM = cls.catpeople['__TOKEN_MAPPER__']
        TM.finalize()
        LABELMAP = util_catpeople.get_labelmap()
        CTMAP = util_catpeople.get_coarse_tagmap()
        # Inject global variables to module's namespace.
        catpeople_preprocessor.TM = TM
        catpeople_preprocessor.LABELMAP = LABELMAP
        catpeople_preprocessor.CTMAP = CTMAP
        catpeople_preprocessor.GENDER_TO_PRONOUN = catpeople_preprocessor.get_gender_to_pronoun(TM)
        catpeople_preprocessor.TOKEN_TO_GENDER = catpeople_preprocessor.get_token_to_gender(TM)
        catpeople_preprocessor.populate_dsctok_globals()
        cls.testid = 1
        print 'Calling setup'

    def expectEqual(self, a, b):
        print 'Running Test', self.testid
        try:
            assert a==b
        except AssertionError:
            print 'Failure:', str([a, b])
        self.testid += 1
        return

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
            self.expectEqual(decode(sentence, entity_descriptors(sentence, parent, label, ctags, referents)), ['book'])
            referents = [19,20]
            self.expectEqual(decode(sentence, entity_descriptors(sentence, parent, label, ctags, referents)), ['music'])
            referents = [10,11,12]
            self.expectEqual(decode(sentence, entity_descriptors(sentence, parent, label, ctags, referents)), ['music', 'jeanine', 'tesori', 'musical'])
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
                self.expectEqual(decode(sentence, entity_descriptors(sentence, parent, label, ctags, referents)), ep)
        return


    def test_entity_list_to_dsctok_csr_mat(self):
        cfg = rasengan.NamespaceLite('mock')
        mention = [[(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 11, 12, 1, 13, 14, 15, 16, 17, 18, 12, 19, 18, 20, 15, 21, 22, 23),
                    [24, 11, 25, 26, 0, 27, 19, 10, 28]], 0, 20, 23]
        PARSES = dict([((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 11, 12, 1, 13, 14, 15, 16, 17, 18, 12, 19, 18, 20, 15, 21, 22, 23),
                        [(4, 4, 4, 16, 4, 4, 4, 4, 4, 11, 4, 13, 16, 16, 16, 0, 16, 17, 18, 21, 19, 18, 24, 18, 24, 24, 24, 29, 27, 16),
                         [13, 14, 14, 28, 21, 14, 21, 15, 21, 33, 28, 13, 1, 24, 13, 0, 29, 30, 29, 33, 30, 38, 13, 37, 38, 37, 29, 33, 30, 21],
                         [5, 1, 1, 6, 0, 7, 0, 6, 0, 6, 10, 5, 6, 10, 5, 1, 2, 6, 2, 6, 6, 4, 5, 6, 4, 6, 2, 6, 6, 0],
                         [9, 15, 15, 21, 2, 8, 2, 21, 4, 21, 36, 9, 21, 41, 9, 15, 14, 21, 14, 21, 21, 7, 9, 21, 7, 24, 14, 21, 21, 3]]),
                       ((24, 11, 25, 26, 0, 27, 19, 10, 28),
                        [(3, 3, 0, 3, 8, 8, 8, 4, 3),
                         [3, 23, 0, 29, 13, 16, 33, 30, 21],
                         [8, 10, 10, 2, 5, 7, 6, 6, 0],
                         [27, 41, 39, 14, 9, 8, 21, 21, 3]])])
        for bc in [0, 1]:
            for oeb in [0, 1]:
                cfg.binarize_counts = bc
                cfg.only_entity_bearer = oeb
                self.expectEqual(dict(catpeople_preprocessor.get_dsctok_from_catpeople_entity([mention], cfg, PARSES)), {14:1})
        return

    def test_get_ngrams_from_catpeople_entity(self):
        cfg = rasengan.NamespaceLite('mock')
        mention = [[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [24, 11, 25, 26, 0, 27, 19, 10, 28], [38, 0]], 0, 7, 9]
        gold_results = {
            (0, 0, 0): {0: 3, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 19: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 1, 38: 1},
            (0, 0, 1): {29849092: 1, 13776517: 1, 8036294: 1, 1148042: 1, 32145167: 1, 9184336: 1, 1317998137681: 1, 2296084: 1, 10332378: 1, 3444126: 1, 44773599: 1, 1148068: 1, 4592168: 1, 1317998137705: 1, 28701036: 1, 5740210: 1, 30997107: 1, 1317998137719: 1, 6888252: 1, 22960830: 1, 12628479: 1},
            (0, 1, 0): {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},
            (0, 1, 1): {8036294: 1, 4592168: 1, 1148042: 1, 9184336: 1, 1317998137681: 1, 5740210: 1, 2296084: 1, 10332378: 1, 6888252: 1, 3444126: 1},
            (1, 0, 0): {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 19: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 1, 38: 1},
            (1, 0, 1): {29849092: 1, 13776517: 1, 8036294: 1, 1148042: 1, 32145167: 1, 9184336: 1, 1317998137681: 1, 2296084: 1, 10332378: 1, 3444126: 1, 44773599: 1, 1148068: 1, 4592168: 1, 1317998137705: 1, 28701036: 1, 5740210: 1, 30997107: 1, 1317998137719: 1, 6888252: 1, 22960830: 1, 12628479: 1},
            (1, 1, 0): {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},
            (1, 1, 1): {8036294: 1, 4592168: 1, 1148042: 1, 9184336: 1, 1317998137681: 1, 5740210: 1, 2296084: 1, 10332378: 1, 6888252: 1, 3444126: 1},
        }
        for bc in [0, 1]:
            for oeb in [0, 1]:
                cfg.binarize_counts = bc
                cfg.only_entity_bearer = oeb
                for ngram in [0, 1]:
                    self.expectEqual(dict(catpeople_preprocessor.get_ngrams_from_catpeople_entity(ngram, [mention], cfg)), gold_results[(bc,oeb,ngram)])
        return

if __name__ == '__main__':
    unittest.main()
