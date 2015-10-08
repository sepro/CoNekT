from planet import db
from planet.models.sequences import Sequence
from planet.models.gene_families import GeneFamily, GeneFamilyMethod

from build.parser.plaza.families import Parser as FamilyParser


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
