var svg_legend;

function svg_legend_init(svg_file, container_id) {
     svg_legend = Pablo.load(svg_file, function(){
        this.appendTo(container_id);
        svg_legend.find('g#score_group').attr('style', 'opacity:0');
    });
}