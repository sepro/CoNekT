/*
Function to write SVG file from cytoscape json object
*/

function __convertColor( color ) {
    if (color.length === 7) {
        return color.toLowerCase();
    } else {
        c = '#' + color[1] + color[1] + color[2] + color[2] + color[3] + color[3];
        return c.toLowerCase();
    }

}

function writeSVG(data) {

    var element = document.createElement('div');
    element.className = "svgDiv";

    var svg = Pablo(element).svg({
        width: 800,
        height: 800
    });



    data.elements.nodes.forEach( function(node) {
        var group = svg.g();
        group.transform('translate', node.position.x, node.position.y)

        if (node.data.current_shape === 'ellipse') {
            group.circle({r:15, fill:__convertColor(node.data.current_color)});
        } else if (node.data.current_shape === 'rectangle') {
            group.rect({x:-15, y:-15, width:30, height:30, fill:__convertColor(node.data.current_color)});
        } else if (node.data.current_shape === 'roundrectangle') {
            group.rect({x:-15, y:-15, rx:5, ry:5, width:30, height:30, fill:__convertColor(node.data.current_color)});
        } else if (node.data.current_shape === 'triangle') {
            group.polygon({points:'0,-20 17,10 -17,10', fill:__convertColor(node.data.current_color)});
        } else if (node.data.current_shape === 'hexagon') {
            group.polygon({points:'0,15 13,7.5 13,-7.5 0,-15 -13,-7.5 -13,7.5', fill:__convertColor(node.data.current_color)})
                .transform('rotate', 30);
        } else if (node.data.current_shape === 'octagon') {
            group.polygon({points:'0,15 10.6,10.6 15,0 10.6,-10.6 0,-15 -10.6,-10.6 -15,0 -10.6,10.6', fill:__convertColor(node.data.current_color)})
                .transform('rotate', 22.5);
        } else if (node.data.current_shape === 'vee') {
            group.polygon({points:'0,20 17,-10 0,0 -17,-10', fill:__convertColor(node.data.current_color)});
        } else if (node.data.current_shape === 'diamond') {
            group.rect({x:-13, y:-13, width:26, height:26, fill:__convertColor(node.data.current_color)})
            .transform('rotate', 45);
        } else if (node.data.current_shape === 'rhomboid') {
            group.rect({x:-13, y:-15, width:26, height:30, fill:__convertColor(node.data.current_color)})
            .transform('skewX', 30);
        }

        text = node.data.name;
        if (node.data.gene_name !== '') { text = node.data.gene_name; }

        group.text({y:6, fill:"none", stroke:'#888888'}).content(text)
            .attr('text-anchor', 'middle')
            .attr('font-family', 'sans-serif');
        group.text({y:6, fill:"white"}).content(text)
            .attr('text-anchor', 'middle')
            .attr('font-family', 'sans-serif');

    });

    data.elements.edges.forEach( function(edge) {

    });



    return(element.innerHTML)

}