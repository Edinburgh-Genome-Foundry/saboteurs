from collections import OrderedDict
import itertools
import numpy as np
from .minimal_cover import minimal_cover


def generate_combinatorial_groups(elements_per_position, prefix='group_'):
    """Generate all possibilities from a combinatorial design.
    
    Parameters
    ----------
    elements_per_position
      A dict {position_name: [elements at this position]}
    prefix
      Prefix to generate names for the generated groups, which will be of the
      form prefix_001, prefix_002, etc.

    Returns
    -------
      groups
        An ordered dict {group_001: [e1, e2, e3, e4], group_002: [...] etc.}
        where each group contains exactly one element from each position, and
        all possible combinations of elements are there.
    """
    if hasattr(elements_per_position, 'values'):
        elements_per_position = list(elements_per_position.values())
    groups = list(itertools.product(*elements_per_position))
    n_zeros = int(np.log10(len(groups))) + 1
    return OrderedDict([
        (prefix + str(i + 1).zfill(n_zeros), group)
        for i, group in enumerate(groups)
    ])

def _minimal_elements_group_coverage(groups):
    elements_group_coverage = {}
    for group_name, elements in groups.items():
        for element in elements:
            if element not in elements_group_coverage:
                elements_group_coverage[element] = set()
            elements_group_coverage[element].add(group_name)
    return minimal_cover(set(groups.keys()), elements_group_coverage.items())

def design_test_batch(possible_groups, max_saboteurs=1):
    """Select a subset of the groups that enables to identify bad elements.

    Parameters
    ----------
    possible_groups
      A dict of the form {group_name: [elements in group]}.
    
    max_saboteurs
      The maximum number of potential bad elements among all elements in all
      the groups. A bad element is an element which will make every group
      that contains it "fail"

    Returns
    -------
    selected_groups, error
      A subset of carefully selected elements of ``possible_groups`` as a dict
      {group: [elements in group]}. The selected groups are such that
      knowing which of them failed or succeeded will be enough information
      to identify all bad elements in the original ``possible_groups`` set.
      If there is an error, then selected groups is [] and the error is a
      string explaining what went wrong.

    """
    covering_elements = _minimal_elements_group_coverage(possible_groups)
    lcov = len(covering_elements)
    if lcov <= max_saboteurs:
        return None, (
            "Not possible to detect up to %d saboteurs, as the following %d "
            "elements collectively cover all constructs, and therefore all "
            "constructs would fail at once if these %d elements alone were"
            "saboteurs:\n\n%s\n\n. Remove these elements from the problem or "
            " decrease the max number of saboteurs if possible.") % (
                max_saboteurs, lcov, lcov, ", ".join(covering_elements))
    all_elements = set(
        element
        for elements in possible_groups.values()
        for element in elements
    )
    
    product = itertools.product(*((1 + max_saboteurs) * (all_elements,)))
    all_tuples = set(
        tuple_ for tuple_ in product 
        if len(set(tuple_)) == len(tuple_)
    )
    
    def all_x_without_ys(group):
        return set(
            tuple_ for tuple_ in all_tuples
            if (tuple_[0] in group)
            and not any((e in group) for e in tuple_[1:])
        )
    
    x_without_ys_sets = [
        (name, all_x_without_ys(group))
        for name, group in possible_groups.items()
    ]
    selected = minimal_cover(all_tuples, x_without_ys_sets)
    if selected is None:
        return [], 'No solution found.'
    keys = list(possible_groups.keys())
    selected = sorted(selected, key=lambda group: keys.index(group))
    return OrderedDict((g, possible_groups[g]) for g in selected), None

def _groups_fail_table(groups):
    """Returns a dict associating each element to the groups it can fail.
    This function is used both in ``plot_elements_in_group`` and
    ``find_logical_saboteurs``.
    
    Parameters
    ----------
    groups
      Ordered dict of the form {group_name: [elements in groups]}

    Returns
    -------
    fail_table
      A dict {element_name: list[True False False ...]} where list[i] is True
      if the element is part of the i-th group in the provided ordered
      dictionnary ``groups``.
    """
    groups = list(groups.values())
    all_elements = []
    for group in groups:
        for element in group:
            if element not in all_elements:
                all_elements.append(element)
    return OrderedDict([
        (element, [(element in group) for group in groups])
        for element in all_elements
    ])

def find_logical_saboteurs(groups, failed_groups):
    """Identify bad and suspicious elements from groups failure data
    
    Parameters
    ----------
    groups
      A dict {group_name: [elements in that group]}
    failed_groups
      A list [group_name_1, group_name_2, ...] of the names of all groups that
      experimentally failed.


    Returns
    -------
    {'saboteurs': [...], 'suspicious': []}
      Where ``suspicious`` is the list of all elements which do not appear in
      successful group, and ``saboteurs`` is the list of suspicious elements
      which are also the only suspicious element in at least one group.
    """
    groups = OrderedDict(groups.items())
    failed_groups = set(failed_groups)
    groups_list = np.array(list(groups.keys()))
    fail_table = {
        element: set(groups_list[groups_])
        for element, groups_ in _groups_fail_table(groups).items()
    }
    suspicious = set(
        element for element, element_groups in fail_table.items()
        if element_groups < failed_groups
    )
    confirmed = set(
        suspect_element
        for suspect_element in suspicious
        if len(fail_table[suspect_element].difference(set().union(*(
            fail_table[other_suspect]
            for other_suspect in suspicious.difference({suspect_element})
        ))))
    )
    return dict(saboteurs=list(confirmed),
                suspicious=list(suspicious.difference(confirmed)))