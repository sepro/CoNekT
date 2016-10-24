var cy;
var initial_json;

$(function(){ // on dom ready

var url = $('#cy').attr( "json" );
var cycss_url = $('#cy').attr( "cycss" );

cy = cytoscape({
  container: document.getElementById('cy'),
  style: $.get(cycss_url),
  elements: url !== undefined ? $.getJSON(url) : graph_data,
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
        }]

        if (typeof n.data('profile_link') !== 'undefined') {
            content.push({value: 'Profile : <a href="' + n.data('profile_link') + '">' + n.data('id') + '</a>'});
        }

        if (typeof n.data('cluster_id') !== 'undefined') {
            content.push({value: 'Cluster : <a href="' + n.data('cluster_url') + '">' + n.data('cluster_name') + '</a>'});
        }

        if (typeof n.data('spm_condition') !== 'undefined') {
            content.push({value: 'Expression specificity : ' + n.data('spm_condition') + '(' + n.data('spm_score').toFixed(2) + ')'});
        }

        content.push(
        {
          value: n.data('family_name') !== null ? 'Family : <a href="' + n.data('family_url') + '">' + n.data('family_name') + '</a>' : '<span class="text-muted">No family found</span>'
        }, {
          value: n.data('family_clade') !== 'None' ? 'Clade : <strong>' + n.data('family_clade') + '</strong>' : '<span class="text-muted">No clade assigned</span>'
        });



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
        }];

    if (typeof e.data('profile_comparison') !== 'undefined') {
        content.push({value: '<a href="' + e.data('profile_comparison') + '">Compare profiles</a>'});
    }

    if (typeof e.data('link_score') !== 'undefined') {
    content.push({ value: 'Link Score: ' + e.data('link_score') });
    }

    if (typeof e.data('link_pcc') !== 'undefined') {
        if (e.data('link_pcc') !== null) {
            content.push({ value: 'PCC: ' + e.data('link_pcc').toFixed(3) });
        }
    }

    if (typeof e.data('depth') !== 'undefined') {
    content.push({ value: 'Depth: ' + e.data('depth') });
    }

    if (typeof e.data('ecc_score') !== 'undefined') {
    content.push({ value: 'ECC: ' + e.data('ecc_score').toFixed(2) });
    }


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
        var svg_families = [];
        var svg_labels = [];
        var svg_species = [];
        var svg_spm = [];
        var svg_clusters = [];
        cy.nodes('[^compound]').forEach(function(n){
            family_color = n.data('family_color');
            family_shape = n.data('family_shape');
            family = n.data('family_name');

            lc_color = n.data('lc_color');
            lc_shape = n.data('lc_shape');
            lc_label = n.data('lc_label');

            spm_color = n.data('spm_condition_color');
            spm_shape = n.data('spm_condition_shape');
            spm = n.data('spm_condition');

            cluster_color = n.data('cluster_color');
            cluster_shape = n.data('cluster_shape');
            cluster = n.data('cluster_name');

            species = n.data('species_name');
            species_color = n.data('species_color');
            species_shape = 'ellipse';

            if (species_color !== undefined) {
                if (!(species_color in svg_species)) {
                    svg_species[species_color] = []
                }
                svg_species[species_color][species_shape] = species;
            }

            if (family_color !== undefined){
                if (!(family_color in svg_families)) {
                    svg_families[family_color] = []
                }
                svg_families[family_color][family_shape] = family;
            }

            if (lc_color !== undefined){
                if (!(lc_color in svg_labels)) {
                    svg_labels[lc_color] = []
                }
                svg_labels[lc_color][lc_shape] = lc_label;
            }

            if (cluster_color !== undefined){
                if (!(cluster_color in svg_clusters)) {
                    svg_clusters[cluster_color] = []
                }
                svg_clusters[cluster_color][cluster_shape] = cluster;
            }

            if (spm_color !== undefined){
                if (!(spm_color in svg_spm)) {
                    svg_spm[spm_color] = []
                }
                svg_spm[spm_color][spm_shape] = spm;
            }


        }); //end cy.nodes.forEach

        if (Object.keys(svg_labels) !== ["undefined"]) {generate_legend(svg_labels, 'lc_color');}
        if (Object.keys(svg_families) !== ["undefined"]) { generate_legend(svg_families, 'family_color');}
        if (Object.keys(svg_clusters) !== ["undefined"]) { generate_legend(svg_clusters, 'cluster_color');}
        if (Object.keys(svg_spm) !== ["undefined"]) { generate_legend(svg_spm, 'spm_color');}
        if (Object.keys(svg_species) !== ["undefined"]) { generate_legend(svg_species, 'species_color'); }

        console.log("Successfully generated legend...");
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
 } else if ($( this ).attr( 'attr' ) === 'spm_color' ) {
    $('.cy-node-shape[attr="spm_shape"]').click();
 } else if ($( this ).attr( 'attr' ) === 'cluster_color' ) {
    $('.cy-node-shape[attr="cluster_shape"]').click();
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
               animate: true,
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

  document.body.appendChild(download);
  download.click();
  document.body.removeChild(download);
})

$('#cy-download-img-lowres').click(function(ev) {
  ev.preventDefault();
  var png64 = cy.png({scale: 1, bg: "#FFFFFF"});

  var download = document.createElement('a');
  download.href = png64;
  download.download = 'cytoscape-lowres.png';

  document.body.appendChild(download);
  download.click();
  document.body.removeChild(download);
})

$('#cy-download-json').click(function(ev) {
  ev.preventDefault();
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(initial_json));
  element.setAttribute('download', "cytoscape.json");

  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
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

  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
})

$('#cy-download-xgmml').click(function(ev) {
  ev.preventDefault();

  xgmml = writeXGMML(cy);

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(xgmml));
  element.setAttribute('download', "cytoscape.xgmml");

  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
})

$('#cy-download-svg').click(function(ev) {
  ev.preventDefault();

  svg = writeSVG(cy);

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(svg));
  element.setAttribute('download', "cytoscape.svg");

  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
})

$('#cy-download-svg-with-legend').click(function(ev) {
  ev.preventDefault();

  svg_out = Pablo(writeSVG(cy));
  legend = Pablo(svg_legend.markup(false));

  var graph_height = parseInt(Pablo.getAttributes(svg_out[0])['height'].replace('px',''));
  var graph_width = parseInt(Pablo.getAttributes(svg_out[0])['width'].replace('px',''));
  var legend_height = parseInt(Pablo.getAttributes(legend[0])['height'].replace('px',''));
  var legend_width = parseInt(Pablo.getAttributes(legend[0])['width'].replace('px',''));
  var total_height = graph_height + 20 + legend_height;
  var total_width = (graph_width > legend_width ? graph_width : legend_width);

  l = svg_out.g({'id':'legend'}).transform('translate', 0, graph_height+20);

  l.append(legend);

  svg_out.attr('viewBox', '0 0 ' + total_width + ' ' + total_height);
  svg_out.attr('height', total_height + 'px');
  svg_out.attr('width', total_width + 'px');

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(svg_out));
  element.setAttribute('download', "cytoscape_w_legend.svg");

  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
})

$('#cy-download-png-with-legend').click(function(ev) {
  ev.preventDefault();

  svg_out = Pablo(writeSVG(cy));
  legend = Pablo(svg_legend.markup(false));

  var graph_height = parseInt(Pablo.getAttributes(svg_out[0])['height'].replace('px',''));
  var graph_width = parseInt(Pablo.getAttributes(svg_out[0])['width'].replace('px',''));
  var legend_height = parseInt(Pablo.getAttributes(legend[0])['height'].replace('px',''));
  var legend_width = parseInt(Pablo.getAttributes(legend[0])['width'].replace('px',''));
  var total_height = graph_height + 20 + legend_height;
  var total_width = (graph_width > legend_width ? graph_width : legend_width);

  l = svg_out.g({'id':'legend'}).transform('translate', 0, graph_height+20);

  l.append(legend);

  svg_out.attr('viewBox', '0 0 ' + total_width + ' ' + total_height);
  svg_out.attr('height', total_height + 'px');
  svg_out.attr('width', total_width + 'px');

  svg_out.dataUrl('png', function(dataUrl){
      var element = document.createElement('a');
      element.setAttribute('href', dataUrl);
      element.setAttribute('download', "cytoscape__w_legend.png");
      element.setAttribute('style', 'display:none');

      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    });
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

