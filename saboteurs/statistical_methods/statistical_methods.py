from scipy.stats import binom
from collections import OrderedDict
from sklearn import linear_model, metrics
from sklearn.feature_selection import SelectFpr, f_classif
import numpy as np
from copy import deepcopy

def _find_twins(groups_data, almost_twins_threshold=0.8):
    groups_members_list = [data["members"] for data in groups_data.values()]
    all_members = set([
        member for l in groups_members_list
        for member in l
    ])
    profiles = {
        member: [member in parts_list for parts_list in groups_members_list]
        for member in all_members
    }
    profiles = {
        member: profile
        for member, profile in profiles.items()
        if min(profile) != max(profile)
    }
    all_members = sorted(set(profiles.keys()))
    twins = {}
    almost_tweens = {m: set() for m in all_members}
    has_tweens = {m: False for m in all_members}
    for i, m1 in enumerate(all_members):
        if has_tweens[m1]:
            continue
        for m2 in all_members[i + 1:]:
            if has_tweens[m2]:
                continue
            corr = np.corrcoef(profiles[m1], profiles[m2])[1, 0]
            if corr > 0.999:
                if m1 not in twins:
                    twins[m1] = set()
                twins[m1].add(m2)
                has_tweens[m1] = has_tweens[m2] = True
            elif corr > almost_twins_threshold:
                almost_tweens[m1].add((m2, corr))
                almost_tweens[m2].add((m1, corr))
    return twins, almost_tweens, has_tweens

def find_statistical_saboteurs(groups_data, pvalue_threshold=0.1, effect_threshold=0,
                   max_significant_members=10):
    """Return statistics on possible bad elements in the data.

    Parameters
    ----------
    groups_data
      Result of ``csv_to_groups_data()``

    pvalue_threshold
      Only failure-associated elements with a p-value below this threshold
      will be included in the final statistics

    """
    groups_data = deepcopy(groups_data)
    twins, almost_tweens, has_twins = _find_twins(groups_data)
    members_sets = [set(group['members']) for group in groups_data.values()]
    all_members = set().union(*members_sets)
    conserved_members = members_sets[0].intersection(*members_sets)
    members_with_twins = set().union(*twins.values())
    varying_members = sorted(all_members.difference(conserved_members)
                                        .difference(members_with_twins))

    # Build the data

    def build_data_and_observed(selected_members, by_group=False):
        data = []
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
    regression.fit(data, observed)

    # ANOVA analysis (for p-values)
    selector = SelectFpr(f_classif, alpha=pvalue_threshold)
    selector.fit(data, observed)

    # select the most interesting parts
    data_ = zip(selector.pvalues_, regression.coef_, varying_members)
    significant_members = OrderedDict([
        (name, {'pvalue': pvalue, 'twins': twins.get(name, [])})
        for pvalue, coef, name in sorted(data_)
        if (pvalue < pvalue_threshold) and (coef > 0)
    ])

    if len(significant_members) == 0:
        return {
            'groups_data': groups_data,
            'conserved_members': conserved_members,
            'varying_members': varying_members,
            'significant_members': significant_members,
        }
    # LASSO model (significant parts only)
    data, observed = build_data_and_observed(significant_members)
    regression.fit(data, observed)
    zipped = zip(regression.coef_, significant_members.items())
    for coef, (name, data_) in zipped:
        data_['effect'] = coef
    for member in list(significant_members.keys()):
        if significant_members[member]["effect"] < effect_threshold:
            significant_members.pop(member)

    # print (significant_members)
    # significant_members = significant_members[:max_significant_members]

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
    intercept = min(0.9, max(0.1, regression.intercept_))
    for group_data, obs, pred in zipped:
        std = binom.std(group_data['attempts'], intercept) / group_data['attempts']
        group_data['failure_rate'] = obs
        group_data['deviation'] = np.round((obs - pred) / std, decimals=1)

    return {
        'groups_data': groups_data,
        'conserved_members': conserved_members,
        'varying_members': varying_members,
        'significant_members': significant_members,
        'f1_score': f1_score
    }
