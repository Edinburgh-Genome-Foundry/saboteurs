.. raw:: html

    <p align="center">
    <img alt="Primavera Logo" title="Saboteurs Logo" src="https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/saboteurs/master/saboteurs/assets/logo.png" width="700">
    <br /><br />
    </p>

.. image:: https://travis-ci.org/Edinburgh-Genome-Foundry/Primavera.svg?branch=master
   :target: https://travis-ci.org/Edinburgh-Genome-Foundry/Primavera
   :alt: Travis CI build status

Saboteurs is a Python library to detect bad elements (or *weakest links*) from success/failure data.

**Example 1:** assume that a secret organization has a few dozen agents (Anna, Bob, Charlie, etc.). Regularly, the organization puts together a group (Anna and David and Peggy) and sends that group to missions, some of which will be successful, some of which will fail. After a large number of missions, looking at the results of each group, you may ask: are there some agents which tend to lower the chances of success of the groups they are part of ?

With the Saboteurs library, you would first put your data in a spreadsheet ``data.csv`` like `this one <>`_ then run the following script:

.. code:: python

  from saboteurs import csv_to_groups_data, find_saboteurs, analysis_report
  groups_data = csv_to_groups_data("data.csv")
  analysis_results = find_saboteurs(groups_data)
  analysis_report(analysis_results, "report.pdf")

You obtain the following `PDF report <>`_ highlighting which members have a significant negative impact on their groups, and where they appear:

.. image:: https://github.com/Edinburgh-Genome-Foundry/saboteurs/raw/master/screenshot.png

**Example 2:** Saboteurs is used at the `Edinburgh Genome Foundry <http://genomefoundry.org/>`_ to identify defectuous genetic parts. Sometimes when assembling large fragments of DNA, each with typically 5 to 25 parts, we observe that some assemblies have far fewer successes ("good clones") than some others. We use Saboteurs to identify possible parts which would be causing the damage. This would generally mean that the sample corresponding to these parts has been compromised.

Installation
-------------

You can install Primavera through PIP

.. code::

    sudo pip install saboteurs

Alternatively, you can unzip the sources in a folder and type

.. code::

    sudo python setup.py install

License = MIT
--------------

Primavera is an open-source software originally written at the Edinburgh Genome Foundry by `Zulko <https://github.com/Zulko>`_ and `released on Github <https://github.com/Edinburgh-Genome-Foundry/Primavera>`_ under the MIT licence (¢ Edinburg Genome Foundry). Everyone is welcome to contribute !

More biology software
-----------------------

.. image:: https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Edinburgh-Genome-Foundry.github.io/master/static/imgs/logos/egf-codon-horizontal.png
 :target: https://edinburgh-genome-foundry.github.io/

Saboteurs is part of the `EGF Codons <https://edinburgh-genome-foundry.github.io/>`_ synthetic biology software suite for DNA design, manufacturing and validation.
