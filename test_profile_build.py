from planet import create_app

app = create_app('config')

with app.app_context():
    from planet.models.species import Species
    from planet.models.expression_profiles import ExpressionProfile

    species = Species.query.filter_by(code='ath').first()

    ExpressionProfile.add_profile_from_lstrap('./data/LSTrAP/ath/matrix.tpm.txt',
                                              './data/LSTrAP/ath/runs_description.txt',
                                              species.id,
                                              order_color_file='./data/LSTrAP/ath/runs_order_color.txt'
                                              )
