#!/usr/bin/env python
'''
| Filename    : catpeople_experiment_linear_separability_analyze_pickle.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Fri Sep 30 23:11:33 2016 (-0400)
| Last-Updated: Sat Oct  1 16:13:05 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 20
'''
import catpeople_experiment_linear_separability as ce

class LinSepAnalyzer(ce.LinSepChecker):
    def __init__(self, *args_, **kwargs):
        super(LinSepAnalyzer, self).__init__(*args_, **kwargs)
        return

    def __call__(self):
        for fold_idx, (cat, (train_idx, test_idx)) in enumerate(self.fold_iterator()):
            if cat in ['Oregon_State_University_faculty', 'Mayflower_passengers']:
                mat, classifier = self.ls_exp_call_impl(fold_idx, cat, train_idx, test_idx)
                scores, scratch = self.pa.record[cat][-1]
                coef, intercept, features = scratch['coef'], scratch['intercept'], scratch['features']
                positive_feat = [a  for  (a,b) in zip(features, coef.T) if float(b) > 0]
                negative_feat = [a  for  (a,b) in zip(features, coef.T) if float(b) < 0]
                print 'Test',classifier.decision_function(mat[test_idx])
                print 'Train',classifier.decision_function(mat[train_idx])
                for dset_type, dset in [('test_idx', test_idx), ('train_idx', train_idx)]:
                    for idx in dset:
                        for feat_type, feat_list in [('positive_feat', positive_feat), ('negative_feat', negative_feat)]:
                            print self.url_list[idx], dset_type, feat_type, \
                                self.TM[[features[i]
                                         for i in mat[idx].nonzero()[1]
                                         if features[i] in feat_list]]


if __name__ == '__main__':
    args = ce.populate_args()
    ce.args = args
    lsa = LinSepAnalyzer(
        datacfg=ce.ce.DATACONFIG,
        ppcfg=ce.ce.CONFIG[args.ppcfg],
        expcfg=ce.ce.EXPCONFIG[args.expcfg])
    lsa()
