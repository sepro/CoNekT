from flask import Blueprint, render_template, g, make_response, Response, Markup
from markdown import markdown

from planet import db, cache
from planet.models.species import Species
from planet.models.sequences import Sequence
from planet.models.clades import Clade

from sqlalchemy.orm import undefer, noload
from sqlalchemy import desc

species = Blueprint('species', __name__)


@species.route('/')
@cache.cached()
def species_overview():
    """
    Overview of all species with data in the current database, including some basic statistics

    Pulls the largest clade defined in Clades from the database (if present) and adds this as the tree to the page
    """
    all_species = Species.query.all()

    largest_clade = Clade.query.order_by(desc(Clade.species_count)).limit(1).first()

    tree = largest_clade.newick_tree if largest_clade is not None else None

    return render_template('species.html', all_species=all_species, species_tree=tree)


@species.route('/view/<species_id>')
@cache.cached()
def species_view(species_id):
    """
    Get a species based on the ID and show the details for this species. The description, which can be markdown is
    converted prior to adding it to the template.

    :param species_id: ID of the species to show
    """
    current_species = Species.query.get_or_404(species_id)

    description = None if current_species.description is None \
        else Markup(markdown(current_species.description, extensions=['markdown.extensions.tables', 'markdown.extensions.attr_list']))

    return render_template('species.html', species=current_species, description=description)


@species.route('/sequences/<species_id>/')
@species.route('/sequences/<species_id>/<int:page>')
@cache.cached()
def species_sequences(species_id, page=1):
    """
    Returns a table with sequences from the selected species

    :param species_id: Internal ID of the species
    :param page: Page number
    """
    sequences = Species.query.get(species_id).sequences.paginate(page,
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
    response.headers['Content-type'] = 'text/plain'

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
    sequences = current_species.sequences.options(undefer('coding_sequence')).options(noload('xrefs')).all()

    for s in sequences:
        if s.type == "protein_coding":
            output.append(">" + s.name)
            output.append(s.protein_sequence)

    response = make_response("\n".join(output))
    response.headers["Content-Disposition"] = "attachment; filename=" + current_species.code + ".aa.fasta"
    response.headers['Content-type'] = 'text/plain'

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
        sequences = Sequence.query\
            .options(undefer('coding_sequence'))\
            .options(noload('xrefs'))\
            .filter_by(species_id=selected_species)\
            .all()

        for s in sequences:
            if s.type == "protein_coding":
                yield ">" + s.name + '\n' + s.protein_sequence + '\n'

    return Response(generate(species_id), mimetype='text/plain')



