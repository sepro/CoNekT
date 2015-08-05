from flask import g, Blueprint, flash, redirect, url_for, render_template, request


from planet.models.go import GO

go = Blueprint('go', __name__)

@go.route('/')
def go_overview():
    return redirect(url_for('main.screen'))

@go.route('/view/<go_id>')
def go_view(go_id):
    current_go = GO.query.get_or_404(go_id)

    return render_template('go.html', go=current_go)
