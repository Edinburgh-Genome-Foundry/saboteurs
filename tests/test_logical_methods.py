import os
from saboteurs import (find_logical_saboteurs,
                       generate_combinatorial_groups,
                       design_test_batch,
                       csv_to_groups_data,
                       generate_batch_report)

def test_find_logical_saboteurs():
    groups = {
        1: ['A', 'C', 'D'],
        2: ['B', 'C', 'E'],
        3: ['A', 'B', 'D'],
        4: ['D', 'F', 'G']
    }
    result = find_logical_saboteurs(groups, failed_groups=[2, 4])
    assert result['saboteurs'] == ['E']
    assert sorted(result['suspicious']) == ['F', 'G']

def test_find_logical_saboteurs_from_csv():
    csv_path = os.path.join('tests', 'data', "logical.csv")
    groups, failed_groups = csv_to_groups_data(csv_path)
    result = find_logical_saboteurs(groups, failed_groups=failed_groups)
    assert result['saboteurs'] == ['E']
    assert sorted(result['suspicious']) == ['F', 'G']

def test_design_test_batch():
    elements_per_position = {
        "Position_1": ['A', 'B', 'C'],
        "Position_2": ['D', 'E', 'F', 'G'],
        "Position_3": ['H', 'I', 'J', 'K'],
        "Position_4": ['L', 'M', 'N'],
    }
    possible_groups = generate_combinatorial_groups(elements_per_position)
    selected_groups, error = design_test_batch(possible_groups,
                                               max_saboteurs=2)
    assert (error is None)
    assert len(selected_groups) == 15
    raw_data = generate_batch_report(selected_groups)
    assert len(raw_data) > 2000