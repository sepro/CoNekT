from flask import g, Blueprint, flash, redirect, url_for, render_template, request

from planet.models.species import Species

species = Blueprint('species', __name__)

@species.route('/')
def species_overview():
    return "TEST OK"

@species.route('/view/<species_id>')
def species_view(species_id):
    current_species = Species.query.get_or_404(species_id)

    print(current_species.sequences.count())

    return render_template('species.html', species=current_species)
