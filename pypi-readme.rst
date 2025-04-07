Saboteurs
=========

Saboteurs is a Python library to detect bad elements (or *weakest links*)
from success/failure data. It can also be used to design "test batches" which
will allow to easily identify bad elements.

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

Infos
-----

**PIP installation:**

.. code:: bash

  pip install saboteurs

**Docs:** `<https://edinburgh-genome-foundry.github.io/saboteurs/>`_

**Github page:** `<https://github.com/Edinburgh-Genome-Foundry/saboteurs>`_

**Web apps:**

`Saboteurs detection <https://cuba.genomefoundry.org/find_saboteur_parts>`_

`Batch design <https://cuba.genomefoundry.org/design_part_test_batches>`_


**License:** MIT

Copyright 2017 Edinburgh Genome Foundry, University of Edinburgh


More biology software
---------------------

.. image:: https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Edinburgh-Genome-Foundry.github.io/master/static/imgs/logos/egf-codon-horizontal.png
 :target: https://edinburgh-genome-foundry.github.io/

Saboteurs is part of the `EGF Codons <https://edinburgh-genome-foundry.github.io/>`_ synthetic biology software suite for DNA design, manufacturing and validation.
