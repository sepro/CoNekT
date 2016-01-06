var svg_legend;

function svg_legend_init(svg_file, container_id) {
     svg_legend = Pablo.load(svg_file, function(){
        this.appendTo(container_id);
        svg_legend.find('[edge_color]').attr('style', 'opacity:0');
        svg_legend.find('[edge_color="color"]').attr('style', 'opacity:100')

        svg_legend.find('[edge_width]').attr('style', 'opacity:0');
        svg_legend.find('[edge_width="default"]').attr('style', 'opacity:100')
    });
}

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