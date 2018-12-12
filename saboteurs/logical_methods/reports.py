from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
import flametree
from .logical_methods import _groups_fail_table

def plot_batch(groups, ax=None):
    """Plot a diagram of all groups and the elements they contain.

    The ``groups`` parameter is a dict {group_name: [elements in the group]}.
    The ax is a Matplotlib Ax object on which to plot. If none is provided a
    new ax will be created and returned at the end.
    """
    groups = OrderedDict(groups.items())
    
    fail_table = _groups_fail_table(groups)
    array = np.array(list(fail_table.values())).T[::-1]
    lines, cols = len(array), len(array[0])

    if ax is None:
        _, ax = plt.subplots(1)
    ax.imshow(array, cmap='Purples')
    ax.set_aspect('equal')
    for y in range(lines):
        ax.axhline(y + .5, c='white')
    ax.set_yticks(range(lines))
    for x in range(cols):
        ax.axvline(x + .5, c='white')
    ax.set_xticks(range(cols))
    ax.set_xticklabels(list(fail_table.keys()), rotation=90)
    ax.set_yticklabels(list(groups.keys())[::-1])
    ax.set_xlim(-.5, cols - .5)
    ax.set_ylim(-.5, lines - .5)
    ax.set_aspect('equal')
    return ax

def generate_batch_report(groups, target='@memory', group_naming='group',
                          plot_format='pdf'):
    """Generate a report with CSV and plot describing a groups batch.
    
    Parameters
    ----------
    groups
      A (ordered) dict {group_name: [elements in the group]}.
    
    target
      Either path to a folder, or a zip file, or "@memory" to return raw
      data of a zip file containing the report.
    
    group_naming
      Word that will replace "group" in the report, e.g. "assembly", "team",
      etc.
    
    plot_format
      Formal of the plot (pdf, png, jpeg, etc.)

    """
    root = flametree.file_tree(target)
    csv = ("%s,elements\n" % group_naming) + "\n".join([
        ",".join([group] + list(elements))
        for group, elements in groups.items()
    ])
    root._file('%ss.csv' % group_naming).write(csv)
    ax = plot_batch(groups)
    ax.set_title('Elements per %s' % group_naming)
    ax.figure.savefig(
        root._file('%ss.%s' % (group_naming, plot_format)).open('wb'),
        bbox_inches='tight', format=plot_format)
    return root._close()