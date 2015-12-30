from flask import Blueprint, current_app, Response, redirect, url_for, request, render_template

from planet import blast_thread
from planet.forms.blast import BlastForm

import os
import json
import random
import string
from collections import OrderedDict

blast = Blueprint('blast', __name__)


@blast.route('/', methods=['GET', 'POST'])
def blast_main():
    form = BlastForm(request.form)
    form.populate_blast_types()
    
    if request.method == 'POST' and form.validate():
        token = ''.join([random.choice(string.ascii_letters) for _ in range(18)])
        file_in = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.in')
        file_out = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.out')

        with open(file_in, 'w') as f:
            print('>Input1', file=f)
            print("""MATFDHEHRHSSPAKICRVCGDEVKDNDNGQTFVACHVCAYPVCKPCYEYERSNGNKCCPQCNTIYKRHKGSPKIVGDEENNGPDDSDDELNIKNRQDAS
    SIHQNFAYGSENGDYNSKQQWRPNGRAFSSTGSVLGKDFEAERDGYTDAEWKERVDKWKARQEKRGLVTKGEQTNEDKEDDEEEYLDAEARQPLWRKVPI
    SSSKISPYRIVIVLRLVILVFFFRFRILTPAKDAYPLWLISVICEIWFALSWILDQFPKWFPINRETYLDRLSMRFERDGEKNKLEPVDVFVSTVDPLKE
    PPIITANTILSILSVDYPVNKVSCYVSDDGASMLLFDTLSETSEFARRWVPFCKKYNVEPRAPEFYFSEKIDYLKDKVQTTFVKDRRAMKREYEEFKVRI
    NALVAKAQKKPEEGWVMQDGTPWPGNNTRDHPGMIQVYLGKEGAFDIDGNELPRLVYVSREKRPGYAHHKKAGAMNAMVRVSAVLTNAPFMLNLDCDHYI
    NNSKAIRESMCFLMDPQLGKKLCYVQFPQRFDGIDHNDRYANRNIVFFDINMRGLDGIQGPVYVGTGCVFNRPALYGYEPPVSEKRKKMTCDCWPSWICC
    CCGGGNRNHKSKSSESSKKKSGIKSLFSKLKKKNKKKSDTTTTMSSYSRKRSSTEAIFDLEDIEEGLEGYDELEKSSLMSQKNFEKRFGMSPVFIASTLM
    ENGGLPEATNTSSLIKEAIHVISCGYEEKTEWGKEIGWIYGSVTEDILTGFRMHCRGWKSVYCMPKRPAFKGSAPINLSDRLHQVLRWALGSVEIFFSRH
    CPLWYAWGGKLKILERLAYINTIVYPFTSIPLLAYCTIPAVCLLTGKFIIPTINNFASIWFLALFLSIIATAILELRWSGVSINDLWRNEQFWVIGGVSA
    HLFAVFQGLLKVLFGVDTNFTVTSKGASDEADEFGDLYLFKWTTLLIPPTTLIILNMVGVVAGVSDAINNGYGSWGPLFGKLFFAFWVIVHLYPFLKGLM
    GRQNRTPTIVVLWSILLASIFSLVWVRIDPFLPKQTGPLLKQCGVDC*""", file=f)

        blast_thread.add_job('blastp', file_in, file_out)

        return redirect(url_for('blast.blast_results', token=token))
    else:
        return render_template('blast.html', form=form)


@blast.route('/results/<token>')
def blast_results(token):
    return render_template('blast.html', token=token)


@blast.route('/results/json/<token>')
def blast_results_json(token):
    file_results = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.out')
    file_in = os.path.join(current_app.config['BLAST_TMP_DIR'], token + '.in')
    columns = ['query', 'hit', 'percent_identity', 'alignment_length', 'num_mismatch',
               'num_gaps', 'q_start', 'q_end', 'h_start', 'h_end', 'e_value', 'bit_score']

    if not os.path.exists(file_in):
        return Response(json.dumps({'status': 'error',
                                    'message': 'An error occurred. Most likely the results expired'}),
                        mimetype='application/json')

    if os.path.exists(file_results):
        output = []

        with open(file_results) as f:
            for line in f:
                output.append(OrderedDict(zip(columns, line.split())))

        return Response(json.dumps({'status': 'done', 'data': output}), mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'waiting'}), mimetype='application/json')
