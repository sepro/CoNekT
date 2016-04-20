import os


def check_sanity_species_data(data, name=''):
    required_keys = ['code', 'fasta', 'go', 'interpro', 'profile', 'profile_conversion', 'network',
                     'network_description', 'clusters', 'clusters_description']

    required_paths = ['fasta', 'go', 'interpro', 'profile', 'profile_conversion', 'network', 'clusters']

    if not all([r in data.keys() for r in required_keys]):
        for r in required_keys:
            if r not in data.keys():
                print('[', name, ']', 'Key', r, 'missing')
        return False

    if not all([data[r] is None or os.path.exists(data[r]) for r in required_paths]):
        for r in required_paths:
            if data[r] is not None and not os.path.exists(data[r]):
                print('[', name, ']', 'Problem with path in', r)
        return False

    return True