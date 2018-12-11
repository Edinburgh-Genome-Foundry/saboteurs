from collections import OrderedDict
import itertools
import matplotlib.pyplot as plt
import numpy as np

def minimal_cover(elements_set, subsets, max_subsets=None, heuristic='default',
                  selected=(), depth=0):
    """Generic method to find minimal subset covers.

    Parameters
    ----------
    elements_set
      The set of all ements to cover

    subsets
      A list of (name, subset)

    max_subsets
      Maximal number of subsets allowed

    heuristic
      A function ``((name, subset), selected) => value`` where ``name`` is the
      name of a subset, ``subset`` is what remains of the subset at this stage,
      ``selected`` is a list of already-selected subset names.

    selected
      (Recursion parameter, do not use.) Already-selected elements

    depth
      (Recursion parameter, do not use.). Depth of the recursion

    Returns
    -------

      None if no solution was found, else a collection of [(name, subset)...]
      in the order in which the subsets
    """


    if len(elements_set) == 0:
        return []
    if max_subsets == 0:
        return None

    if depth == 0:
        full_set = set().union(*[subset for name, subset in subsets])
        if full_set != elements_set:
            return None

    subsets = [(n, s) for (n, s) in subsets if len(s)]

    def sorting_heuristic(named_subset):
        name, subset = named_subset
        if (heuristic == 'default'):
            return len(subset)
        else:
            return heuristic(named_subset, selected)

    ordered_subsets = sorted(subsets, key=sorting_heuristic)

    while len(ordered_subsets):
        if max_subsets is not None:
            critical_subset_length = len(elements_set) / max_subsets
            max_len = max(len(s) for name, s in ordered_subsets)
            if max_len < critical_subset_length:
                return None
        name, subset = ordered_subsets.pop()
        new_elements_set = elements_set.difference(subset)
        new_subsets = [
            (name_, sub.difference(subset))
            for (name_, sub) in ordered_subsets
        ]
        new_max_subsets = None if (max_subsets is None) else max_subsets - 1
        result = minimal_cover(new_elements_set, new_subsets,
                               heuristic=heuristic,
                               selected=list(selected) + [subset],
                               max_subsets=new_max_subsets,
                               depth=depth + 1)
        if result is not None:
            return result + [name]
        ordered_subsets = [
            subset_
            for (subset_, (new_name, new_subset)) in zip(ordered_subsets,
                                                         new_subsets)
            if len(new_subset) != 0
        ]
    return None

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
        ('group_' + str(i + 1).zfill(n_zeros), group)
        for i, group in enumerate(groups)
    ])

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
    selected_groups
      A subset of carefully selected elements of ``possible_groups`` as a dict
      {group: [elements in group]}. The selected groups are such that
      knowing which of them failed or succeeded will be enough information
      to identify all bad elements in the original ``possible_groups`` set.

    """
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
    keys = list(possible_groups.keys())
    selected = sorted(selected, key=lambda group: keys.index(group))
    return OrderedDict((g, possible_groups[g]) for g in selected)

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


def plot_elements_in_groups(groups, ax=None):
    """Plot a diagram of all groups and the elements they contain.

    The ``groups`` parameter is a dict {group_name: [elements in the group]}.
    The ax is a Matplotlib Ax object on which to plot. If none is provided a
    new ax will be created and returned at the end.
    """
    groups = OrderedDict(groups.items())
    
    fail_table = _groups_fail_table(groups)
    array = np.array(list(fail_table.values()))
    lines, cols = len(array), len(array[0])

    if ax is None:
        _, ax = plt.subplots(1)
    ax.imshow(array, cmap='Purples')
    ax.set_aspect('equal')
    for y in range(lines):
        ax.axhline(y + .5, c='white')
    ax.set_yticks(range(lines))
    ax.set_yticklabels(fail_table.keys())
    for x in range(cols):
        ax.axvline(x + .5, c='white')
    ax.set_xticks(range(cols))
    ax.set_xticklabels(groups, rotation=90)
    ax.set_xlim(-.5, cols - .5)
    ax.set_ylim(-.5, lines - .5)
    ax.set_aspect('equal')
    return ax

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