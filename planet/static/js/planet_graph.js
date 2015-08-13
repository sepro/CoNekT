$(function(){ // on dom ready

url = $('#cy').attr( "json" );

$('#cy').cytoscape({
  style: cytoscape.stylesheet()
    .selector('node')
      .css({
        'content': 'data(gene_name)',
        'text-valign': 'center',
        'color': 'white',
        'text-outline-width': 1,
        'text-outline-color': '#888'
      })
    .selector('node[node_type = "query"]')
      .css({
        'color': 'black',
        'text-outline-width': 2,
        'text-outline-color': '#EEE'
      })
    .selector('edge')
      .css({
        'curve-style': 'haystack',
        'opacity': 0.75,
      })
    .selector(':selected')
      .css({
        'border-width':'6px',
        'border-color':'#AAD8FF',
        'border-opacity':'0.5',
        'background-color':'#77828C',
        'line-color': 'black',
      }),
  
  elements: $.getJSON(url),
  layout: {
    name: 'concentric',
    padding: 20
  },
  
  // on graph initial layout done (could be async depending on layout...)
  ready: function(){
    window.cy = this;
    
    // giddy up...


    cy.nodes().forEach(function(n){
    var g = n.data('gene_link');

    n.qtip({
      content: [
        {
          platform: 'Planet',
          name: n.data('gene_name'),
          url: g
        }
      ].map(function( link ){
        return link.platform + ': <a href="' + link.url + '">' + link.name + '</a>';
      }).join('<br />\n'),
      position: {
        my: 'bottom center',
        at: 'top center'
      },
      style: {
        classes: 'qtip-bootstrap',
        tip: {
          width: 16,
          height: 8
        }
      }
    });
  });

  }
});

}); // on dom ready