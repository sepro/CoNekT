var svg_legend;

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