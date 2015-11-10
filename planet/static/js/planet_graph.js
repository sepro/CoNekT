var cy;
var initial_json;

$(function(){ // on dom ready

var url = $('#cy').attr( "json" );

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
        'opacity': 0.7,
        'width': 1,
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
    var loading = document.getElementById('loading');
    loading.classList.add('loaded');
    window.cy = this;

    initial_json = JSON.stringify(cy.json(), null, '\t');

    cy.nodes().forEach(function(n){
    // code to add tooltips to the selected node
    var content = [
        {
          value: 'Planet : <a href="' + n.data('gene_link') + '">' + n.data('gene_name') + '</a>'
        }, {
          value: 'Profile : <a href="' + n.data('profile_link') + '">' + n.data('id') + '</a>'
        }, {
          value: 'Clade : <strong>' + n.data('family_clade') + '</strong>'
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

    cy.edges().forEach(function(e){
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

  }
});


$('.cy-node-color').click(function() {
 var attr = $( this ).attr( 'attr' );
 if (attr === "neighbors" || attr === "family_clade_count") {
    cy.nodes().style('background-color', function( ele ){
        if(attr === "family_clade_count") {
          if (ele.data("family_clade") === "None") {
            return "#CCC";
          } else {
            return valueToColor(15 - (ele.data(attr)*3));
          }

        } else {
          return valueToColor(ele.data(attr));
        }
    });
  } else {
    cy.nodes().style('background-color', function( ele ){ return ele.data(attr)});
  }
})

$('.cy-node-shape').click(function() {
  var attr = $( this ).attr( 'attr' );
  cy.nodes().style('shape', function( ele ){ return ele.data(attr)});
})

$('.cy-edge-color').click(function() {
  var attr = $( this ).attr( 'attr' );
  if (attr === "link_score") {
    cy.edges().style('line-color', function( ele ){
        var value = Math.floor(((31 - ele.data(attr))/30)*16);
        return valueToColor(value);
      });
  }
  else{
    cy.edges().style('line-color', function( ele ){ return ele.data(attr)});
  }

})

$('.cy-edge-width').click(function() {
  var attr = $( this ).attr( 'attr' );
  if (attr === "default") {
    cy.edges().style('width', 1);
  } else if (attr === "depth")
  {
    cy.edges().style('width', function( ele ){ return (3 - ele.data('depth'))/2});
  }

})

$('#cy-edge-score').on("slideStop", function(slideEvt) {
    var cutoff = slideEvt.value;

    cy.edges("[link_score>" + cutoff + "]").style('display', 'none');
    cy.edges("[link_score<=" + cutoff + "]").style('display', 'element');
})

$('.cy-depth-filter').click(function() {
    $( '.cy-depth-filter' ).removeClass( 'active' );
    $( this ).addClass( 'active' );

    var cutoff = $( this ).attr( 'cutoff' );

    cy.nodes("[depth>" + (cutoff-1) + "]").style('display', 'none');
    cy.nodes("[depth<=" + (cutoff-1) + "]").style('display', 'element');

    cy.edges("[depth>" + cutoff + "]").style('display', 'none');
    cy.edges("[depth<=" + cutoff + "]").style('display', 'element');
})

$('.cy-layout').click(function() {
    var layout = $( this ).attr( 'layout' );

    cy.layout({ name: layout });
})

$(".cy-option-menu li a").click(function(){
  $(this).parents(".btn-group").find('.btn').html($(this).text() + ' <span class="caret"></span>');
  $(this).parents(".btn-group").find('.btn').val($(this).data('value'));
});

$('#cy-download-img-hires').click(function() {

  var png64 = cy.png({scale: 4, bg: "#FFFFFF"});

  var download = document.createElement('a');
  download.href = png64;
  download.download = 'cytoscape-hires.png';
  download.click();
})

$('#cy-download-img-lowres').click(function() {

  var png64 = cy.png({scale: 1, bg: "#FFFFFF"});

  var download = document.createElement('a');
  download.href = png64;
  download.download = 'cytoscape-lowres.png';
  download.click();
})

$('#cy-download-json').click(function() {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(initial_json));
  element.setAttribute('download', "cytoscape.json");

  element.click();
})

$('#cy-download-jsoncy').click(function() {
  var eles = cy.elements()

  eles.each( function(i, ele) {
    if (ele.isNode()) {
      ele.data('current_color', ele.style('background-color'));
      ele.data('current_shape', ele.style('shape'));
    } else if (ele.isEdge()) {
      ele.data('current_color', ele.style('line-color'));
      ele.data('current_width', ele.style('width'));
    }
  });


  json = JSON.stringify(cy.json(), null, '\t');

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(json));
  element.setAttribute('download', "cytoscape_full.json");

  element.click();

})


function valueToColor(value)
{
  value = value > 15 ? 15 : value;
  value = value < 1 ? 1 : value;
  if (value === null)  {
    return "#FFF";
  } else {
    var color = "#" + (15-value).toString(16) + "" + value.toString(16) + "0";
    return color;
  }
}

}); // end on dom ready

