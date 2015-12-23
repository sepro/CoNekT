from flask import Blueprint, render_template, g, make_response, Response

from planet import db
from planet.models.species import Species
from planet.models.sequences import Sequence

from sqlalchemy.orm import undefer

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


@species.route('/download/coding/<species_id>')
def species_download_coding(species_id):
    """
    Generates a fasta file with all coding sequences for a given species

    :param species_id: Internal ID of the species
    :return: Response with the fasta file
    """
    output = []

    current_species = Species.query.get(species_id)
    sequences = db.engine.execute(db.select([Sequence.__table__.c.name, Sequence.__table__.c.coding_sequence]).
                                  where(Sequence.__table__.c.species_id == current_species.id)).\
        fetchall()

    for (name, coding_sequence) in sequences:
        output.append(">" + name)
        output.append(coding_sequence)

    response = make_response("\n".join(output))
    response.headers["Content-Disposition"] = "attachment; filename=" + current_species.code + ".cds.fasta"

    return response


@species.route('/download/protein/<species_id>')
def species_download_protein(species_id):
    """
    Generates a fasta file with all amino acid sequences for a given species

    :param species_id: Internal ID of the species
    :return: Response with the fasta file
    """
    output = []

    current_species = Species.query.get(species_id)
    sequences = current_species.sequences.options(undefer('coding_sequence')).all()

    for s in sequences:
        if s.type == "protein_coding":
            output.append(">" + s.name)
            output.append(s.protein_sequence)

    response = make_response("\n".join(output))
    response.headers["Content-Disposition"] = "attachment; filename=" + current_species.code + ".aa.fasta"

    return response


@species.route('/stream/coding/<species_id>')
def species_stream_coding(species_id):
    """
    Generates a fasta file with all coding sequences for a given species. However this is send as a streaming
    response (and seems to bring up the download dialog a few seconds faster)

    :param species_id: Internal ID of the species
    :return: Streamed response with the fasta file
    """
    def generate(selected_species):
        sequences = db.engine.execute(db.select([Sequence.__table__.c.name, Sequence.__table__.c.coding_sequence]).
                                      where(Sequence.__table__.c.species_id == selected_species)).\
            fetchall()

        for name, coding_sequence in sequences:
            yield ">" + name + '\n' + coding_sequence + '\n'

    return Response(generate(species_id), mimetype='text/plain')


@species.route('/stream/protein/<species_id>')
def species_stream_protein(species_id):
    """
    Generates a fasta file with all amino acid sequences for a given species. However this is send as a streaming
    response (and seems to bring up the download dialog a few seconds faster)

    :param species_id: Internal ID of the species
    :return: Streamed response with the fasta file
    """
    def generate(selected_species):
        sequences = Sequence.query.options(undefer('coding_sequence')).filter_by(species_id=selected_species).all()

        for s in sequences:
            if s.type == "protein_coding":
                yield ">" + s.name + '\n' + s.protein_sequence + '\n'

    return Response(generate(species_id), mimetype='text/plain')



