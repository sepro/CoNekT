from planet import db
from planet.models.sequences import Sequence
from planet.models.gene_families import GeneFamily, GeneFamilyMethod

from utils.parser.plaza.families import Parser as FamilyParser

import csv
import re


def add_families_from_tab(filename, description, handle_isoforms=True):

    # Create new method for these families
    method = GeneFamilyMethod(description)

    try:
        db.session.add(method)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        quit()

    gene_hash = {}
    all_sequences = Sequence.query.all()

    for sequence in all_sequences:
        gene_hash[sequence.name.lower()] = sequence

        if handle_isoforms:
            gene_id = re.sub('\.\d+$', '', sequence.name.lower())
            gene_hash[gene_id] = sequence

    family_hash = {}

    families = {}
    genes = []

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
                family = row['family']
                gene = row['gene']

                genes.append(gene)

                if family not in families.keys():
                    families[family] = []
                    family_hash[family] = GeneFamily(family)
                    family_hash[family].method_id = method.id

                families[family].append(gene)

    for name, f in family_hash.items():
        db.session.add(f)

    for name, f in family_hash.items():
        for gene in families[name]:
            if gene.lower() in gene_hash.keys():
                gene_hash[gene.lower()].families.append(family_hash[name])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    return method.id


def add_families_from_plaza(filename, description):
    family_parser = FamilyParser()
    family_parser.read(filename)

    method = GeneFamilyMethod(description)

    db.session.add(method)

    gene_hash = {}
    all_sequences = Sequence.query.all()

    for sequence in all_sequences:
        gene_hash[sequence.name] = sequence

    for family, genes in family_parser.families.items():
        new_family = GeneFamily(family)
        new_family.method_id = method.id

        db.session.add(new_family)

        for gene in genes:
            if gene in gene_hash:
                gene_hash[gene].families.append(new_family)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    return method.id
