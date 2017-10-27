from flask import Blueprint, current_app, Response, redirect, url_for, request, render_template, flash
from sqlalchemy.sql.expression import func

from conekt import blast_thread
from conekt.models.sequences import Sequence
from conekt.forms.blast import BlastForm

import os
import json
import random
import string
from collections import OrderedDict
from time import sleep

blast = Blueprint('blast', __name__)


@blast.route('/', methods=['GET', 'POST'])
def blast_main():
    """
    Main blast interface

    GET request: the html with the blast form will be returned
    POST requests: the input will be validated and the blast will be started
    """
    form = BlastForm(request.form)
    form.populate_blast_types()
    
    if request.method == 'POST' and form.validate():
        blast_type = request.form.get('blast_type')
        fasta = request.form.get('fasta')

        token = ''.join([random.choice(string.ascii_letters) for _ in range(18)])
        file_in = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.in')
        file_out = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.out')

        with open(file_in, 'w') as f:
            print(fasta, file=f)

        blast_thread.add_job(blast_type, file_in, file_out)

        return redirect(url_for('blast.blast_results', token=token))

    if form.errors:
        flash(form.errors, 'danger')

    # select example from the database
    sequence = Sequence.query.filter(Sequence.type == 'protein_coding')\
        .filter(func.length(Sequence.coding_sequence) > 300).first()

    example = {
        'blast_type': 'blastp',
        'fasta': sequence.protein_sequence if sequence is not None else None
    }

    return render_template('blast.html', form=form, example=example)


@blast.route('/results/<token>')
def blast_results(token):
    """
    Renders the blast results for a given token

    :param token: code for the generated results
    :return: page containing the blast results
    """
    return render_template('blast.html', token=token)


@blast.route('/results/json/<token>')
def blast_results_json(token):
    """
    Returns a json file with the status of the blast and the results in case it is completed

    :param token: code for the generated results
    :return: json object with the blast status and results
    """
    file_results = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.out')
    file_in = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.in')
    columns = ['query', 'hit', 'percent_identity', 'alignment_length', 'num_mismatch',
               'num_gaps', 'q_start', 'q_end', 'h_start', 'h_end', 'e_value', 'bit_score']

    # Check if output exists and is writeable (which indicates the move is completed... i hope)
    if os.path.exists(file_results) and os.access(file_results, os.W_OK):
        # sleep(0.2) #might be necessary in case the os.access doesn't do the trick
        output = []

        with open(file_results) as f:
            for line in f:
                output.append(OrderedDict(zip(columns, line.split())))

        return Response(json.dumps({'status': 'done', 'data': output}), mimetype='application/json')
    else:
        if not os.path.exists(file_in):
            return Response(json.dumps({'status': 'error',
                                        'message': 'An error occurred. Error with input or results expired'}),
                            mimetype='application/json')
        else:
            return Response(json.dumps({'status': 'waiting'}), mimetype='application/json')
