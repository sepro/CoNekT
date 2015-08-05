from flask import Blueprint, render_template
from flask.ext.login import current_user


main = Blueprint('main', __name__)


@main.route('/')
def screen():
    """
    Shows the main screen
    """
    return render_template('main.html')

