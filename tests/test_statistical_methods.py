import os
from saboteurs import csv_to_groups_data, find_statistical_saboteurs, statistics_report

def test_basics(tmpdir):
    csv_path = os.path.join('tests', 'data', "basic_example.csv")
    pdf_path = os.path.join(str(tmpdir), 'test.pdf')
    groups_data = csv_to_groups_data(csv_path)
    analysis_results = find_statistical_saboteurs(groups_data)
    statistics_report(analysis_results, pdf_path)
    data = statistics_report(analysis_results, '@memory')
    assert len(data) > 70000
