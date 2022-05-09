.. raw:: html

    <p align="center">
    <img alt="Saboteurs Logo" title="Saboteurs Logo" src="https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/saboteurs/master/docs/_static/images/logo.png" width="700">
    <br /><br />
    </p>
    

.. image:: https://github.com/Edinburgh-Genome-Foundry/saboteurs/actions/workflows/build.yml/badge.svg
    :target: https://github.com/Edinburgh-Genome-Foundry/saboteurs/actions/workflows/build.yml
    :alt: GitHub CI build status

.. image:: https://coveralls.io/repos/github/Edinburgh-Genome-Foundry/saboteurs/badge.svg?branch=master
   :target: https://coveralls.io/github/Edinburgh-Genome-Foundry/saboteurs?branch=master


.. raw:: html

    <h1>Saboteurs</h1>

Saboteurs is a Python library to detect failure-causing elements from success/failure data.

We use it at the `Edinburgh Genome Foundry <http://genomefoundry.org/>`_ to
identify defectuous genetic parts early:

- When assembling large fragments of DNA, each with typically 5 to 25 parts, we
  observe that some assemblies have far fewer successes ("good clones") than
  some others. We use Saboteurs to identify possible parts which would be
  causing the damage. This would generally mean that the sample corresponding
  to these parts has been compromised.
- Before launching a large batch of assemblies which reuse the same few parts,
  we use Saboteurs to design a smaller "test batch" of carefully selected
  assemblies to detect and identify possible bad parts.

See `this page <https://edinburgh-genome-foundry.github.io/saboteurs/>`_  for the HTML docs.

You can also use Saboteurs online, using `this web app <https://cuba.genomefoundry.org/find_saboteur_parts>`_ for saboteurs detection, or `this other app <https://cuba.genomefoundry.org/design_part_test_batches>`_ for designing test batches.

Usage
-----

Logical methods
~~~~~~~~~~~~~~~

**Identifying saboteur elements from experimental results**

Assume that a secret organization has a few dozen agents ([A]nna, [B]ob, [C]harlie, [D]olly, etc.). Regularly, the organization puts together a team (e.g. A, C, D) and sends them to a mission, which should succeed unless one of the members is a double-agent who will secretly sabotage the mission. Looking at the table below, can you identify the *saboteur(s)*?

======= ======= =======
Mission Members Outcome
======= ======= =======
1       A C D   Success
2       B C E   Failure
3       A B D   Success
4       D F G   Failure
======= ======= =======

Mission 2 raises suspicion on B, C, and E, but Mission 1 clears C, and mission 3 clears B. Therefore **E is a saboteur**. Meanwhile mission 4 raises **suspicion on F and G**, but while none of them is cleared by another mission, it is impossible to say if only F or only G or both are saboteurs.

The Saboteurs library has a method ``find_logical_saboteurs`` which allows to do this reasoning many groups with many elements. Here is how you would solve the problem above:

.. code:: python

    from saboteurs import find_logical_saboteurs
    groups = {
        1: ['A', 'C', 'D'],
        2: ['B', 'C', 'E'],
        3: ['A', 'B', 'D'],
        4: ['D', 'F', 'G']
    }
    find_logical_saboteurs(groups, failed_groups=[2, 4])
    # result: {'saboteurs': ['E'], 'suspicious': ['G', 'F']}

In the result, ``suspicious`` is the list of all elements which only appear in
failing groups, and ``saboteurs`` is the list of suspicious elements which are
also the only suspicious element in at least one group (and therefore confirmed
unambiguously as saboteurs).

**Designing experiment batches to find saboteur elements**

Assume that we have a list of agents, among which we suspect might hide one or two saboteurs.
We want to select a batch of "test groups" (from all possible teams) so that when we get the result
of all these teams (success or failure) we will be able to identify the one or two saboteurs.
This is solved as follows:

.. code:: python

    from saboteurs import design_test_batch
    all_possible_groups = {
        'group_1': ['A', 'B', 'C],
        'group_2': ['A', 'B', 'D', 'E'],
        # ... and many more
    }
    selected_groups, error = design_test_batch(all_possible_groups,
                                               max_saboteurs=2)
    # result:
    # OrderedDict([('group_3', ('A', 'B', 'L')),
    #              ('group_9', ('A', 'E', 'I', 'L')),
    #              ... and more])
        
You can get a quick report (CSV file and plot) of the selected groups with

.. code:: python

    generate_batch_report(selected_groups, plot_format='png',
                          target='design_test_batch_report')

.. image:: https://github.com/Edinburgh-Genome-Foundry/saboteurs/raw/master/examples/logical_methods/design_test_batch_report/groups.png

In practice, a group can have different "positions" and a given element can
only fill one of these positions. Consider for instance that there are 4
possible positions, with respective possible elements lists as follows: 

.. code:: python

    elements_per_position = {
        "Position_1": ['A', 'B', 'C'],
        "Position_2": ['D', 'E', 'F', 'G'],
        "Position_3": ['H', 'I', 'J', 'K'],
        "Position_4": ['L', 'M', 'N'],
    }

In that case there are 3x4x4x3=144 possible combinations, which can be generated
using Saboteur's utility method ``generate_combinatorial_groups``:

.. code:: python

    from saboteurs import (generate_combinatorial_groups, design_test_batch)
    possible_groups = generate_combinatorial_groups(elements_per_position)
    selected_groups = design_test_batch(possible_groups, max_saboteurs=2)
    # result:
    # OrderedDict([('group_009', ('A', 'D', 'J', 'N')),
    #              ('group_016', ('A', 'E', 'I', 'L')),
    #              ... and 13 other groups])


Statistical methods
~~~~~~~~~~~~~~~~~~~

**Example 1:** assume that a secret organization has a few dozen agents (Anna, Bob, Charlie, etc.). Regularly, the organization puts together a group (Anna and David and Peggy) and sends that group to missions, some of which will be successful, some of which will fail. After a large number of missions, looking at the results of each group, you may ask: are there some agents which tend to lower the chances of success of the groups they are part of ?

With the Saboteurs library, you would first put your data in a spreadsheet ``data.csv`` like `this one <https://github.com/Edinburgh-Genome-Foundry/saboteurs/blob/master/examples/basic_example/basic_example.csv>`_ then run the following script:

.. code:: python

  from saboteurs import (csv_to_groups_data,
                         find_statistical_saboteurs,
                         statistics_report)
  groups_data = csv_to_groups_data("data.csv")
  analysis_results = find_statistical_saboteurs(groups_data)
  statistics_report(analysis_results, "report.pdf")

You obtain the following `PDF report <https://github.com/Edinburgh-Genome-Foundry/saboteurs/raw/master/examples/statistical_methods/basic_example/basic_example.pdf>`_ highlighting which members have a significant negative impact on their groups, and where they appear:

.. raw:: html

    <p align="center">
    <img src="https://github.com/Edinburgh-Genome-Foundry/saboteurs/raw/master/Screenshot1.png" width="400">
    <img src="https://github.com/Edinburgh-Genome-Foundry/saboteurs/raw/master/Screenshot2.png" width="400">
    </p>

Installation
------------

You can install Saboteurs through PIP:

.. code::

    pip install saboteurs

Alternatively, you can unzip the sources in a folder and type:

.. code::

    python setup.py install

License = MIT
-------------

Saboteurs is an open-source software originally written at the Edinburgh Genome Foundry by `Zulko <https://github.com/Zulko>`_ and `released on Github <https://github.com/Edinburgh-Genome-Foundry/Primavera>`_ under the MIT licence (Copyright 2017 Edinburgh Genome Foundry). Everyone is welcome to contribute!

More biology software
---------------------

.. image:: https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Edinburgh-Genome-Foundry.github.io/master/static/imgs/logos/egf-codon-horizontal.png
 :target: https://edinburgh-genome-foundry.github.io/

Saboteurs is part of the `EGF Codons <https://edinburgh-genome-foundry.github.io/>`_ synthetic biology software suite for DNA design, manufacturing and validation.
