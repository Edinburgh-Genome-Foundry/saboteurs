import os
import string
from collections import OrderedDict

import pandas
import numpy as np
from pdf_reports import pug_to_html, write_report, EGF_LOGO_URL

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
STYLESHEET = os.path.join(THIS_PATH, 'assets', 'report_style.css')
TEMPLATE = os.path.join(THIS_PATH, 'assets', 'report_template.pug')
SABOTEURS_LOGO_URL = os.path.join(THIS_PATH, 'assets', 'logo.png')

def make_groups_table(analysis_results):
    """Return a Pandas dataframe indicating with elements belong to each group.
    """
    return pandas.DataFrame.from_records([
        OrderedDict([
            ('Group', group),
            ("Failure Rate (%)", int(100 * group_data['failure_rate']))] + [
                (member, "✔" * (member in group_data['members']))
                for member in analysis_results['significant_members']
            ] + [("Mystery", "*" * abs(max(0, int(group_data['deviation']))))]
        )
        for (group, group_data) in analysis_results['groups_data'].items()
    ]).sort_values('Failure Rate (%)', ascending=False)

def make_members_table(analysis_results):
    """Return a Pandas dataframe with significance/impact of the main elements.
    """
    return pandas.DataFrame.from_records([
        OrderedDict([
            ('Member', member),
            ("p-value", np.round(data['pvalue'], 3)),
            ("Effect", "+%d%%" % (100 * data['effect']))
        ])
        for (member, data) in analysis_results['significant_members'].items()
    ]).sort_values('p-value')

def dataframe_to_html(dataframe, extra_classes=()):
    """Return a HTML version of a dataframe with Semantic UI CSS style classes.
    """
    classes = ('ui', 'compact', 'celled', 'striped',
               'definition', 'table', 'groups') + extra_classes
    return dataframe.to_html(classes=classes, index=False)

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
    members_table = make_members_table(analysis_results)
    groups_table = make_groups_table(analysis_results)
    print (SABOTEURS_LOGO_URL)
    html = pug_to_html(
        filepath=TEMPLATE,
        members_table=dataframe_to_html(members_table),
        groups_table=dataframe_to_html(groups_table),
        f1_score=analysis_results['f1_score'],
        saboteurs_logo_url=SABOTEURS_LOGO_URL,
        egf_logo_url=EGF_LOGO_URL
    )
    html = replace_in_text(html, capitalize=True, replacements=replacements)
    write_report(html, outfile, extra_stylesheets=(STYLESHEET,))
