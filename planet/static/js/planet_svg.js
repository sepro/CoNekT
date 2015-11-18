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
        group.circle({r:15, fill:__convertColor(node.data.current_color)});
        group.text({fill:"none", stroke:"black"}).content(node.data.name).attr('text-anchor', 'middle');
        group.text({fill:"white"}).content(node.data.name).attr('text-anchor', 'middle');
    });

    data.elements.edges.forEach( function(edge) {

    });



    return(element.innerHTML)

}