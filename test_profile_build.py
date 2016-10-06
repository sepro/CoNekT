from planet import create_app
annotation = {}

with open('./data/LSTrAP/ath/runs_description.txt', 'r') as fin:
    # get rid of the header
    _ = fin.readline()

    for line in fin:
        parts = line.strip().split('\t')
        if len(parts) > 1:
            run, description = parts
            annotation[run] = description

order, colors = [], []

with open('./data/LSTrAP/ath/runs_order_color.txt', 'r') as fin:
    for line in fin:
        o, c = line.strip().split('\t')
        order.append(o)
        colors.append(c)


app = create_app('config')

with app.app_context():
    from build.db.expression_profile import add_profile_from_lstrap
    add_profile_from_lstrap('./data/LSTrAP/ath/matrix.tpm.txt', annotation, 'ath', order=order, colors=colors)