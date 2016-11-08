from planet import create_app

app = create_app('config')


CLADES = {
    'Arabidopsis': {
        'species': ['ath'],
        'tree': None
    },
    'Poplar': {
        'species': ['ptr'],
        'tree': None
    },
    'Soybean': {
        'species': ['gma'],
        'tree': None
    },
    'Medicago': {
        'species': ['mtr'],
        'tree': None
    },
    'Rice': {
        'species': ['osa'],
        'tree': None
    },
    'Legumes': {
        'species': ['mtr', 'gma'],
        'tree': '(mtr:0.01, gma:0.01);'
    },
    'Fabids': {
        'species': ['mtr', 'gma', 'ptr'],
        'tree': '((mtr:0.01, gma:0.01):0.01, ptr:0.02);'
    },
    'Rosids': {
        'species': ['mtr', 'gma', 'ptr', 'ath'],
        'tree': '(((mtr:0.01, gma:0.01):0.01, ptr:0.02):0.01, ath:0.03);'
    },
    'Angiosperms': {
        'species': ['mtr', 'gma', 'ptr', 'ath', 'osa'],
        'tree': '((((mtr:0.01, gma:0.01):0.01, ptr:0.02):0.01, ath:0.03):0.01, osa:0.04);'
    },
}

SPECIES = {
    'Brachypodium distachyon': {
        'code': 'bdi',
        'fasta': 'data/cds/bdi.clean.tfa',
        'go': None,
        'interpro': None,
        'profile': 'data/profiles/Bdi.plot.txt',
        'profile_conversion': 'data/profiles/bdi_probe_conversion.txt',
        'network': 'data/hrr/BdiPfamPlazaGO.hrr',
        'network_description': 'HQ Network for Brachypodium distachyon',
        'clusters': 'data/hrr/Bdi.S=3R=30.hcca',
        'clusters_description': 'Bdi HCCA',
        'id': 6,
        'network_id': None,
        'tissues': {
            "P: Coleoptile (10 DAG)": "coleoptile",
            "G: Lower node, tips of adventitious root are detectable (35 DAG)": "node",
            "G: Young spikelets": "spikelet",
            "P: First internode (17 DAG)": "internode",
            "G: Third 2 cm of peduncle": "peduncle",
            "J: Mature leaves, fully expanded (60 DAG)": "leaf",
            "G: Internode (35 DAG)": "internode",
            "G: Endosperm (31 DAF)": "seed",
            "P: Leaf (17 DAG)": "leaf",
            "G: Endosperm (11 DAF)": "seed",
            "G: Last spikelet internode": "spikelet",
            "G: Top part of inclined node (45 deg)": "node",
            "G: Whole grain (31 DAF)": "seed",
            "G: Spikelet peduncle": "peduncle",
            "P: Mesocotyl (60 DAG)": "mesocotyl",
            "P: Shoots in the dark (3 days old)": "shoot",
            "P: Young spikelets (3 DAF)": "spikelet",
            "P: Leaf (60 DAG)": "leaf",
            "P: Coleoptile (17+27 DAG pooled)": "coleoptile",
            "G: Mature root system (35 DAG)" : "root",
            "G: Bottom part of inclined node (45 deg)": "node",
            "G: First spikelet internode": "spikelet",
            "J: Young leaves < 6 cm (60 DAG)": "leaf",
            "P: First internode (27 DAG)": "internode",
            "P: Roots (10 DAG)": "root",
            "P: De-etiolated shoots (3 days old)": "shoot",
            "G: Last 2 cm of peduncle": "peduncle",
            "G: Mesocotyl (35 DAG)": "mesocotyl",
            "G: Dry whole seeds (2 years old)": "seed",
            "P: First node (17 DAG)": "node",
            "P: First node (10 DAG)": "node",
            "G: Upper node (35 DAG)": "node",
            "G: Whole grain (11 DAF)": "seed",
            "P: Internode (60 DAG)": "internode",
            "J: First lignified internodes at the basis of culms (60 DAG)": "internode",
            "P: First node (60 DAG)": "node",
            "P: Mesocotyl (10 DAG)": "mesocotyl",
            "J: First internodes at the top of culms (60 DAG)": "internode",
            "P: Leaf (27 DAG)": "leaf",
            "G: Second 2 cm of peduncle": "peduncle",
            "P: Mesocotyl (17 DAG)": "mesocotyl",
            "G: First 2 cm of peduncle": "peduncle",
            "P: Mesocotyl (27 DAG)": "mesocotyl",
            "P: First node (27 DAG)": "node",
            "P: Leaf (10 DAG)": "leaf"}
        }
}


with app.app_context():
    from build.sanity import check_sanity_species_data

    from build.db.expression import parse_expression_plot
    from build.db.expression import parse_expression_network
    from build.db.coexpression_clusters import add_planet_coexpression_clusters
    from build.db.xref import create_plaza_xref_families

    from planet.models.coexpression_clusters import CoexpressionClusteringMethod,CoexpressionCluster
    from planet.models.expression_networks import ExpressionNetworkMethod
    from planet.models.gene_families import GeneFamilyMethod
    from planet.models.species import Species
    from planet.models.clades import Clade
    from planet.models.go import GO
    from planet.models.expression_specificity import ExpressionSpecificityMethod
    from planet.models.expression_profiles import ExpressionProfile
    from planet.models.condition_tissue import ConditionTissue

    from planet.ftp import export_ftp_data
    for s, data in SPECIES.items():
        ExpressionSpecificityMethod.calculate_specificities(data['id'], s + " condition specific profiles")
        if 'tissues' in data:
            # ExpressionSpecificityMethod.calculate_tissue_specificities(data['id'], s + " tissue specific profiles (new version, no background)", data['tissues'], remove_background=True)
            # ExpressionSpecificityMethod.calculate_tissue_specificities(data['id'], s + " tissue specific profiles", data['tissues'], use_max=True, remove_background=True)
            # ConditionTissue.add(data['id'], s + " tissue specific profiles", data['tissues'])
            pass

