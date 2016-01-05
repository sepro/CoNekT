var svg_legend;

function svg_legend_init(svg_file, container_id) {
     svg_legend = Pablo.load(svg_file, function(){
        this.appendTo(container_id);
        svg_legend.find('[legend_type="edge_color"]').attr('style', 'opacity:0');
    });
}

$('.cy-edge-color').click(function() {
    svg_legend.find('[legend_type="edge_color"]').attr('style', 'opacity:0');
    svg_legend.find('[edge_color="' + $( this ).attr( 'attr' ) + '"]').attr('style', 'opacity:100');
})