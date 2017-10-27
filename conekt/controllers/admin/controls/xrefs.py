import os
from tempfile import mkstemp

from flask import request, flash, url_for
from conekt.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.forms.admin.add_xrefs import AddXRefsForm, AddXRefsFamiliesForm
from conekt.models.xrefs import XRef


@admin_controls.route('/add/xrefs', methods=['POST'])
@admin_required
def add_xrefs():
    """
    Adds external references to sequences. A few platforms are included by default (note that this only works if the
    sequence name is the same in PlaNet and the third-party platform)

    A tab-delimited text-file can be uploaded with the following structure:

    sequence_name(planet)   sequence_name(other platform)   platform_name   url
    ...

    :return: Redirect to admin panel interface
    """
    form = AddXRefsForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        platform = request.form.get('platforms')

        if platform == 'plaza_3_dicots':
            XRef.create_plaza_xref_genes(species_id)
            flash('Added XRefs to PLAZA 3.0 dicots for species id %d' % species_id, 'success')
            return redirect(url_for('admin.index'))
        elif platform == 'evex':
            XRef.create_evex_xref_genes(species_id)
            flash('Added XRefs to EVEX dicots for species id %d' % species_id, 'success')
            return redirect(url_for('admin.index'))
        else:
            xref_data = request.files[form.file.name].read()
            if xref_data != b'':
                fd, temp_path = mkstemp()

                with open(temp_path, 'wb') as xref_writer:
                    xref_writer.write(xref_data)

                XRef.add_xref_genes_from_file(species_id, temp_path)

                os.close(fd)
                os.remove(temp_path)
                flash('Added XRefs from file %s' % form.file.name, 'success')
            else:
                flash('Empty file or no file provided, cannot add XRefs', 'danger')

            return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/xrefs_family', methods=['POST'])
@admin_required
def add_xrefs_family():
    """
    Adds external references to gene families. A tab-delimited text-file can be uploaded with the following structure:

    family_name(planet)   family_name(other platform)   platform_name   url
    ...

    :return: Redirect to admin panel interface
    """
    form = AddXRefsFamiliesForm(request.form)

    if request.method == 'POST':
        gene_family_methods_id = int(request.form.get('gene_family_method_id'))

        xref_data = request.files[form.file.name].read()
        if xref_data != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(xref_data)

            XRef.add_xref_families_from_file(gene_family_methods_id, temp_path)

            os.close(fd)
            os.remove(temp_path)
            flash('Added XRefs from file %s' % form.file.name, 'success')
        else:
            flash('Empty file or no file provided, cannot add XRefs', 'danger')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)