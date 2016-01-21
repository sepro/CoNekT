$( document ).ready(function() {

    function update( panel ){
        var base_url = panel.attr( "base-url" );
        var page_count = parseInt(panel.attr( "page-count" ));
        var page = parseInt(panel.attr( "current_page"));

        panel.html('<br /><br /><div id="loading" class="pagination"><i class="fa fa-refresh fa-spin"></i></div>');
        panel.load( base_url + page );

        if (page == 1)
        {
            panel.parent().find( ".planet-pagination-first" ).attr("disabled", true);
            panel.parent().find( ".planet-pagination-back" ).attr("disabled", true);
        } else {
            panel.parent().find( ".planet-pagination-first" ).attr("disabled", false);
            panel.parent().find( ".planet-pagination-back" ).attr("disabled", false);
        }

        if (page == page_count)
        {
            panel.parent().find( ".planet-pagination-last" ).attr("disabled", true);
            panel.parent().find( ".planet-pagination-next" ).attr("disabled", true);
        } else {
            panel.parent().find( ".planet-pagination-last" ).attr("disabled", false);
            panel.parent().find( ".planet-pagination-next" ).attr("disabled", false);
        }
    }

    $('.planet-pagination').each(function() {
        update($( this ));
    });

    $( ".planet-pagination-first" ).click( function () {
        var panel = $( this ).closest('.planet-pagination-container').find('.planet-pagination');
        panel.attr( "current_page", 1);
        update(panel);
    });

    $( ".planet-pagination-last" ).click( function () {
        var panel = $( this ).closest('.planet-pagination-container').find('.planet-pagination');
        var page_count = parseInt(panel.attr( "page-count" ));
        panel.attr( "current_page", page_count);
        update(panel);
    });

    $( ".planet-pagination-next" ).click( function () {
        var panel = $( this ).closest('.planet-pagination-container').find('.planet-pagination');
        var page_count = parseInt(panel.attr( "page-count" ));
        var current_page = parseInt(panel.attr( "current_page"));
        if (current_page < page_count)
        {
            panel.attr( "current_page", current_page + 1);
        }
        update(panel);
    });

    $( ".planet-pagination-back" ).click( function () {
        var panel = $( this ).closest('.planet-pagination-container').find('.planet-pagination');
        var current_page = parseInt(panel.attr( "current_page"));
        if (current_page > 1)
        {
            panel.attr( "current_page", current_page - 1);
        }
        update(panel);
    });
});