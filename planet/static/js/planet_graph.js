var cy;

$(function(){ // on dom ready

url = $('#cy').attr( "json" );

cy = cytoscape({
  container: document.getElementById('cy'),
  style: cytoscape.stylesheet()
    .selector('node')
      .css({
        'content': 'data(gene_name)',
        'text-valign': 'center',
        'color': '#FFF',
        'background-color': 'data(color)',
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
        'width': 'mapData(depth, 2, 0, 1, 2)',
        'line-color': 'data(color)'
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
  

  ready: function(){
    window.cy = this;


    cy.nodes().forEach(function(n){
    // code to add tooltips to the selected node
    var content = [
        {
          platform: 'Planet',
          name: n.data('gene_name'),
          url: n.data('gene_link')
        }, {
          platform: 'Profile',
          name: n.data('id'),
          url: n.data('profile_link')
        }
      ]


    n.qtip({
      content: content.map(function( link ){
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


$('.cy-node-color').click(function() {

  attr = $( this ).attr( 'attr' );

  $('.cy-node-color').removeClass( 'active' );
  $( this ).addClass( 'active' );

  cy.nodes().forEach(function(n){
    n.style('background-color', n.data(attr))
    })
})

$('.cy-depth-filter').click(function() {
    $( '.cy-depth-filter' ).removeClass( 'active' );
    $( this ).addClass( 'active' );

    cutoff = $( this ).attr( 'cutoff' );

    cy.nodes().forEach(function(n){
      if (n.data('depth')> cutoff - 1)
      {
        n.style('display', 'none')
      } else {
        n.style('display', 'element')
      }
    })

    cy.edges().forEach(function(e){
      if (e.data('depth')> cutoff)
      {
        e.style('display', 'none')
      } else {
        e.style('display', 'element')
      }
    })
})

$('.cy-layout').click(function() {
    layout = $( this ).attr( 'layout' );

    cy.layout({ name: layout });
})

}); // on dom ready