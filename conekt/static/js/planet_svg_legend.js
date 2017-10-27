/*global $, document, Pablo */
var svg_legend;
var svg_families;
var svg_labels;

// constants for drawing grid legend
var MARGIN_TOP = 150;
var MARGIN_LEFT = 85;
var HSPACE = 140;
var VSPACE = 80;
var COLS = 5;
var MAX_LABELS = 3;

$(function () {
    'use strict';
    var svg_file  = $('#legend').attr('url');
    svg_legend = Pablo.load(svg_file, function () {
            this.appendTo($('#legend'));
            svg_legend.find('[edge_color]').attr('style', 'display:none');
            svg_legend.find('[edge_color="color"]').attr('style', 'display:true');

            svg_legend.find('[edge_width]').attr('style', 'display:none');
            svg_legend.find('[edge_width="default_width"]').attr('style', 'display:true');
            svg_legend.find('[node_color]').attr('style', 'display:none');
            svg_legend.find('[node_color="color"]').attr('style', 'display:true');
        });
});

$('.cy-edge-color').click(function (ev) {
    'use strict';
    ev.preventDefault();
    svg_legend.find('[edge_color]').attr('style', 'display:none');
    svg_legend.find('[edge_color="' + $(this).attr('attr') + '"]').attr('style', 'display:true');
});

$('.cy-edge-width').click(function (ev) {
    'use strict';
    ev.preventDefault();
    svg_legend.find('[edge_width]').attr('style', 'display:none');
    svg_legend.find('[edge_width="' + $(this).attr('attr') + '"]').attr('style', 'display:true');
});

$('.cy-node-color').click(function (ev) {
    'use strict';
    ev.preventDefault();
    svg_legend.find('[node_color]').attr('style', 'display:none');
    svg_legend.find('[node_color="' + $(this).attr('attr') + '"]').attr('style', 'display:true');
});

$('#cy-download-svg-legend').click(function (ev) {
    'use strict';
    ev.preventDefault();

    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(svg_legend));
    element.setAttribute('download', 'cytoscape_legend.svg');

    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
});

$('#cy-download-png-legend').click(function (ev) {
    'use strict';
    ev.preventDefault();

    svg_legend.dataUrl('png', function (dataUrl) {
        var element = document.createElement('a');
        element.setAttribute('href', dataUrl);
        element.setAttribute('download', "cytoscape_legend.png");
        element.setAttribute('style', 'display:none');

        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    });
});

function generate_legend(label_set, attribute, extra_attribute) {
    'use strict';
    var families = svg_legend.g().transform('translate', MARGIN_LEFT, MARGIN_TOP),
        col = 0,
        row = 0,
        color = null,
        shape = null;

    families.attr('node_color', attribute);
    families.attr('style', 'opacity:0');

    for (color in label_set) {
        for (shape in label_set[color]) {
            var label = (label_set[color][shape] === null) ? 'None' : label_set[color][shape],
                new_label = families.g();

            new_label.attr('class', 'legend_node legend_node_' + label.split(';').join('_'));
            new_label.transform('translate', col * HSPACE, row * VSPACE + 15);
            new_label.attr(extra_attribute, label)

            if (shape === 'ellipse') {
                new_label.circle({r: 15, fill: color});
            } else if (shape === 'rectangle') {
                new_label.rect({x: -15, y: -15, width: 30, height: 30, fill: color});
            } else if (shape === 'roundrectangle') {
                new_label.rect({x: -15, y: -15, rx: 5, ry: 5, width: 30, height: 30, fill: color});
            } else if (shape === 'triangle') {
                new_label.polygon({points: '0,-20 17,10 -17,10', fill: color});
            } else if (shape === 'hexagon') {
                new_label.polygon({points: '0,15 13,7.5 13,-7.5 0,-15 -13,-7.5 -13,7.5', fill: color})
                    .transform('rotate', 30);
            } else if (shape === 'octagon') {
                new_label.polygon({points: '0,15 10.6,10.6 15,0 10.6,-10.6 0,-15 -10.6,-10.6 -15,0 -10.6,10.6', fill: color})
                    .transform('rotate', 22.5);
            } else if (shape === 'vee') {
                new_label.polygon({points: '0,20 17,-10 0,0 -17,-10', fill: color});
            } else if (shape === 'diamond') {
                new_label.rect({x: -13, y: -13, width: 26, height: 26, fill: color})
                    .transform('rotate', 45);
            } else if (shape === 'rhomboid') {
                new_label.rect({x: -13, y: -15, width: 26, height: 30, fill: color})
                    .transform('skewX', 30);
            }

            var label_group = new_label.g(),
                labels = label.split(';');
            if (labels.length > MAX_LABELS) {
                labels = labels.slice(0, MAX_LABELS);
                labels.push('...');
            }

            var i = 0;
            for (i = 0; i < labels.length; i += 1) {
                var y = 15 * i;
                label_group.text({y: y, fill: 'none', stroke: '#fff'}).content(labels[i])
                    .attr('text-anchor', 'middle')
                    .attr('font-family', 'sans-serif');
                label_group.text({y: y, fill: 'black'}).content(labels[i])
                    .attr('text-anchor', 'middle')
                    .attr('font-family', 'sans-serif');
                label_group.attr('height', y + 15);
            }

            label_group.transform('translate', 0, -(label_group.attr('height') / 2) + 12);

            if (col < COLS - 1) {
                col += 1;
            } else {
                col = 0;
                row += 1;
            }
        }
    }

    var total_height = parseInt(((row + 1) * VSPACE + MARGIN_TOP), 10),
        document_height = parseInt(svg_legend.attr('height').replace('px', ''), 10);
        //viewbox = svg_legend.attr('viewBox');

    if (total_height > document_height) {
        svg_legend.attr('viewBox', '0 0 750 ' + total_height);
        svg_legend.attr('height', total_height + 'px');
    }
}
