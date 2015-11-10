/*
Function to write XGMML file from cytoscape json object
*/

function __convertColor( color ) {
    if (color.length === 7) {
        return color.toLowerCase();
    } else {
        c = '#' + color[1] + color[1] + color[2] + color[2] + color[3] + color[3];
        return c.toLowerCase();
    }

}

function __convertShape ( shape ) {
    if (shape === 'rhomboid') {
        return 'RHOMBUS';
    } else if (shape === 'roundrectangle') {
        return 'ROUND_RECTANGLE';
    } else {
        return shape.toUpperCase();
    }
}

function writeXGMML(data) {

    var xw = new XMLWriter('UTF-8');
    xw.formatting = 'indented';//add indentation and newlines
    xw.indentChar = ' ';//indent with spaces
    xw.indentation = 2;//add 2 spaces per level

    xw.writeStartDocument( );

    xw.writeStartElement( 'graph' );
    xw.writeAttributeString( 'id', 'planet_cytoscape_network');
    xw.writeAttributeString( 'label', 'planet_cytoscape_network');
    xw.writeAttributeString( 'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance');
    xw.writeAttributeString( 'xmlns:dc', 'http://purl.org/dc/elements/1.1/');
    xw.writeAttributeString( 'xmlns:rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#');
    xw.writeAttributeString( 'xmlns', 'http://www.cs.rpi.edu/XGMML');

        xw.writeStartElement( 'att' );
        xw.writeAttributeString( 'name', 'documentVersion');
        xw.writeAttributeString( 'value', '1.0');
        xw.writeEndElement();

        xw.writeStartElement( 'att' );
        xw.writeAttributeString( 'name', 'backgroundColor');
        xw.writeAttributeString( 'value', '#ffffff');
        xw.writeEndElement();

        data.elements.nodes.forEach( function(node) {
          xw.writeStartElement( 'node' );
          xw.writeAttributeString( 'id', node.data.id );
          xw.writeAttributeString( 'label', node.data.name );
          xw.writeAttributeString( 'name', 'base' );

              xw.writeStartElement( 'att' );
              xw.writeAttributeString( 'label', 'gene_name' );
              xw.writeAttributeString( 'name', 'gene_name' );
              xw.writeAttributeString( 'value', node.data.gene_name );
              xw.writeAttributeString( 'type', 'string');
              xw.writeEndElement();

                xw.writeStartElement( 'graphics' );
                xw.writeAttributeString( 'width', '1' );
                xw.writeAttributeString( 'fill', __convertColor(node.data.current_color) );
                xw.writeAttributeString( 'outline', "#000000" );
                xw.writeAttributeString( 'x', node.position.x);
                xw.writeAttributeString( 'y', node.position.y);
                xw.writeAttributeString( 'h', '30.0');
                xw.writeAttributeString( 'w', '30.0');
                xw.writeAttributeString( 'type', __convertShape(node.data.current_shape) );

                  xw.writeStartElement( 'att' );
                  xw.writeAttributeString( 'name', 'cytoscapeNodeGraphicsAttributes' );
                      xw.writeStartElement( 'att' );
                      xw.writeAttributeString( 'name', 'nodeTransparency' );
                      xw.writeAttributeString( 'value', '1.0' );
                      xw.writeEndElement();

                      xw.writeStartElement( 'att' );
                      xw.writeAttributeString( 'name', 'nodeLabelFont' );
                      xw.writeAttributeString( 'value', 'Default-0-12' );
                      xw.writeEndElement();

                      xw.writeStartElement( 'att' );
                      xw.writeAttributeString( 'name', 'borderLineType' );
                      xw.writeAttributeString( 'value', 'solid' );
                      xw.writeEndElement();
                  xw.writeEndElement();

                xw.writeEndElement();

          xw.writeEndElement();
        });

        data.elements.edges.forEach( function(edge) {
          xw.writeStartElement( 'edge' );
          xw.writeAttributeString( 'id', edge.data.id );
          xw.writeAttributeString( 'label', edge.data.id );
          xw.writeAttributeString( 'source', edge.data.source );
          xw.writeAttributeString( 'target', edge.data.target );

            xw.writeStartElement( 'graphics' );
            xw.writeAttributeString( 'width', edge.data.current_width.replace('px', '') );
            xw.writeAttributeString( 'fill', __convertColor(edge.data.current_color) );
            xw.writeEndElement();

          xw.writeEndElement();

        });

    xw.writeEndElement();
    xw.writeEndDocument();

    var output = xw.flush();

    xw.close();

    return output;
}