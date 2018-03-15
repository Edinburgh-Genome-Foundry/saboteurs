import pandas
from scipy.stats import binom
from collections import OrderedDict
from sklearn import linear_model, metrics
from sklearn.feature_selection import SelectFpr, f_classif
import numpy as np
from copy import deepcopy

def csv_to_groups_data(csv_path):
    dataframe = pandas.read_csv(csv_path)
    dataframe.columns = ['id', 'attempts', 'failures', 'members']
    groups_data = OrderedDict([
        (d['id'], d)
        for d in dataframe.to_dict(orient='records')
    ])
    for d in groups_data.values():
        d['members'] = d['members'].split(',')
    return groups_data

def find_saboteurs(groups_data, pvalue_threshold=0.1):
    groups_data = deepcopy(groups_data)
    members_sets = [set(group['members']) for group in groups_data.values()]
    all_members = set().union(*members_sets)
    conserved_members = members_sets[0].intersection(*members_sets)
    varying_members = sorted(all_members.difference(conserved_members))

    # Build the data

    def build_data_and_observed(selected_members, by_group=False):
        data  = []
        observed = []
        for group_name, group_data in groups_data.items():
            attempts = int(group_data['attempts'])
            failures = int(group_data['failures'])
            vector = [[
                (mb in group_data['members'])
                for mb in selected_members
            ]]
            if by_group:
                data += vector
                observed.append(1.0 * failures / attempts)
            else:
                data += attempts * vector
                observed += (attempts - failures) * [0] + failures * [1]
        return np.array(data), np.array(observed)

    # LASSO model (gives positive / negative impact)
    data, observed = build_data_and_observed(varying_members)
    regression = linear_model.RidgeCV()
    # regression = linear_model.LogisticRegressionCV(penalty='l2')
    regression.fit(data, observed)

    # ANOVA analysis (for p-values)
    selector = SelectFpr(f_classif, alpha=pvalue_threshold)
    selector.fit(data, observed)

    # select the most interesting parts
    data_ = zip(selector.pvalues_, regression.coef_, varying_members)
    significant_members = OrderedDict([
        (name, {'pvalue': pvalue})
        for pvalue, coef, name in sorted(data_)
        if (pvalue < pvalue_threshold) and (coef > 0)
    ])

    # LASSO model (significant parts only)
    data, observed = build_data_and_observed(significant_members)
    regression.fit(data, observed)
    zipped = zip(regression.coef_, significant_members.items())
    for coef, (name, data_) in zipped:
        data_['effect'] = coef

    # Build a classifier to compute a L1 score
    classifier = linear_model.LogisticRegressionCV(penalty='l2')
    classifier.fit(data, observed)
    f1_score = metrics.f1_score(observed, classifier.predict(data))

    # Find constructs which are less explained by the parts:
    data, observed = build_data_and_observed(significant_members,
                                             by_group=True)
    regression.fit(data, observed)
    predictions = regression.predict(data)
    zipped = zip(groups_data.values(), observed, predictions)
    for group_data, obs, pred in zipped:
        std = binom.std(group_data['attempts'], pred) / group_data['attempts']
        group_data['failure_rate'] = obs
        group_data['deviation'] = np.round((obs - pred) / std, decimals=1)

    return {
        'groups_data': groups_data,
        'conserved_members': conserved_members,
        'varying_members': varying_members,
        'significant_members': significant_members,
        'f1_score': f1_score
    }
