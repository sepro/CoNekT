var cy;
var initial_json;

$(function(){ // on dom ready

var url = $('#cy').attr( "json" );
var cycss_url = $('#cy').attr( "cycss" );

cy = cytoscape({
  container: document.getElementById('cy'),
  style: $.get(cycss_url),
  elements: $.getJSON(url),
  layout: {
    name: 'concentric',
    padding: 30,
    minNodeSpacing: 10,
    avoidOverlap: false
  },
  

  ready: function(){
    $('#loading').addClass('loaded')
    $('#legend').show();
    window.cy = this;

    initial_json = JSON.stringify(cy.json(), null, '\t');

    cy.nodes('[^compound]').forEach(function(n){
    // code to add tooltips to the selected node
    var content = [
        {
          value: n.data('gene_id') !== null ? 'Planet : <a href="' + n.data('gene_link') + '">' + n.data('gene_name') + '</a>' : '<span class="text-muted">No sequence linked to probe</span>'
        },
        {
          value: n.data('description') !== null ? '<strong>' + n.data('description') + '</strong><br />' : '<span class="text-muted">No description available</span>'
        },
        {
          value: n.data('tokens') !== null ? 'Other names: <strong>' + n.data('tokens') + '</strong><br />' : '<span class="text-muted">No alias available</span>'
        },
        {
          value: 'Profile : <a href="' + n.data('profile_link') + '">' + n.data('id') + '</a>'
        }, {
          value: n.data('family_name') !== null ? 'Family : <a href="' + n.data('family_url') + '">' + n.data('family_name') + '</a>' : '<span class="text-muted">No family found</span>'
        }, {
          value: n.data('family_clade') !== 'None' ? 'Clade : <strong>' + n.data('family_clade') + '</strong>' : '<span class="text-muted">No clade assigned</span>'
        }
      ]


    n.qtip({
      content: content.map(function( item ){
        return item.value;
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

    cy.edges('[^homology]').forEach(function(e){
    // code to add tooltips to the selected node
    var content = [{
          value: 'Edge: ' + e.data('source') + ' and ' + e.data('target'),
        }, {
          value: '<a href="' + e.data('profile_comparison') + '">Compare profiles</a>'
        }, {
          value: 'Link Score: ' + e.data('link_score')
        }, {
          value: 'Depth: ' + e.data('depth')
        }
      ]


    e.qtip({
      content: content.map(function( item ){
        return item.value;
      }).join('<br />\n'),
      position: {
        my: 'bottom center',
        at: 'center center'
      },
      style: {
        classes: 'qtip-bootstrap',
        tip: {
          width: 16,
          height: 8
        }
      }
    });
  }); // end cy.edges.forEach...

        // Fill data for legend
        svg_families = [];
        svg_labels = [];
        cy.nodes('[^compound]').forEach(function(n){
            family_color = n.data('family_color');
            family_shape = n.data('family_shape');
            family = n.data('family_name')
            lc_color = n.data('lc_color');
            lc_shape = n.data('lc_shape');
            lc_label = n.data('lc_label');

            if (!(family_color in svg_families)) {
                svg_families[family_color] = []
            }
            svg_families[family_color][family_shape] = family;

            if (!(lc_color in svg_labels)) {
                svg_labels[lc_color] = []
            }
            svg_labels[lc_color][lc_shape] = lc_label;

        }); //end cy.nodes.forEach

        generate_legend(svg_labels, 'lc_color');
        generate_legend(svg_families, 'family_color');
  }
});


$('.cy-node-color').click(function(ev) {
  ev.preventDefault();
  $( this ).closest('.cy-option-menu').find('.cy-node-color').each(function () {
    cy.nodes('[^compound]').removeClass( $( this ).attr( 'attr' ) );
  });
 cy.nodes('[^compound]').addClass( $( this ).attr( 'attr' ) );

 if ($( this ).attr( 'attr' ) === 'family_color' ) {
    $('.cy-node-shape[attr="family_shape"]').click();
 } else if ($( this ).attr( 'attr' ) === 'lc_color' ) {
    $('.cy-node-shape[attr="lc_shape"]').click();
 } else {
    $('.cy-node-shape[attr="shape"]').click();
 }

})

$('.cy-node-shape').click(function(ev) {
  ev.preventDefault();
  $( this ).closest('.cy-option-menu').find('.cy-node-shape').each(function () {
    cy.nodes('[^compound]').removeClass( $( this ).attr( 'attr' ) );
  });
 cy.nodes('[^compound]').addClass( $( this ).attr( 'attr' ) );
})

$('.cy-edge-color').click(function(ev) {
  ev.preventDefault();
  $( this ).closest('.cy-option-menu').find('.cy-edge-color').each(function () {
    cy.edges('[^homology]').removeClass( $( this ).attr( 'attr' ) );
  });
 cy.edges('[^homology]').addClass( $( this ).attr( 'attr' ) );
})

$('.cy-edge-width').click(function(ev) {
  ev.preventDefault();
  $( this ).closest('.cy-option-menu').find('.cy-edge-width').each(function () {
    cy.edges('[^homology]').removeClass( $( this ).attr( 'attr' ) );
  });
 cy.edges('[^homology]').addClass( $( this ).attr( 'attr' ) );
})

$('#cy-edge-score').on("slideStop", function(slideEvt) {
    var cutoff = slideEvt.value;

    cy.edges("[link_score>" + cutoff + "]").style('display', 'none');
    cy.edges("[link_score<=" + cutoff + "]").style('display', 'element');
})

$('.cy-depth-filter').click(function(ev) {
    ev.preventDefault();
    $( '.cy-depth-filter' ).removeClass( 'active' );
    $( this ).addClass( 'active' );

    var cutoff = $( this ).attr( 'cutoff' );

    cy.nodes("[depth>" + (cutoff-1) + "]").style('display', 'none');
    cy.nodes("[depth<=" + (cutoff-1) + "]").style('display', 'element');

    cy.edges("[depth>" + cutoff + "]").style('display', 'none');
    cy.edges("[depth<=" + cutoff + "]").style('display', 'element');
})

$('.cy-layout').click(function(ev) {
    ev.preventDefault();
    var layout = $( this ).attr( 'layout' );

    cy.layout({name: layout,
               padding: 30,
               minNodeSpacing: 10,
               animate: false,
               avoidOverlap: false,
               //cose settings
               nodeOverlap: 1,
               idealEdgeLength: function( edge ){ return 5; },
               edgeElasticity: function( edge ){ return 10; }
               });
})

$(".cy-option-menu li a").click(function(){
  $(this).parents(".btn-group").find('.btn').html($(this).text() + ' <span class="caret"></span>');
  $(this).parents(".btn-group").find('.btn').val($(this).data('value'));
});

$("#cy-search").click(function(ev){
  ev.preventDefault();
  var term = $("#cy-search-term").val().trim().toLowerCase();
  var url = $( this ).attr( 'search-url' );


  cy.nodes('[^compound]').toggleClass('found', false);
  var valid_genes = []
  $.getJSON(url+term, function(data){
         var i=0;
         for(i=0;i<data.length;i++){
            valid_genes.push(data[i])
        }
        })
  .done(function(){
    cy.nodes('[^compound]').each( function(i, node) {
      if(node.data('gene_name').toLowerCase() === term ||
         node.data('name').toLowerCase() === term ||
         (node.data('family_name') !== null && node.data('family_name').toLowerCase() === term) ||
         (typeof node.data('interpro') !== 'undefined' && node.data('interpro').indexOf(term.toUpperCase()) > -1) ||
         valid_genes.indexOf(node.data('gene_id')) > -1
         ) {
        node.toggleClass('found');

      }
    });

  });


});

$('#cy-download-img-hires').click(function(ev) {
  ev.preventDefault();
  var png64 = cy.png({scale: 4, bg: "#FFFFFF"});

  var download = document.createElement('a');
  download.href = png64;
  download.download = 'cytoscape-hires.png';
  download.click();
})

$('#cy-download-img-lowres').click(function(ev) {
  ev.preventDefault();
  var png64 = cy.png({scale: 1, bg: "#FFFFFF"});

  var download = document.createElement('a');
  download.href = png64;
  download.download = 'cytoscape-lowres.png';
  download.click();
})

$('#cy-download-json').click(function(ev) {
  ev.preventDefault();
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(initial_json));
  element.setAttribute('download', "cytoscape.json");

  element.click();
})

$('#cy-download-jsoncy').click(function(ev) {
  ev.preventDefault();
  var eles = cy.elements()

  eles.each( function(i, ele) {
    if (ele.isNode()) {
      ele.data('current_color', ele.renderedStyle('background-color'));
      ele.data('current_shape', ele.renderedStyle('shape'));
    } else if (ele.isEdge()) {
      ele.data('current_color', ele.renderedStyle('line-color'));
      ele.data('current_width', ele.renderedStyle('width'));
    }
  });


  json = JSON.stringify(cy.json(), null, '\t');

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(json));
  element.setAttribute('download', "cytoscape_full.json");

  element.click();

})

$('#cy-download-xgmml').click(function(ev) {
  ev.preventDefault();
  var eles = cy.elements();

  eles.each( function(i, ele) {
    if (ele.isNode()) {
      ele.data('current_color', ele.renderedStyle('background-color'));
      ele.data('current_shape', ele.renderedStyle('shape'));
    } else if (ele.isEdge()) {
      ele.data('current_color', ele.renderedStyle('line-color'));
      ele.data('current_width', ele.renderedStyle('width'));
    }
  });

  xgmml = writeXGMML(cy.json());

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(xgmml));
  element.setAttribute('download', "cytoscape.xgmml");

  element.click();
})

$('#cy-download-svg').click(function(ev) {
  ev.preventDefault();
  var eles = cy.elements();

  eles.each( function(i, ele) {
    if (ele.isNode()) {
      ele.data('current_color', ele.renderedStyle('background-color'));
      ele.data('current_shape', ele.renderedStyle('shape'));
    } else if (ele.isEdge()) {
      ele.data('current_color', ele.renderedStyle('line-color'));
      ele.data('current_width', ele.renderedStyle('width'));
    }
  });

  svg = writeSVG(cy.json());

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(svg));
  element.setAttribute('download', "cytoscape.svg");

  element.click();
})

$('#cy-reset').on('click', function(ev){
  ev.preventDefault();
  cy.animate({
    fit: {
      eles: cy.elements(),
      padding: 5
    },
    duration: 500
  });
});

}); // end on dom ready

