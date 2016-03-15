from planet import create_app

from build.db.species import add_species_from_fasta
from build.db.go import add_go_from_plaza
from build.db.go import populate_go
from build.db.interpro_xml import populate_interpro
from build.db.interpro_data import add_interpro_from_plaza
from build.db.families import add_families_from_plaza
from build.db.expression import parse_expression_plot
from build.db.expression import parse_expression_network
from build.db.coexpression_clusters import add_planet_coexpression_clusters
from build.db.xref import create_plaza_xref_families, create_plaza_xref_genes

from planet.models.coexpression_clusters import CoexpressionClusteringMethod,CoexpressionCluster
from planet.models.expression_networks import ExpressionNetworkMethod
from planet.models.gene_families import GeneFamilyMethod
from planet.models.species import Species
from planet.models.clades import Clade
from planet.models.go import GO

from planet.ftp import export_ftp_data

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
        'id': None,
        'network_id': None
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
        'id': None,
        'network_id': None
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
        'id': None,
        'network_id': None
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
        'id': None,
        'network_id': None
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
        'id': None,
        'network_id': None
    }
}


with app.app_context():
    # print("Adding species")
    # print("==============")
    #
    # for species, data in SPECIES.items():
    #     print("\tAdding", species)
    #     data['id'] = add_species_from_fasta(data['fasta'], data['code'], species)
    #
    # print("Populating GO and InterPro")
    # print("==========================")
    # populate_go("data/go.obo")
    # populate_interpro("data/interpro.xml")
    #
    # print("Adding Functional Annotation")
    # print("============================")
    # for species, data in SPECIES.items():
    #     if 'go' in data.keys():
    #         add_go_from_plaza(data['go'])
    #
    #     if 'interpro' in data.keys():
    #         add_interpro_from_plaza(data['interpro'])
    #
    # print("Adding Families")
    # print("===============")
    # families_id = add_families_from_plaza("data/genefamily_data.hom.csv", "PLAZA 3.0 Homologous gene families")
    #
    # print("Adding Expression Plots")
    # print("=======================")
    # for species, data in SPECIES.items():
    #     if 'profile' in data.keys() and 'profile_conversion' in data.keys():
    #         parse_expression_plot(data['profile'], data['profile_conversion'], data['code'])
    #
    #
    # print("Adding Expression Networks")
    # print("==========================")
    # for species, data in SPECIES.items():
    #     if 'network_description' in data.keys() and 'network' in data.keys():
    #         data['network_id'] = parse_expression_network(data['network'], data['code'], data['network_description'])

    #
    # print("Adding Coexpression Clusters")
    # print("============================")
    # add_planet_coexpression_clusters("data/GmaPfamPlazaGO.hrr", "data/Gma.S=3R=30.hcca",
    #                                  "Glycine max clusters PlaNet 1", soy_network_id)
    # add_planet_coexpression_clusters("data/AthPfamPlazaGO.hrr", "data/Ath.S=3R=30.hcca",
    #                                  "Arabidopsis thaliana clusters PlaNet 1", ath_network_id)
    # add_planet_coexpression_clusters("data/mtr/MtrPfamPlazaGO.clean.hrr", "data/mtr/Mtr.S=3R=30.hcca",
    #                                  "Medicago truncatula clusters PlaNet 1", mtr_network_id)
    #
    #
    # print("Precalculating big counts")
    # print("=========================")
    # CoexpressionClusteringMethod.update_counts()
    # ExpressionNetworkMethod.update_count()
    # GeneFamilyMethod.update_count()
    # Species.update_counts()
    # GO.update_species_counts()
    #
    # print("Adding clades and assigning them to gene families")
    # print("=================================================")
    # for c, data in CLADES.items():
    #     Clade.add_clade(c, data['species'], data['tree'])

    #
    Clade.update_clades()
    #
    # print("Calculate GO enrichment for clusters and similarities")
    # print("=====================================================")
    # CoexpressionCluster.calculate_enrichment()
    # CoexpressionCluster.calculate_similarities(gene_family_method_id=families_id)
    #
    # print("Calculate ECC scores for homologous genes")
    # print("=====================================================")
    # ExpressionNetworkMethod.calculate_ecc([soy_network_id, ath_network_id, mtr_network_id], families_id)
    #
    # print("Adding XRefs")
    # print("============")
    # create_plaza_xref_genes(ath_id)
    # create_plaza_xref_genes(ptr_id)
    # create_plaza_xref_families(families_id)
    #
    # print("Building FTP data")
    # print("=================")
    # export_ftp_data()

