var svg_legend;
var svg_families;
var svg_labels;

// constants for drawing grid legend
var MARGIN_TOP = 150
var MARGIN_LEFT = 50
var HSPACE = 120
var VSPACE = 80
var COLS = 5
var MAX_LABELS = 3

$(function() {
     var svg_file  = $('#legend').attr( "url" );
     svg_legend = Pablo.load(svg_file, function(){
        this.appendTo($('#legend'));
        svg_legend.find('[edge_color]').attr('style', 'opacity:0');
        svg_legend.find('[edge_color="color"]').attr('style', 'opacity:100')

        svg_legend.find('[edge_width]').attr('style', 'opacity:0');
        svg_legend.find('[edge_width="default"]').attr('style', 'opacity:100')

        svg_legend.find('[node_color]').attr('style', 'opacity:0');
        svg_legend.find('[node_color="color"]').attr('style', 'opacity:100')
    });

});

$('.cy-edge-color').click(function(ev) {
    ev.preventDefault();
    svg_legend.find('[edge_color]').attr('style', 'opacity:0');
    svg_legend.find('[edge_color="' + $( this ).attr( 'attr' ) + '"]').attr('style', 'opacity:100');
})

$('.cy-edge-width').click(function(ev) {
    ev.preventDefault();
    svg_legend.find('[edge_width]').attr('style', 'opacity:0');
    svg_legend.find('[edge_width="' + $( this ).attr( 'attr' ) + '"]').attr('style', 'opacity:100');
})

$('.cy-node-color').click(function(ev) {
    ev.preventDefault();
    svg_legend.find('[node_color]').attr('style', 'opacity:0');
    svg_legend.find('[node_color="' + $( this ).attr( 'attr' ) + '"]').attr('style', 'opacity:100');
})

function generate_legend(label_set, attribute) {
    var families = svg_legend.g().transform('translate', MARGIN_LEFT, MARGIN_TOP);
    families.attr('node_color', attribute);
    families.attr('style', 'opacity:0');

    var col = 0;
    var row = 0;

    for (var color in label_set) {
        for(var shape in label_set[color])
        {
            var label = (label_set[color][shape] === null) ? 'None' : label_set[color][shape];

            var new_label = families.g();
            new_label.transform('translate', col*HSPACE, row*VSPACE+15);

            if (shape === 'ellipse') {
                new_label.circle({r:15, fill:color});
            } else if (shape === 'rectangle') {
                new_label.rect({x:-15, y:-15, width:30, height:30, fill:color});
            } else if (shape === 'roundrectangle') {
                new_label.rect({x:-15, y:-15, rx:5, ry:5, width:30, height:30, fill:color});
            } else if (shape === 'triangle') {
                new_label.polygon({points:'0,-20 17,10 -17,10', fill:color});
            } else if (shape === 'hexagon') {
                new_label.polygon({points:'0,15 13,7.5 13,-7.5 0,-15 -13,-7.5 -13,7.5', fill:color})
                    .transform('rotate', 30);
            } else if (shape === 'octagon') {
                new_label.polygon({points:'0,15 10.6,10.6 15,0 10.6,-10.6 0,-15 -10.6,-10.6 -15,0 -10.6,10.6', fill:color})
                    .transform('rotate', 22.5);
            } else if (shape === 'vee') {
                new_label.polygon({points:'0,20 17,-10 0,0 -17,-10', fill:color});
            } else if (shape === 'diamond') {
                new_label.rect({x:-13, y:-13, width:26, height:26, fill:color})
                .transform('rotate', 45);
            } else if (shape === 'rhomboid') {
                new_label.rect({x:-13, y:-15, width:26, height:30, fill:color})
                .transform('skewX', 30);
            }

            label_group = new_label.g();
            labels = label.split(';');
            if (labels.length > MAX_LABELS) {
                labels = labels.slice(0,MAX_LABELS);
                labels.push('...');
            }

            for(var i = 0; i < labels.length; i++) {
                var y = 15*i;
                label_group.text({y:y, fill:"none", stroke:'#888888'}).content(labels[i])
                    .attr('text-anchor', 'middle')
                    .attr('font-family', 'sans-serif');
                label_group.text({y:y, fill:"white"}).content(labels[i])
                    .attr('text-anchor', 'middle')
                    .attr('font-family', 'sans-serif');
                label_group.attr('height', y+15)
            }

            label_group.transform('translate', 0, -(label_group.attr('height')/2)+12);

            if (col < COLS-1) {
                col += 1;
            } else {
                col = 0;
                row += 1;
            }
        }
    }
}