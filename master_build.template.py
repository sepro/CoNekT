from build.species import add_species_from_fasta
from build.go import add_go_from_plaza
from build.go import populate_go
from build.interpro_xml import populate_interpro
from build.interpro_data import add_interpro_from_plaza
from build.families import add_families_from_plaza
from build.expression import parse_expression_plot
from build.expression import parse_expression_network
from build.coexpression_clusters import add_planet_coexpression_clusters
from build.xref import create_plaza_xref_families, create_plaza_xref_genes

from planet.models.coexpression_clusters import CoexpressionClusteringMethod
from planet.models.expression_networks import ExpressionNetworkMethod
from planet.models.gene_families import GeneFamilyMethod
from planet.models.species import Species
from planet.models.clades import Clade

from planet.ftp import export_ftp_data

print("Adding species")
print("==============")
print("\tArabidopsis thaliana")
ath_id = add_species_from_fasta("data/ath/cds.ath.tfa", "ath", "Arabidopsis thaliana")
print("\tPopulus trichocarpa")
ptr_id = add_species_from_fasta("data/ptr/cds.ptr.tfa", "ptr", "Populus trichocarpa")
print("\tGlycine max")
gma_id = add_species_from_fasta("data/gmax.jgi.cds.fasta", "gma", "Glycine max")

print("Populating GO and InterPro")
print("==========================")
populate_go("data/go.obo")
populate_interpro("data/interpro.xml")

print("Adding Functional Annotation")
print("============================")
add_go_from_plaza("data/ath/go.ath.csv")
add_go_from_plaza("data/ptr/go.ptr.csv")

add_interpro_from_plaza("data/ath/interpro.ath.csv")
add_interpro_from_plaza("data/ptr/interpro.ptr.csv")

print("Adding Families")
print("===============")
families_id = add_families_from_plaza("data/genefamily_data.hom.csv", "PLAZA 3.0 Homologous gene families")

print("Adding Expression Plots")
print("=======================")
parse_expression_plot("data/Ath.plot.txt", "data/AthPfamPlazaGO.hrr", "ath")
parse_expression_plot("data/Gma.plot.txt", "data/GmaPfamPlazaGO.hrr", "gma")

print("Adding Expression Networks")
print("==========================")
soy_network_id = parse_expression_network("data/GmaPfamPlazaGO.hrr", "gma", "Glycine max network from PlaNet 1")
ath_network_id = parse_expression_network("data/AthPfamPlazaGO.hrr", "ath", "Arabidopsis thaliana network from PlaNet 1")

print("Adding Coexpression Clusters")
print("============================")
add_planet_coexpression_clusters("data/GmaPfamPlazaGO.hrr", "data/Gma.S=3R=30.hcca",
                                 "Glycine max clusters PlaNet 1", soy_network_id)
add_planet_coexpression_clusters("data/AthPfamPlazaGO.hrr", "data/Ath.S=3R=30.hcca",
                                 "Arabidopsis thaliana clusters PlaNet 1", ath_network_id)

print("Precalculating big counts")
print("=========================")
CoexpressionClusteringMethod.update_counts()
ExpressionNetworkMethod.update_count()
GeneFamilyMethod.update_count()
Species.update_counts()

print("Adding clades and assigning them to gene families")
print("=================================================")
Clade.add_clade('Arabidopsis', ['ath'])
Clade.add_clade('Poplar', ['ptr'])
Clade.add_clade('Soy', ['gma'])
Clade.add_clade('Fabids', ['ptr', 'gma'])
Clade.add_clade('Dicots', ['ath', 'ptr', 'gma'])

Clade.update_clades()

print("Adding XRefs")
print("============")
create_plaza_xref_genes(ath_id)
create_plaza_xref_genes(ptr_id)
create_plaza_xref_families(families_id)


print("Building FTP data")
print("=================")
export_ftp_data()

