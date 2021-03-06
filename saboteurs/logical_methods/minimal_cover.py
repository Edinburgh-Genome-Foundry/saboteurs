"""Provides a generic and slightly-smarter minimal cover algorithm."""


def minimal_cover(
    elements_set, subsets, max_subsets=None, heuristic="default", selected=(), depth=0
):
    """Generic method to find minimal subset covers.

    Parameters
    ----------
    elements_set
      The set of all elements to cover.

    subsets
      A list of (name, subset).

    max_subsets
      Maximal number of subsets allowed.

    heuristic
      A function ``((name, subset), selected) => value`` where ``name`` is the
      name of a subset, ``subset`` is what remains of the subset at this stage,
      ``selected`` is a list of already-selected subset names.

    selected
      (Recursion parameter, do not use.) Already-selected elements.

    depth
      (Recursion parameter, do not use.). Depth of the recursion.

    Returns
    -------

      None if no solution was found, else a collection of [(name, subset)...].
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
        if heuristic == "default":
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
            (name_, sub.difference(subset)) for (name_, sub) in ordered_subsets
        ]
        new_max_subsets = None if (max_subsets is None) else max_subsets - 1
        result = minimal_cover(
            new_elements_set,
            new_subsets,
            heuristic=heuristic,
            selected=list(selected) + [subset],
            max_subsets=new_max_subsets,
            depth=depth + 1,
        )
        if result is not None:
            return result + [name]
        ordered_subsets = [
            subset_
            for (subset_, (new_name, new_subset)) in zip(ordered_subsets, new_subsets)
            if len(new_subset) != 0
        ]
    return None
