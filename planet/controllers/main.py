from flask import Blueprint, render_template, current_app, redirect, g, flash, url_for

from planet.models.news import News

main = Blueprint('main', __name__)


@main.route('/')
def screen():
    """
    Shows the main screen
    """

    keyword_examples = current_app.config['KEYWORD_EXAMPLES'] if'KEYWORD_EXAMPLES' in current_app.config.keys() else None

    news = News.query.order_by(News.posted.desc()).limit(5)

    return render_template('static_pages/main.html', news=news, keyword_examples=keyword_examples)


@main.route('/features')
def features():
    """
    Shows overview of features
    """
    return render_template('static_pages/features.html')


@main.route('/about')
def about():
    """
    Shows the about page
    """
    return render_template('static_pages/about.html')


@main.route('/contact')
def contact():
    """
    Shows the about contact
    """
    return render_template('static_pages/contact.html')


@main.route('/disclaimer')
def disclaimer():
    """
    Shows the disclaimer
    """
    return render_template('static_pages/disclaimer.html')


@main.route('/privacy')
def privacy_policy():
    """
    Shows the privacy policy
    """
    if g.imprint is not None:
        return redirect(g.privacy)
    else:
        flash("No Privacy Policy URL defined", "warning")
        redirect(url_for("main.main"))


@main.route('/imprint')
def imprint():
    if g.imprint is not None:
        return redirect(g.imprint)
    else:
        flash("No Imprint URL defined", "warning")
        redirect(url_for("main.main"))
