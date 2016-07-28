from planet import create_app
from planet.models.expression_profiles import ExpressionProfile
from planet.models.expression_specificity import ExpressionSpecificity, ExpressionSpecificityMethod

from sys import argv


def write_entropy_specificity(method_id, filename):
    """
    Dumps the spm values and corresponding entropy value for a given profile

    :param method_id: Method ID of the method used to calculate the spm value (Table expression_specificity_method)
    :param filename: file to write output to
    """
    app = create_app('config')

    with app.app_context():
        profiles = ExpressionProfile.query.all()
        m = ExpressionSpecificityMethod.query.get(method_id)

        with open(filename, "w") as f_out:
            for p in profiles:
                if m.species_id == p.species_id:
                    s = p.specificities.filter(ExpressionSpecificity.method_id == method_id).order_by(ExpressionSpecificity.score.desc()).first()
                    if s is not None:
                        spm = s.score
                        method = s.method.description
                        condition = s.condition
                        print(p.id, p.probe, p.sequence.name if p.sequence is not None else None, p.species.name, p.entropy, spm, condition, method, sep='\t', file=f_out)


if __name__ == "__main__":
    write_entropy_specificity(int(argv[1]), argv[2])