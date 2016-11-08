from planet import create_app

app = create_app('config')


with app.app_context():
    # from build.db.expression_profile import add_profile_from_lstrap
    #
    # order = []
    # colors = []
    # annotation = {}
    #
    # with open('./data/LSTrAP/ath/runs_description.txt') as fin:
    #     for line in fin:
    #         parts = line.strip().split('\t')
    #         if len(parts) > 1:
    #             annotation[parts[0]] = parts[1]
    #
    # with open('./data/LSTrAP/ath/runs_order_color.txt') as fin:
    #     for line in fin:
    #         o, c = line.strip().split('\t')
    #         order.append(o)
    #         colors.append(c)
    #
    # add_profile_from_lstrap('./data/LSTrAP/ath/matrix.tpm.txt', annotation, 'ath', order=order, colors=colors)

    # from build.db.expression import read_expression_network_lstrap
    # from build.db.coexpression_clusters import add_lstrap_coexpression_clusters
    #
    # # network_method_id = read_expression_network_lstrap('./data/LSTrAP/ath/pcc.table.txt', 'ath', 'LSTrAP Arabidopsis thaliana co-expression network')
    # network_method_id = 11
    #
    # add_lstrap_coexpression_clusters('./data/LSTrAP/ath/mcl.clusters.txt', 'LSTrAP Arabidopsis thaliana coexpression clusters', network_method_id)
    from planet.models.expression_specificity import ExpressionSpecificityMethod

    ExpressionSpecificityMethod.calculate_specificities(3, 'Arabidopsis thaliana RNA-Seq conditions2', False)