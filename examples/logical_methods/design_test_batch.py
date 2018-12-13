from saboteurs import (generate_combinatorial_groups,
                       design_test_batch,
                       generate_batch_report)

elements_per_position = {
    "Position_1": ['A', 'B', 'C'],
    "Position_2": ['D', 'E', 'F', 'G'],
    "Position_3": ['H', 'I', 'J', 'K'],
    "Position_4": ['L', 'M', 'N'],
}
possible_groups = generate_combinatorial_groups(elements_per_position,
                                                prefix='G')
selected_groups, error = design_test_batch(possible_groups, max_saboteurs=2)
generate_batch_report(selected_groups, plot_format='png',
                      target='design_test_batch_report')