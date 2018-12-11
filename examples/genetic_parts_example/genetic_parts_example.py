from saboteurs import csv_to_groups_data, find_statistical_saboteurs, analysis_report
groups_data = csv_to_groups_data("assemblies_data.csv")
analysis_results = find_statistical_saboteurs(groups_data)
analysis_report(analysis_results, "genetic_parts_example.pdf", replacements=[
    ('groups', 'assemblies'),
    ('group', 'assembly'),
    ('member', 'part')
])
