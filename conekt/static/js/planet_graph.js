/*global $, cytoscape, document, graph_data, window, generate_legend, writeXGMML, writeSVG, Pablo, svg_legend */
var cy;
var initial_json;

function select_neighborhood(ev, node_name) {
    ev.preventDefault();

    // Select all nodes in the neighborhood
    cy.nodes('[gene_name = \'' + node_name + '\']').neighborhood().select();

    // Reset all nodes in the legend
    svg_legend.find(".legend_node").transform('scale', null);

    // Close tooltip
    $('div.qtip:visible').qtip('hide');
};

function click_edge(ev) {
    ev.preventDefault();
    // Reset all nodes in the legend
    svg_legend.find(".legend_node").transform('scale', null);
};

function select_homologs(ev, family) {
    ev.preventDefault();

    // Select all nodes in the neighborhood
    cy.nodes('[family_name = \'' + family + '\' ]').select();

    // Reset all nodes in the legend
    svg_legend.find(".legend_node").transform('scale', null);

    // Find node matching to family
    var family_match = svg_legend.find(".legend_node_"+ family);
    // Increase size of that node
    family_match.transform('scale', 1.5);


    // Close tooltip
    $('div.qtip:visible').qtip('hide');
};

function select_lc(ev, lc_label) {
    ev.preventDefault();

    // Select all nodes in the neighborhood
    cy.nodes('[lc_label = \'' + lc_label + '\' ]').select();

    // Reset all nodes in the legend
    svg_legend.find(".legend_node").transform('scale', null);

    // Find node matching to family
    var family_match = svg_legend.find(".legend_node_"+ lc_label.split(';').join('_'));
    // Increase size of that node
    family_match.transform('scale', 1.5);


    // Close tooltip
    $('div.qtip:visible').qtip('hide');
};

$(function () { // on dom ready
    'use strict';
    var url = $('#cy').attr("json"),
        cycss_url = $('#cy').attr("cycss");

    cy = cytoscape({
        container: document.getElementById('cy'),
        style: $.get(cycss_url),
        wheelSensitivity: 0.333,
        elements: url !== undefined ? $.getJSON(url) : graph_data,
        layout: {
            name: 'cose',
            padding: 60,
            minNodeSpacing: 30,
            avoidOverlap: false
        },
        ready: function () {
            window.cy = this;

            var has_ecc = false;
            initial_json = JSON.stringify(cy.json(), null, '\t');

            cy.nodes('[^compound]').forEach(function (n) {
                // code to add tooltips to the selected node
                var content = [
                    {
                        value: n.data('gene_id') !== null ? '<strong>Gene ID:</strong> <a href="' + n.data('gene_link') + '">' + n.data('gene_name') + '</a>' : '<span class="text-muted">No sequence linked to probe</span>'
                    },
                    {
                        value: n.data('description') !== null ? '<em>' + (n.data('description').length > 90 ? n.data('description').substring(0, 87) + "..." :  n.data('description')) + '</em><br />' : '<span class="text-muted">No description available</span>'
                    },
                    {
                        value: n.data('tokens') !== null ? '<strong>Other names:</strong> ' + n.data('tokens') + '<br />' : '<span class="text-muted">No alias available</span>'
                    }];

                if (n.data('profile_link') !== undefined) {
                    content.push({value: '<strong>Profile:</strong> <a href="' + n.data('profile_link') + '">' + n.data('id') + '</a>'});
                }

                if (n.data('cluster_id') !== undefined) {
                    content.push({value: '<strong>Cluster:</strong> <a href="' + n.data('cluster_url') + '">' + n.data('cluster_name') + '</a>'});
                }

                if (n.data('spm_condition') !== undefined) {
                    content.push({value: '<strong>Expression specificity:</strong> ' + n.data('spm_condition') + '(' + n.data('spm_score').toFixed(2) + ')'});
                }

                content.push(
                    {
                        value: n.data('family_name') !== null ? '<strong>Family:</strong> <a href="' + n.data('family_url') + '">' + n.data('family_name') + '</a>' : '<span class="text-muted">No family found</span>'
                    },
                    {
                        value: n.data('family_clade') !== 'None' ? '<strong>Clade:</strong> ' + n.data('family_clade') : '<span class="text-muted">No clade assigned</span>'
                    },
                    {
                        value: ''
                    },
                    {
                        value: '<span class="text-muted">Select:</span>'
                    },
                    {
                        value: '<a href="#" onclick="select_neighborhood(event, \'' + n.data('gene_name') + '\')">Direct neighbors</a>'
                    }
                );

                if (n.data('family_name') !== null) {
                    content.push(
                    {
                        value: '<a href="#" onclick="select_homologs(event, \'' + n.data('family_name') + '\')">Homologs</a>'
                    }
                    )
                }
                if (n.data('lc_label') !== null) {
                    content.push(
                    {
                        value: '<a href="#" onclick="select_lc(event, \'' + n.data('lc_label') + '\')">Same label</a>'
                    }
                    )
                }

                n.qtip({
                    content: content.map(function (item) {
                        return item.value;
                    }).join('<br />\n'),
                    position: {
                        my: 'bottom center',
                        at: 'top center'
                    },
                    style: {
                        classes: 'qtip-bootstrap',
                        tip: {
                            width: 16,
                            height: 8
                        }
                    }
                });
            }); /* End nodes.forEach */

            cy.edges('[^homology]').forEach(function (e) {
                // code to add tooltips to the selected node
                var content = [{
                        value: 'Edge: ' + e.data('source') + ' and ' + e.data('target')
                    }];

                if (e.data('profile_comparison') !== undefined) {
                    content.push({value: '<a href="' + e.data('profile_comparison') + '">Compare expression profiles</a>'});
                }

                if (e.data('hrr') !== undefined) {
                    if (e.data('hrr') !== null) {
                        content.push({ value: 'Rank (HRR): ' + e.data('hrr') });
                    } else {
                        content.push({ value: 'Couldn\'t determine HRR' })
                    }
                }

                if (e.data('link_pcc') !== undefined) {
                    if (e.data('link_pcc') !== null) {
                        content.push({ value: 'Correlation (PCC): ' + e.data('link_pcc').toFixed(3) });
                    }
                }

                if (e.data('depth') !== undefined) {
                    content.push({ value: 'Depth: ' + e.data('depth') });
                }

                if (e.data('ecc_score') !== undefined) {
                    content.push({ value: 'ECC: ' + e.data('ecc_score').toFixed(2) });
                    has_ecc = true;
                }

                e.qtip({
                    content: content.map(function (item) {
                        return item.value;
                    }).join('<br />\n'),
                    position: {
                        my: 'bottom center',
                        at: 'center center'
                    },
                    style: {
                        classes: 'qtip-bootstrap',
                        tip: {
                            width: 16,
                            height: 8
                        }
                    }
                });
            }); // end cy.edges.forEach...

            /* Enable click events */
            cy.edges().on("click", function(ev) {
                click_edge(ev);
            });

             cy.on("click", function(ev) {
                click_edge(ev);
            });

            /* Make cursor pointer when hovering over*/
            cy.on('mouseover', 'node', function (evt) {
                        $('html,body').css('cursor', 'pointer');
                    } );

            cy.on('mouseout', 'node', function (evt) {
                        $('html,body').css('cursor', 'default');
                    });

            /* Make cursor pointer when hovering over*/
            cy.on('mouseover', 'edge', function (evt) {
                        $('html,body').css('cursor', 'pointer');
                    } );

            cy.on('mouseout', 'edge', function (evt) {
                        $('html,body').css('cursor', 'default');
                    });

            // Fill data for legend
            var svg_families = [],
                svg_labels = [],
                svg_species = [],
                svg_spm = [],
                svg_clusters = [],
                svg_clades = [];
            cy.nodes('[^compound]').forEach(function (n) {
                var family_color = n.data('family_color'),
                    family_shape = n.data('family_shape'),
                    family = n.data('family_name'),

                    lc_color = n.data('lc_color'),
                    lc_shape = n.data('lc_shape'),
                    lc_label = n.data('lc_label'),

                    spm_color = n.data('spm_condition_color'),
                    spm_shape = n.data('spm_condition_shape'),
                    spm = n.data('spm_condition'),

                    cluster_color = n.data('cluster_color'),
                    cluster_shape = n.data('cluster_shape'),
                    cluster = n.data('cluster_name'),

                    clade = n.data('family_clade'),
                    clade_color = n.data('family_clade_color'),
                    clade_shape = n.data('family_clade_shape'),

                    species = n.data('species_name'),
                    species_color = n.data('species_color'),
                    species_shape = 'ellipse';

                if (species_color !== undefined) {
                    if (!svg_species.hasOwnProperty(species_color)) {
                        svg_species[species_color] = [];
                    }
                    svg_species[species_color][species_shape] = species;
                }

                if (family_color !== undefined) {
                    if (!svg_families.hasOwnProperty(family_color)) {
                        svg_families[family_color] = [];
                    }
                    svg_families[family_color][family_shape] = family;
                }

                if (clade !== undefined) {
                    if (!svg_clades.hasOwnProperty(clade_color)) {
                        svg_clades[clade_color] = [];
                    }
                    svg_clades[clade_color][clade_shape] = clade;
                }

                if (lc_color !== undefined) {
                    if (!svg_labels.hasOwnProperty(lc_color)) {
                        svg_labels[lc_color] = [];
                    }
                    svg_labels[lc_color][lc_shape] = lc_label;
                }
                if (cluster_color !== undefined) {
                    if (!svg_clusters.hasOwnProperty(cluster_color)) {
                        svg_clusters[cluster_color] = [];
                    }
                    svg_clusters[cluster_color][cluster_shape] = cluster;
                }
                if (spm_color !== undefined) {
                    if (!svg_spm.hasOwnProperty(spm_color)) {
                        svg_spm[spm_color] = [];
                    }
                    svg_spm[spm_color][spm_shape] = spm;
                }
            }); //end cy.nodes.forEach

            if (Object.keys(svg_clades).length > 0) { generate_legend(svg_clades, 'family_clade_color', 'family_clade'); }
            if (Object.keys(svg_labels).length > 0) { generate_legend(svg_labels, 'lc_color', 'lc_label'); }
            if (Object.keys(svg_families).length > 0) { generate_legend(svg_families, 'family_color', 'family_name'); }
            if (Object.keys(svg_clusters).length > 0) { generate_legend(svg_clusters, 'cluster_color', 'cluster'); }
            if (Object.keys(svg_spm).length > 0) { generate_legend(svg_spm, 'spm_color', 'spm'); }
            if (Object.keys(svg_species).length > 0) { generate_legend(svg_species, 'species_color', 'species'); }

            if (has_ecc) {
                $('.cy-node-color[attr="species_color"]').click();
                $('.cy-edge-color[attr="ecc_type"]').click();
            } else {
                $('.cy-node-color[attr="family_color"]').click();
            }


            $('#loading').addClass('loaded');
            $('#legend').show();

            $('g[family_name]').click( function(ev) {
                var family_name = $(this).attr('family_name');
                svg_legend.find(".legend_node").transform('scale', null);
                svg_legend.find(".legend_node_" + family_name).transform('scale', 1.5);
                cy.nodes().unselect();
                cy.nodes('[family_name="' + family_name + '"]').select();
            } );

            $('g[family_clade]').click( function(ev) {
                var family_clade = $(this).attr('family_clade');
                svg_legend.find(".legend_node").transform('scale', null);
                svg_legend.find(".legend_node_" + family_clade).transform('scale', 1.5);
                cy.nodes().unselect();
                cy.nodes('[family_clade="' + family_clade + '"]').select();
            } );

            $('g[lc_label]').click( function(ev) {
                var lc_label = $(this).attr('lc_label');
                svg_legend.find(".legend_node").transform('scale', null);
                svg_legend.find(".legend_node_" + lc_label.split(';').join('_')).transform('scale', 1.5);
                cy.nodes().unselect();
                cy.nodes('[lc_label="' + lc_label + '"]').select();
            } );

            $('g[species]').click( function(ev) {
                var species = $(this).attr('species');
                svg_legend.find(".legend_node").transform('scale', null);
                svg_legend.find('g[species="' + species + '"]').transform('scale', 1.5);
                cy.nodes().unselect();
                cy.nodes('[species_name="' + species + '"]').select();
            } );
        }
    });

    $('.cy-node-color').click(function (ev) {
        ev.preventDefault();
        $(this).closest('.cy-option-menu').find('.cy-node-color').each(function () {
            cy.nodes('[^compound]').removeClass($(this).attr('attr'));
        });
        cy.nodes('[^compound]').addClass($(this).attr('attr'));

        if ($(this).attr('attr') === 'family_color') {
            $('.cy-node-shape[attr="family_shape"]').click();
        } else if ($(this).attr('attr') === 'lc_color') {
            $('.cy-node-shape[attr="lc_shape"]').click();
        } else if ($(this).attr('attr') === 'spm_color') {
            $('.cy-node-shape[attr="spm_shape"]').click();
        } else if ($(this).attr('attr') === 'cluster_color') {
            $('.cy-node-shape[attr="cluster_shape"]').click();
        }else if ($(this).attr('attr') === 'family_clade_color') {
            $('.cy-node-shape[attr="family_clade_shape"]').click();
        } else {
            $('.cy-node-shape[attr="shape"]').click();
        }
    });

    $('.cy-node-shape').click(function (ev) {
        ev.preventDefault();
        $(this).closest('.cy-option-menu').find('.cy-node-shape').each(function () {
            cy.nodes('[^compound]').removeClass($(this).attr('attr'));
        });
        cy.nodes('[^compound]').addClass($(this).attr('attr'));
    });

    $('.cy-node-hide').click(function (ev) {
        ev.preventDefault();
        cy.nodes('[tag="hideable"]').addClass('hidden');
        $(this).hide();
        $('.cy-node-show').show();
    });

    $('.cy-node-show').click(function (ev) {
        ev.preventDefault();
        cy.nodes('[tag="hideable"]').removeClass('hidden');
        $(this).hide();
        $('.cy-node-hide').show();
    });

    $('.cy-edge-color').click(function (ev) {
        ev.preventDefault();
        $(this).closest('.cy-option-menu').find('.cy-edge-color').each(function () {
            cy.edges('[^homology]').removeClass($(this).attr('attr'));
        });
        cy.edges('[^homology]').addClass($(this).attr('attr'));
    });

    $('.cy-edge-width').click(function (ev) {
        ev.preventDefault();
        $(this).closest('.cy-option-menu').find('.cy-edge-width').each(function () {
            cy.edges('[^homology]').removeClass($(this).attr('attr'));
        });

        cy.edges('[^homology]').addClass($(this).attr('attr'));
    });

    $('#cy-edge-score').on("slideStop", function (slideEvt) {
        var cutoff = slideEvt.value;

        cy.edges("[hrr>" + cutoff + "]").style('display', 'none');
        cy.edges("[hrr<=" + cutoff + "]").style('display', 'element');
    });

    $('.cy-depth-filter').click(function (ev) {
        ev.preventDefault();
        $('.cy-depth-filter').removeClass('active');
        $(this).addClass('active');

        var cutoff = $(this).attr('cutoff');

        cy.nodes("[depth>" + (cutoff - 1) + "]").style('display', 'none');
        cy.nodes("[depth<=" + (cutoff - 1) + "]").style('display', 'element');

        cy.edges("[depth>" + cutoff + "]").style('display', 'none');
        cy.edges("[depth<=" + cutoff + "]").style('display', 'element');
    });

    $('.cy-layout').click(function (ev) {
        ev.preventDefault();
        var layout = $(this).attr('layout');

        cy.layout({name: layout,
                   padding: 60,
                   minNodeSpacing: 30,
                   animate: true,
                   avoidOverlap: false,
                   animationThreshold: 250,
                   //cose settings
                   nodeOverlap: 8,
                   idealEdgeLength: 32,
                   edgeElasticity: 32,
                   numIter: 1000,
                   maxSimulationTime: 2000,
                   lengthFactor: 100
                   });
    });

    $("#cy-search").click(function (ev) {
        ev.preventDefault();
        var term = $("#cy-search-term").val().trim().toLowerCase(),
            search_url = $(this).attr('search-url'),
            valid_genes = [];

        cy.nodes('[^compound]').toggleClass('found', false);
        $('#search_logo').hide();
        $('#search_spinner').show();
        $.getJSON(search_url + term, function (data) {
            var i = 0;
            for (i = 0; i < data.length; i += 1) {
                valid_genes.push(data[i]);
            }
        }).error(function() {
            $('#search_logo').show();
            $('#search_spinner').hide();
        }).done(function () {
            if (term !== '') {
                cy.nodes('[^compound]').each(function (i, node) {
                    if (node.data('gene_name').toLowerCase() === term ||
                            node.data('name').toLowerCase() === term ||
                            (node.data('family_name') !== null && node.data('family_name').toLowerCase() === term) ||
                            (node.data('interpro') !== undefined && node.data('interpro').indexOf(term.toUpperCase()) > -1) ||
                            valid_genes.indexOf(node.data('gene_id')) > -1 ||
                            (node.data('tokens') !== undefined && node.data('tokens') !== null && node.data('tokens').toLowerCase().includes(term))) {
                        node.toggleClass('found');
                    }
                });
            }
        }).done(function() {
            $('#search_logo').show();
            $('#search_spinner').hide();
        });
    });

    $('#cy-download-img-hires').click(function (ev) {
        ev.preventDefault();
        var png64 = cy.png({scale: 4, bg: "#FFFFFF"}),
            download = document.createElement('a');

        download.href = png64;
        download.download = 'cytoscape-hires.png';

        document.body.appendChild(download);
        download.click();
        document.body.removeChild(download);
    });

    $('#cy-download-img-lowres').click(function (ev) {
        ev.preventDefault();
        var png64 = cy.png({scale: 1, bg: "#FFFFFF"}),
            download = document.createElement('a');

        download.href = png64;
        download.download = 'cytoscape-lowres.png';

        document.body.appendChild(download);
        download.click();
        document.body.removeChild(download);
    });

    $('#cy-download-json').click(function (ev) {
        ev.preventDefault();
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(initial_json));
        element.setAttribute('download', "cytoscape.json");

        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    });

    $('#cy-download-jsoncy').click(function (ev) {
        ev.preventDefault();
        var eles = cy.elements(),
            json = '',
            element = document.createElement('a');

        eles.each(function (i, ele) {
            if (ele.isNode()) {
                ele.data('current_color', ele.renderedStyle('background-color'));
                ele.data('current_shape', ele.renderedStyle('shape'));
            } else if (ele.isEdge()) {
                ele.data('current_color', ele.renderedStyle('line-color'));
                ele.data('current_width', ele.renderedStyle('width'));
            }
        });

        json = JSON.stringify(cy.json(), null, '\t');

        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(json));
        element.setAttribute('download', "cytoscape_full.json");

        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    });

    $('#cy-download-xgmml').click(function (ev) {
        ev.preventDefault();

        var xgmml = writeXGMML(cy),
            element = document.createElement('a');

        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(xgmml));
        element.setAttribute('download', "cytoscape.xgmml");

        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    });

    $('#cy-download-svg').click(function (ev) {
        ev.preventDefault();

        var svg = writeSVG(cy),
            element = document.createElement('a');

        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(svg));
        element.setAttribute('download', "cytoscape.svg");

        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    });

    $('#cy-download-svg-with-legend').click(function (ev) {
        ev.preventDefault();

        var svg_out = new Pablo(writeSVG(cy)),
            legend = new Pablo(svg_legend.markup(false)),
            graph_height = parseInt(Pablo.getAttributes(svg_out[0]).height.replace('px', ''), 10),
            graph_width = parseInt(Pablo.getAttributes(svg_out[0]).width.replace('px', ''), 10),
            legend_height = parseInt(Pablo.getAttributes(legend[0]).height.replace('px', ''), 10),
            legend_width = parseInt(Pablo.getAttributes(legend[0]).width.replace('px', ''), 10),
            total_height = graph_height + 20 + legend_height,
            total_width = (graph_width > legend_width ? graph_width : legend_width),
            l = svg_out.g({'id': 'legend'}).transform('translate', 0, graph_height + 20),
            element = document.createElement('a');

        l.append(legend);

        svg_out.attr('viewBox', '0 0 ' + total_width + ' ' + total_height);
        svg_out.attr('height', total_height + 'px');
        svg_out.attr('width', total_width + 'px');

        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(svg_out));
        element.setAttribute('download', "cytoscape_w_legend.svg");

        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    });

    $('#cy-download-png-with-legend').click(function (ev) {
        ev.preventDefault();

        var svg_out = new Pablo(writeSVG(cy)),
            legend = new Pablo(svg_legend.markup(false)),
            graph_height = parseInt(Pablo.getAttributes(svg_out[0]).height.replace('px', ''), 10),
            graph_width = parseInt(Pablo.getAttributes(svg_out[0]).width.replace('px', ''), 10),
            legend_height = parseInt(Pablo.getAttributes(legend[0]).height.replace('px', ''), 10),
            legend_width = parseInt(Pablo.getAttributes(legend[0]).width.replace('px', ''), 10),
            total_height = graph_height + 20 + legend_height,
            total_width = (graph_width > legend_width ? graph_width : legend_width),
            l = svg_out.g({'id': 'legend'}).transform('translate', 0, graph_height + 20);

        l.append(legend);

        svg_out.attr('viewBox', '0 0 ' + total_width + ' ' + total_height);
        svg_out.attr('height', total_height + 'px');
        svg_out.attr('width', total_width + 'px');

        svg_out.dataUrl('png', function (dataUrl) {
            var element = document.createElement('a');
            element.setAttribute('href', dataUrl);
            element.setAttribute('download', "cytoscape__w_legend.png");
            element.setAttribute('style', 'display:none');

            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        });
    });

    $('#cy-reset').on('click', function (ev) {
        ev.preventDefault();
        cy.animate({
            fit: {
                eles: cy.elements(),
                padding: 5
            },
            duration: 500
        });
    });
}); // end on dom ready