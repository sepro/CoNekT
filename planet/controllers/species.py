from flask import Blueprint, render_template, g, current_app

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
    sequence_count = current_species.sequences.count()

    return render_template('species.html', species=current_species, sequence_count=sequence_count)


@species.route('/sequences/<species_id>/')
@species.route('/sequences/<species_id>/<int:page>')
def species_sequences(species_id, page=1):
    """
    Returns a table with sequences from the selected species

    :param species_id: Internal ID of the species
    :param page: Page number
    """
    sequences = Species.query.get(species_id).sequences.order_by('name').paginate(page,
                                                                                  g.page_items,
                                                                                  False).items

    return render_template('pagination/sequences.html', sequences=sequences)
