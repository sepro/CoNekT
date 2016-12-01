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
    'Arabidopsis thaliana': {
        'code': 'ath',
        'fasta': 'data/cds/cds.ath.tfa',
        'go': 'data/go/go.ath.csv',
        'interpro': 'data/interpro/interpro.ath.csv',
        'profile': 'data/profiles/Ath.plot.txt',
        'profile_conversion': 'data/profiles/ath_probe_conversion.txt',
        'network': 'data/hrr/AthPfamPlazaGO.clean.hrr',
        'network_description': 'HQ Network for Arabidopsis thaliana',
        'clusters': 'data/hrr/Ath.S=3R=50.hcca',
        'clusters_description': 'Ath HCCA',
        'id': 3,
        'network_id': 3
    },
    'Populus trichocarpa': {
        'code': 'ptr',
        'fasta': 'data/cds/cds.ptr.tfa',
        'go': 'data/go/go.ptr.csv',
        'interpro': 'data/interpro/interpro.ptr.csv',
        'profile': 'data/profiles/Ptr.plot.txt',
        'profile_conversion': 'data/profiles/ptr_probe_conversion.txt',
        'network': 'data/hrr/PtrPfamPlazaGO.clean.hrr',
        'network_description': 'HQ Network for Populus trichocarpa',
        'clusters': 'data/hrr/Ptr.S=3R=50.hcca',
        'clusters_description': 'Ptr HCCA',
        'id': 1,
        'network_id': 2,
        'tissues': {"seedlings in light": "seedling",
                    "dark sdlings in 3h light": "seedling",
                    "seedlings in dark": "seedling",
                    "young leaf": "leaf", "mature leaf": "leaf",
                    "root": "root",
                    "xylem": "stem",
                    "female catkins": "female catkins", "male catkins": "male catkins"}
    },
    'Glycine max': {
        'code': 'gma',
        'fasta': 'data/cds/cds.gma.tfa',
        'go': 'data/go/go.gma.csv',
        'interpro': 'data/interpro/interpro.gma.csv',
        'profile': 'data/profiles/Gma.plot.txt',
        'profile_conversion': 'data/profiles/gma_probe_conversion.txt',
        'network': 'data/hrr/GmaPfamPlazaGO.clean.hrr',
        'network_description': 'HQ Network for Glycine max',
        'clusters': 'data/hrr/Gma.S=3R=50.hcca',
        'clusters_description': 'Gma HCCA',
        'id': 5,
        'network_id': 1
    },
    'Medicago truncatula': {
        'code': 'mtr',
        'fasta': 'data/cds/cds.mtr.tfa',
        'go': 'data/go/go.mtr.csv',
        'interpro': 'data/interpro/interpro.mtr.csv',
        'profile': 'data/profiles/Mtr.plot.txt',
        'profile_conversion': 'data/profiles/mtr_probe_conversion.txt',
        'network': 'data/hrr/MtrPfamPlazaGO.clean.hrr',
        'network_description': 'HQ Network for Medicago truncatula',
        'clusters': 'data/hrr/Mtr.S=3R=50.hcca',
        'clusters_description': 'Mtr HCCA',
        'id': 4,
        'network_id': 4
    },
    'Oryza sativa': {
        'code': 'osa',
        'fasta': 'data/cds/cds.osa.tfa',
        'go': 'data/go/go.osa.csv',
        'interpro': 'data/interpro/interpro.osa.csv',
        'profile': 'data/profiles/Osa.plot.txt',
        'profile_conversion': 'data/profiles/osa_probe_conversion.txt',
        'network': 'data/hrr/OsaPfamPlazaGO.clean.hrr',
        'network_description': 'HQ Network for Oryza sativa',
        'clusters': 'data/hrr/Osa.S=3R=50.hcca',
        'clusters_description': 'Osa HCCA',
        'id': 2,
        'network_id': 5,
        'tissues': {
                        "stigma": "spikelet",
                        "Ovary": "spikelet",
                        "Suspension cell": "spikelet",
                        "Shoot": "shoot",
                        "Root": "root",
                        "Anther": "spikelet",
                        "Embryo": "seed",
                        "Endosperm": "seed",
                        "5d-seed": "seed",
                        "Root, 7d Seedling": "root", # remove this one ?
                        "Mature leaf": "leaf",
                        "Y Leaf": "leaf",
                        "SAM": "shoot",
                        "Young inflorescence (P1, upto 3 cm)": "spikelet",
                        "Inflorescence (P2, 3 - 5 cm)": "spikelet",
                        "Inflorescence (P3, 5 - 10 cm)": "spikelet",
                        "Inflorescence (P4, 10 - 15 cm)": "spikelet",
                        "Inflorescence (P5, 15 - 22 cm)": "spikelet",
                        "Inflorescence (P6, 22 - 30 cm)": "spikelet",
                        "Seed (S1, 0 - 2 dap)": "seed",
                        "Seed (S2, 3 - 4 dap)": "seed",
                        "Seed (S3, 5 - 10 dap)": "seed",
                        "Seed (S4, 11 - 20 dap)": "seed",
                        "Seed (S5, 21 - 29 dap)": "seed",
                        "7d Seedling": "seedling",
                        "7d Seedling, Drought stress": "seedling",
                        "7d Seedling, Salt stress": "seedling",
                        "7d Seedling, Cold stress": "seedling",
                        "Coleoptiles, 4 d aerobic": "coleoptile",
                        "Coleoptiles, 4 d anoxic": "coleoptile"}
    },
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
    # import of models need to happen after app is created !
    from build.sanity import check_sanity_species_data

    from build.db.expression import parse_expression_plot
    from build.db.expression import parse_expression_network
    from build.db.coexpression_clusters import add_planet_coexpression_clusters
    from build.db.xref import create_plaza_xref_families

    from planet.models.coexpression_clusters import CoexpressionClusteringMethod,CoexpressionCluster
    from planet.models.expression_networks import ExpressionNetworkMethod
    from planet.models.gene_families import GeneFamilyMethod, GeneFamily
    from planet.models.species import Species
    from planet.models.sequences import Sequence
    from planet.models.clades import Clade
    from planet.models.go import GO
    from planet.models.xrefs import XRef
    from planet.models.interpro import Interpro
    from planet.models.expression_specificity import ExpressionSpecificityMethod
    from planet.models.expression_profiles import ExpressionProfile
    from planet.models.condition_tissue import ConditionTissue

    from planet.ftp import export_ftp_data

    print("Checking input")
    print("==============")

    if not all([check_sanity_species_data(SPECIES[s], name=s) for s in SPECIES.keys()]):
        print("Check failed ... quiting ... bye!")
        quit()
    else:
        print("All checks passed, starting to add data")

    print("Adding species")
    print("==============")

    for species, data in SPECIES.items():
        print("\tAdding", species)
        data['id'] = Species.add(data['code'], species)
        Sequence.add_from_fasta(data['fasta'], data['id'])

    print("Populating GO and InterPro")
    print("==========================")
    GO.add_from_obo("data/go.obo")
    Interpro.add_from_xml("data/interpro.xml")

    print("Adding Functional Annotation")
    print("============================")
    for species, data in SPECIES.items():
        if data['go'] is not None:
            # TODO replace with load from tab
            GO.add_go_from_plaza(data['go'])

        if data['interpro'] is not None:
            # TODO replace with load from interproscan
            Interpro.add_interpro_from_plaza(data['interpro'])

    print("Adding Families")
    print("===============")
    # TODO OBSOLETE
    # families_id = GeneFamily.add_families_from_plaza("data/genefamily_data.hom.csv", "PLAZA 2.5 Homologous gene families")

    print("Adding Expression Plots")
    print("=======================")
    for species, data in SPECIES.items():
        if 'profile' in data.keys() and 'profile_conversion' in data.keys():
            parse_expression_plot(data['profile'], data['profile_conversion'], data['code'])

    print("Adding Expression Networks")
    print("==========================")
    for species, data in SPECIES.items():
        if 'network_description' in data.keys() and 'network' in data.keys():
            data['network_id'] = parse_expression_network(data['network'], data['code'], data['network_description'])

    print("Adding Coexpression Clusters")
    print("============================")
    for species, data in SPECIES.items():
        if all(x in data.keys() for x in ['network', 'clusters', 'network_id', 'clusters_description']):
            add_planet_coexpression_clusters(data['network'],
                                             data['clusters'],
                                             data['clusters_description'],
                                             data['network_id'])

    print("Precalculating big counts")
    print("=========================")
    CoexpressionClusteringMethod.update_counts()
    ExpressionNetworkMethod.update_count()
    GeneFamilyMethod.update_count()
    Species.update_counts()
    GO.update_species_counts()

    print("Adding clades and assigning them to gene families")
    print("=================================================")
    for c, data in CLADES.items():
        Clade.add_clade(c, data['species'], data['tree'])

    Clade.update_clades()
    Clade.update_clades_interpro()

    print("Calculate GO enrichment for clusters and similarities")
    print("=====================================================")
    # CoexpressionCluster.calculate_enrichment()
    # CoexpressionCluster.calculate_similarities(gene_family_method_id=1)

    print("Calculate ECC scores for homologous genes")
    print("=====================================================")
    # ExpressionNetworkMethod.calculate_ecc(list(range(1, 6)), 1)

    print("Calculate conditions specific profiles")
    print("=========================================")
    for s, data in SPECIES.items():
        ExpressionSpecificityMethod.calculate_specificities(data['id'], s + " condition specific profiles", False)
        if 'tissues' in data:
            ExpressionSpecificityMethod.calculate_tissue_specificities(data['id'], s + " tissue specific profiles", data['tissues'], use_max=True, remove_background=False)
            # TODO needs to work with colors and order as well
            # ConditionTissue.add(data['id'], s + " tissue specific profiles", data['tissues'])

    # print("Building FTP data")
    # print("=================")
    # export_ftp_data()

