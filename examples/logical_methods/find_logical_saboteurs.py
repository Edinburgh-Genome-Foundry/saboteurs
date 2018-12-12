from saboteurs import find_logical_saboteurs

# NOTE: the teo definitions below could also be read from a CSV:
# groups, failed_groups = csv_to_groups_data('find_logical_saboteurs.csv')

groups = {
    1: ['A', 'C', 'D'],
    2: ['B', 'C', 'E'],
    3: ['A', 'B', 'D'],
    4: ['D', 'F', 'G']
}
failed_groups = [2, 4]

result = find_logical_saboteurs(groups, failed_groups=failed_groups)
print (result)