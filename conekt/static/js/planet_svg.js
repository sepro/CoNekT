/*
Function to write SVG file from cytoscape json object
*/

function __componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function __rgbToHex(r, g, b) {
    return "#" + __componentToHex(r) + __componentToHex(g) + __componentToHex(b);
}

function __convertColor( color ) {
    if (color.indexOf('rgb(') > -1) {
        values = color.replace('rgb','').replace('(','').replace(')','');
        rgb = values.split(", ");
        return __rgbToHex(parseInt(rgb[0]), parseInt(rgb[1]), parseInt(rgb[2])).toLowerCase();
    }
    else if (color.length === 7) {
        return color.toLowerCase();
    } else {
        c = '#' + color[1] + color[1] + color[2] + color[2] + color[3] + color[3];
        return c.toLowerCase();
    }

}

function writeSVG(data) {
    var min_x = null;
    var min_y = null;
    var max_x = 200;
    var max_y = 200;
    var margin = 100;

    var node_positions = new Array();
    data.nodes().forEach( function(node) {
        node_positions[node.data('id')] = new Array();
        node_positions[node.data('id')]["x"] = node.position('x');
        node_positions[node.data('id')]["y"] = node.position('y');

        if (node.position('x') > max_x) { max_x = node.position('x')}
        if (node.position('y') > max_y) { max_y = node.position('y')}
        
        if (min_x === null) {min_x =  node.position('x');}
        if (min_y === null) {min_y =  node.position('y');}
        
        if (node.position('x') < min_x) { min_x = node.position('x')}
        if (node.position('y') < min_y) { min_y = node.position('y')}
        
    });

    var width = (max_x - min_x) + margin*2;
    var height = (max_y - min_y) + margin*2;

    var element = document.createElement('div');
    element.className = "svgDiv";

    var svg = Pablo(element).svg({
        width: width,
        height: height
    });

    var network = svg.g().transform('translate', (-min_x)+margin, (-min_y)+margin);

    data.edges().forEach( function(edge) {
        if (edge.data('homology'))
        {
            network.line({  x1:node_positions[edge.data('source')]["x"],
                        y1:node_positions[edge.data('source')]["y"],
                        x2:node_positions[edge.data('target')]["x"],
                        y2:node_positions[edge.data('target')]["y"],
                        stroke: __convertColor(edge.renderedStyle('line-color')),
                        'stroke-width': edge.renderedStyle('width').replace('px', ''),
                        'stroke-dasharray': '5,5'})
        } else {
            network.line({  x1:node_positions[edge.data('source')]["x"],
                        y1:node_positions[edge.data('source')]["y"],
                        x2:node_positions[edge.data('target')]["x"],
                        y2:node_positions[edge.data('target')]["y"],
                        stroke: __convertColor(edge.renderedStyle('line-color')),
                        'stroke-width': edge.renderedStyle('width').replace('px', '')})
        }
    });

    data.nodes().forEach( function(node) {
        if (!node.data('compound')) {
            var group = network.g();
            group.transform('translate', node.position('x'), node.position('y'))
            if (node.renderedStyle('shape') === 'ellipse') {
                group.circle({r:15, fill:__convertColor(node.renderedStyle('background-color'))});
            } else if (node.renderedStyle('shape') === 'rectangle') {
                group.rect({x:-15, y:-15, width:30, height:30, fill:__convertColor(node.renderedStyle('background-color'))});
            } else if (node.renderedStyle('shape') === 'roundrectangle') {
                group.rect({x:-15, y:-15, rx:5, ry:5, width:30, height:30, fill:__convertColor(node.renderedStyle('background-color'))});
            } else if (node.renderedStyle('shape') === 'triangle') {
                group.polygon({points:'0,-20 17,10 -17,10', fill:__convertColor(node.renderedStyle('background-color'))});
            } else if (node.renderedStyle('shape') === 'hexagon') {
                group.polygon({points:'0,15 13,7.5 13,-7.5 0,-15 -13,-7.5 -13,7.5', fill:__convertColor(node.renderedStyle('background-color'))})
                    .transform('rotate', 30);
            } else if (node.renderedStyle('shape') === 'octagon') {
                group.polygon({points:'0,15 10.6,10.6 15,0 10.6,-10.6 0,-15 -10.6,-10.6 -15,0 -10.6,10.6', fill:__convertColor(node.renderedStyle('background-color'))})
                    .transform('rotate', 22.5);
            } else if (node.renderedStyle('shape') === 'vee') {
                group.polygon({points:'0,20 17,-10 0,0 -17,-10', fill:__convertColor(node.renderedStyle('background-color'))});
            } else if (node.renderedStyle('shape') === 'diamond') {
                group.rect({x:-13, y:-13, width:26, height:26, fill:__convertColor(node.renderedStyle('background-color'))})
                .transform('rotate', 45);
            } else if (node.renderedStyle('shape') === 'rhomboid') {
                group.rect({x:-13, y:-15, width:26, height:30, fill:__convertColor(node.renderedStyle('background-color'))})
                .transform('skewX', 30);
            }

            text = node.data('name');
            if (node.data('best_name') !== '') { text = node.data('best_name'); }

            group.text({y:6, fill:"none", stroke:'#ffffff',  'stroke-width':"2"}).content(text)
                .attr('text-anchor', 'middle')
                .attr('font-family', 'sans-serif');
            group.text({y:6, fill:"black"}).content(text)
                .attr('text-anchor', 'middle')
                .attr('font-family', 'sans-serif');
        }
    });

    return(element.innerHTML)

}