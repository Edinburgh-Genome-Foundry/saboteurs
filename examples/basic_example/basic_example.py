from saboteurs import csv_to_groups_data, find_statistical_saboteurs, analysis_report
groups_data = csv_to_groups_data("basic_example.csv")
analysis_results = find_statistical_saboteurs(groups_data)
analysis_report(analysis_results, "basic_example.pdf")
