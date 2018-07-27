import os
import string
from collections import OrderedDict

import pandas
import numpy as np
from pdf_reports import pug_to_html, write_report

from .version import __version__

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
STYLESHEET = os.path.join(THIS_PATH, 'assets', 'report_style.css')
TEMPLATE = os.path.join(THIS_PATH, 'assets', 'report_template.pug')

def saboteurs_pug_to_html(**context):
    defaults = {
        'logo_url': os.path.join(THIS_PATH, 'assets', 'logo.png'),
        'sidebar_text': "Generated by Saboteurs version " + __version__
    }
    for k in defaults:
        if k not in context:
            context[k] = defaults[k]
    return pug_to_html(TEMPLATE, **context)

def make_groups_table(analysis_results):
    """Return a Pandas dataframe indicating with elements belong to each group.
    """
    return pandas.DataFrame.from_records([
        OrderedDict([
            ('Group', group),
            ("Failure Rate (%)", int(100 * group_data['failure_rate']))] + [
                (member, "✔" * (member in group_data['members']))
                for member in analysis_results['significant_members']
            ] + [("Mystery", "nan" if (str(group_data['deviation']) == "nan")
                 else "*" * abs(max(0, int(group_data['deviation']))))]
        )
        for (group, group_data) in analysis_results['groups_data'].items()
    ]).sort_values('Failure Rate (%)', ascending=False)

def make_members_table(analysis_results):
    """Return a Pandas dataframe with significance/impact of the main elements.
    """
    return pandas.DataFrame.from_records([
        OrderedDict([
            ('Member', member),
            ("p-value", "%.03f" % np.round(data['pvalue'], 3)),
            ("Effect", "+%d%%" % (100 * data['effect'])),
            ("Twins", "<br/>".join(data["twins"]))
        ])
        for (member, data) in analysis_results['significant_members'].items()
    ]).sort_values('p-value')

def replace_in_text(text, replacements, capitalize=True):
    """Return the text with all the replacements done.

    Parameters
    ----------

    text
      Some string.

    replacements
      A list of the form ``[("text_to_replace", "text_replacing"), ...]``

    capitalize
      If true, then for each pair ``"text to replace"=>"text replacing"`` in
      ``replacements``, the couple ``"Text to replace"=>"Text replacing"``
      is also added (note the capitalization of the first letter)
    """
    if capitalize:
        replacements = list(replacements) + [
            (string.capwords(target), string.capwords(replacement))
            for target, replacement in replacements
        ]
    for target, replacement in replacements:
        text = text.replace(target, replacement)
    return text

def analysis_report(analysis_results, outfile, replacements=()):
    """Procude a PDF reports from the results of ``find_saboteurs()``.

    Parameters
    ----------

    analysis_results
      The result of ``saboteurs.find_saboteurs``.

    outfile
      Path to the final PDF file, or file-like object.

    replacements
      A list of the form ``[("text_to_replace", "text_replacing"), ...]``
    """
    if len(analysis_results['significant_members']) == 0:
        html = saboteurs_pug_to_html(
            members_table=None,
            groups_table=None,
            f1_score=None,
            saboteurs_found=False
        )
    else:
        html = saboteurs_pug_to_html(
            members_table=make_members_table(analysis_results),
            groups_table=make_groups_table(analysis_results),
            f1_score=analysis_results['f1_score'],
            saboteurs_found=True
        )
    html = replace_in_text(html, capitalize=True, replacements=replacements)
    write_report(html, outfile, extra_stylesheets=(STYLESHEET,))
