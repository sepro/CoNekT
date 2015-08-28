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
  cy.nodes().style('background-color', function( ele ){ return ele.data(attr)});
})

$('.cy-edge-color').click(function() {
  attr = $( this ).attr( 'attr' );
  cy.edges().style('line-color', function( ele ){ return ele.data(attr)});
})

$('.cy-depth-filter').click(function() {
    $( '.cy-depth-filter' ).removeClass( 'active' );
    $( this ).addClass( 'active' );

    cutoff = $( this ).attr( 'cutoff' );

    cy.nodes("[depth>" + (cutoff-1) + "]").style('display', 'none');
    cy.nodes("[depth<=" + (cutoff-1) + "]").style('display', 'element');

    cy.edges("[depth>" + cutoff + "]").style('display', 'none');
    cy.edges("[depth<=" + cutoff + "]").style('display', 'element');
})

$('.cy-layout').click(function() {
    layout = $( this ).attr( 'layout' );

    cy.layout({ name: layout });
})



}); // on dom ready

$('#cy-download-img').click(function() {

  var png64 = cy.png();
  var canvas = document.getElementById("png-eg");

  var ctx = canvas.getContext("2d");

  var image = new Image();

  image.onload = function() {
    ctx.drawImage(image, 0, 0);
    setTimeout(image.onload,5000);
  };
  image.src = png64;

  var dt = canvas.toDataURL('image/png');
  this.href = dt.replace(/^data:image\/[^;]/, 'data:application/octet-stream');
})