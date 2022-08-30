import json
import base64
import contextlib

from flask import Blueprint, request, render_template, flash, Markup, url_for
from sqlalchemy.orm import noload

from conekt import cache
from conekt.forms.profile_comparison import ProfileComparisonForm
from conekt.helpers.chartjs import prepare_profiles, prepare_profiles_download
from conekt.models.expression.coexpression_clusters import CoexpressionCluster
from conekt.models.expression.profiles import ExpressionProfile
from conekt.models.relationships.sequence_cluster import (
    SequenceCoexpressionClusterAssociation,
)
from conekt.models.sequences import Sequence

profile_comparison = Blueprint("profile_comparison", __name__)


@profile_comparison.route("/cluster/<cluster_id>")
@profile_comparison.route("/cluster/<cluster_id>/<int:normalize>")
@cache.cached()
def profile_comparison_cluster(cluster_id, normalize=0):
    """
    This will get all the expression profiles for members of given cluster and plot them

    :param cluster_id: internal id of the cluster to visualize
    :param normalize: if the plot should be normalized (against max value of each series)
    """
    cluster = CoexpressionCluster.query.get(cluster_id)
    associations = (
        SequenceCoexpressionClusterAssociation.query.filter_by(
            coexpression_cluster_id=cluster_id
        )
        .options(noload(SequenceCoexpressionClusterAssociation.sequence))
        .all()
    )

    probes = [a.probe for a in associations]

    # get max 51 profiles, only show the first 50 (the extra one is fetched to throw the warning)
    profiles = ExpressionProfile.get_profiles(
        cluster.method.network_method.species_id, probes, limit=51
    )

    if len(profiles) > 50:
        flash(
            Markup(
                (
                    "To many profiles in this cluster only showing the <strong>first 50</strong>. <br />"
                    + "<strong>Note:</strong> The <a href='%s'>heatmap</a> can be used to with more genes and "
                    + "allows downloading the data for local analysis."
                )
                % url_for("heatmap.heatmap_cluster", cluster_id=cluster_id)
            ),
            "warning",
        )

    profile_chart = prepare_profiles(
        profiles[:50],
        True if normalize == 1 else False,
        ylabel="TPM" + (" (normalized)" if normalize == 1 else ""),
    )

    # Get table in base64 format for download
    data = base64.encodebytes(
        prepare_profiles_download(
            profiles[:50], True if normalize == 1 else False
        ).encode("utf-8")
    )

    return render_template(
        "expression_profile_comparison.html",
        profiles=json.dumps(profile_chart),
        normalize=normalize,
        cluster=cluster,
        data=data.decode("utf-8"),
    )


@profile_comparison.route("/", methods=["GET", "POST"])
def profile_comparison_main():
    """
    Profile comparison tool, accepts a species and a list of probes and plots the profiles for the selected
    """
    form = ProfileComparisonForm(request.form)
    form.populate_species()

    if request.method == "POST":
        terms = request.form.get("probes").split()
        species_id = request.form.get("species_id")
        normalize = True if request.form.get("normalize") == "y" else False

        probes = terms

        # also do search by gene ID
        sequences = Sequence.query.filter(Sequence.name.in_(terms)).all()

        for s in sequences:
            for ep in s.expression_profiles:
                probes.append(ep.probe)

        # make probe list unique
        probes = list(set(probes))

        # get max 51 profiles, only show the first 50 (the extra one is fetched to throw the warning)
        profiles = ExpressionProfile.get_profiles(species_id, probes, limit=51)

        not_found = [p.lower() for p in probes]
        for p in profiles:
            with contextlib.suppress(ValueError):
                not_found.remove(p.probe.lower())

            with contextlib.suppress(ValueError):
                not_found.remove(p.sequence.name.lower())

        if len(not_found) > 0:
            flash("Couldn't find profile for: %s" % ", ".join(not_found), "warning")

        if len(profiles) > 50:
            flash(
                Markup(
                    (
                        "To many profiles in this cluster only showing the <strong>first 50</strong>. <br />"
                        + "<strong>Note:</strong> The <a href='%s'>heatmap</a> can be used to with more genes and "
                        + "allows downloading the data for local analysis."
                    )
                    % url_for("heatmap.heatmap_main")
                ),
                "warning",
            )

        # Get json object for chart
        profile_chart = prepare_profiles(
            profiles[:50],
            normalize,
            ylabel="TPM" + (" (normalized)" if normalize == 1 else ""),
        )

        # Get table in base64 format for download
        data = base64.encodebytes(
            prepare_profiles_download(profiles[:50], normalize).encode("utf-8")
        )

        return render_template(
            "expression_profile_comparison.html",
            profiles=json.dumps(profile_chart),
            form=form,
            data=data.decode("utf-8"),
        )
    else:
        profiles = (
            ExpressionProfile.query.filter(ExpressionProfile.sequence_id is not None)
            .order_by(ExpressionProfile.species_id)
            .limit(5)
            .all()
        )

        example = {"species_id": None, "probes": None}

        if len(profiles) > 0:
            example["species_id"] = profiles[0].species_id
            example["probes"] = " ".join([p.sequence.name for p in profiles])

        return render_template(
            "expression_profile_comparison.html", form=form, example=example
        )
