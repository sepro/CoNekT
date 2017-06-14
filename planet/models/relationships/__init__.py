from planet import db

sequence_go = db.Table('sequence_go',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                       db.Column('go_id', db.Integer, db.ForeignKey('go.id'), index=True)
                       )

sequence_interpro = db.Table('sequence_interpro',
                             db.Column('id', db.Integer, primary_key=True),
                             db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                             db.Column('interpro_id', db.Integer, db.ForeignKey('interpro.id'), index=True),
                             )

sequence_family = db.Table('sequence_family',
                           db.Column('id', db.Integer, primary_key=True),
                           db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                           db.Column('gene_family_id', db.Integer, db.ForeignKey('gene_families.id'), index=True)
                           )

sequence_coexpression_cluster = \
    db.Table('sequence_coexpression_cluster',
             db.Column('id', db.Integer, primary_key=True),
             db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
             db.Column('coexpression_cluster_id', db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True)
             )

coexpression_cluster_similarity = \
    db.Table('coexpression_cluster_similarity',
             db.Column('id', db.Integer, primary_key=True),
             db.Column('source_id', db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True),
             db.Column('target_id', db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True)
             )

sequence_xref = db.Table('sequence_xref',
                         db.Column('id', db.Integer, primary_key=True),
                         db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                         db.Column('xref_id', db.Integer, db.ForeignKey('xrefs.id'), index=True)
                         )

sequence_sequence_ecc = db.Table('sequence_sequence_ecc',
                                 db.Column('id', db.Integer, primary_key=True),
                                 db.Column('query_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                                 db.Column('target_id', db.Integer, db.ForeignKey('sequences.id'), index=True)
                                 )

sequence_sequence_clade = db.Table('sequence_sequence_clade',
                                   db.Column('id', db.Integer, primary_key=True),
                                   db.Column('sequence_one_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                                   db.Column('sequence_two_id', db.Integer, db.ForeignKey('sequences.id'), index=True)
                                   )

family_xref = db.Table('family_xref',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('gene_family_id', db.Integer, db.ForeignKey('gene_families.id'), index=True),
                       db.Column('xref_id', db.Integer, db.ForeignKey('xrefs.id'), index=True)
                       )

cluster_go_enrichment = db.Table('cluster_go_enrichment',
                                 db.Column('id', db.Integer, primary_key=True),
                                 db.Column('cluster_id', db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True),
                                 db.Column('go_id', db.Integer, db.ForeignKey('go.id'), index=True)
                                 )


