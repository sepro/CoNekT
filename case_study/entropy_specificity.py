from planet import create_app
from planet.models.expression_profiles import ExpressionProfile
from planet.models.expression_specificity import ExpressionSpecificity, ExpressionSpecificityMethod

from sqlalchemy.orm import joinedload

app = create_app('config')

with app.app_context():
    profiles = ExpressionProfile.query.all()
    methods = ExpressionSpecificityMethod.query.all()

    with open("./data/entropy_specificity_full.txt", "w") as f_out:
        for m in methods:
            for p in profiles:
                if m.species_id == p.species_id:
                    s = p.specificities.filter(ExpressionSpecificity.method_id == m.id).order_by(ExpressionSpecificity.score.desc()).first()
                    if s is not None:
                        spm = s.score
                        method = s.method.description
                        condition = s.condition
                        print(p.id, p.probe, p.sequence.name if p.sequence is not None else None, p.species.name, p.entropy, spm, condition, method, sep='\t', file=f_out)