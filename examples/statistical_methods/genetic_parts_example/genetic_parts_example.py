from saboteurs import csv_to_groups_data, find_statistical_saboteurs, statistics_report
groups_data = csv_to_groups_data("assemblies_data.csv")
analysis_results = find_statistical_saboteurs(groups_data)
statistics_report(analysis_results, "genetic_parts_example.pdf", replacements=[
    ('groups', 'assemblies'),
    ('group', 'assembly'),
    ('member', 'part')
])
