from collections import OrderedDict

def csv_to_groups_data(csv_path=None, csv_string=None):
    """Read a CSV to get the data to feed to ``find_statistical_saboteurs()``
    or ``find_logical_saboteurs()``.

    See examples of such a file in the code repository:

    https://github.com/Edinburgh-Genome-Foundry/saboteurs/

    Returns
    -------
    groups, failed_groups
      For datasheets for logical saboteur finding.


    group_data
      For datasheets for statistical saboteur finding. The data is of the form
      
      >>> {"Exp. 1": {
      >>>      exp_id: "Exp. 1",
      >>>     attempts: 7,
      >>>     failures: 10,
      >>>     members: ["Alice", "Bob"]}
      >>>  }
      >>>  "Exp. 2": { etc...
    """
    if csv_string is None:
         with open(csv_path, 'r') as f:
             csv_string = f.read()
    lines = [[e.strip() for e in l.split(',') if len(e.strip())]
                for l in csv_string.split('\n') if len(l)]
    groups = OrderedDict([])
    if 'result' in lines[0]:
        failed_groups = []
        for line in lines[1:]:
            name, result, members = line[0], line[1], line[2:]
            groups[name] = members
            if result != 'success':
                failed_groups.append(name)
        return groups, failed_groups
    else:
        for line in lines[1:]:
            (name, attempts, failures), members = line[:3], line[3:]
            groups[name] = dict(id=name, attempts=int(attempts),
                                failures=int(failures), members=members)
        return groups