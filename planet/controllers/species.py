from flask import Blueprint, render_template

from planet.models.species import Species


species = Blueprint('species', __name__)


@species.route('/')
def species_overview():
    """
    Overview of all species with data in the current database, including some basic statistics
    """
    all_species = Species.query.all()

    return render_template('species.html', all_species=all_species)


@species.route('/view/<species_id>')
def species_view(species_id):
    """
    Get a species based on the ID and show the details for this species

    :param species_id: ID of the species to show
    """
    current_species = Species.query.get_or_404(species_id)

    return render_template('species.html', species=current_species)