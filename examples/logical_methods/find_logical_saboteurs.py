from saboteurs import find_logical_saboteurs

groups = {
    1: ['A', 'C', 'D'],
    2: ['B', 'C', 'E'],
    3: ['A', 'B', 'D'],
    4: ['D', 'F', 'G']
}
result = find_logical_saboteurs(groups, failed_groups=[2, 4])
print (result)