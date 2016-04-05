from planet import create_app
from planet.models.expression_profiles import ExpressionProfile
from planet.models.expression_specificity import ExpressionSpecificity

from sqlalchemy.orm import joinedload

app = create_app('config')

with app.app_context():
    profiles = ExpressionProfile.query.all()

    with open("./data/entropy_specificity.txt", "w") as f_out:
        for p in profiles:
            s = p.specificities.filter(ExpressionSpecificity.method.has(description='Condition specificity')).order_by(ExpressionSpecificity.score.desc()).first()
            if s is not None:
                spm = s.score
                method = s.method.description
                condition = s.condition
                print(p.id, p.probe, p.sequence.name if p.sequence is not None else None, p.species.name, p.entropy, spm, condition, method, sep='\t', file=f_out)