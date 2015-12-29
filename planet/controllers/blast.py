from flask import Blueprint, current_app, Response, redirect, url_for

from planet import blast_thread

import os
import json
import random
import string

blast = Blueprint('blast', __name__)


@blast.route('/', methods=['GET', 'POST'])
def blast_main():
    token = ''.join([random.choice(string.ascii_letters) for _ in range(18)])
    file_in = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.in')
    file_out = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.out')

    blast_thread.add_job('blastp', file_in, file_out)

    return redirect(url_for('blast.blast_results', token=token))


@blast.route('/results/<token>')
def blast_results(token):
    return token


@blast.route('/queue')
def blast_queue():
    return list(blast_thread.queue)


@blast.route('/results/json/<token>')
def blast_results_json(token):
    filename = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.out')
    columns = ["query", "hit", "percent_identity", "alignment_length", "num_mismatch",
               "num_gaps", "q_start", "q_end", "h_start", "h_end", "e_value", "bit_score"]

    if os.path.exists(filename):
        output = []
        with open(filename) as f:
            for line in f:
                output.append(dict(zip(columns, line.split())))
        return Response(json.dumps({'status': 'done', 'data': output}), mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'waiting'}), mimetype='application/json')
