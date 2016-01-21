$( document ).ready(function() {
    $('#planet-pagination').attr( "current_page", 1 );

    function update(){
        var base_url = $('#planet-pagination').attr( "base-url" );
        var page_count = parseInt($('#planet-pagination').attr( "page-count" ));
        var page = parseInt($('#planet-pagination').attr( "current_page"));

        $( "#planet-pagination" ).html('<br /><br /><div id="loading" class="pagination"><i class="fa fa-refresh fa-spin"></i></div>');
        $( "#planet-pagination" ).load( base_url + page );

        if (page == 1)
        {
            $( "#planet-pagination-first" ).attr("disabled", true);
            $( "#planet-pagination-back" ).attr("disabled", true);
        } else {
            $( "#planet-pagination-first" ).attr("disabled", false);
            $( "#planet-pagination-back" ).attr("disabled", false);
        }

        if (page == page_count)
        {
            $( "#planet-pagination-last" ).attr("disabled", true);
            $( "#planet-pagination-next" ).attr("disabled", true);
        } else {
            $( "#planet-pagination-last" ).attr("disabled", false);
            $( "#planet-pagination-next" ).attr("disabled", false);
        }

    }

    update();

    $( "#planet-pagination-first" ).click( function () {
        $('#planet-pagination').attr( "current_page", 1);
        update();
    });

    $( "#planet-pagination-last" ).click( function () {
        var page_count = parseInt($('#planet-pagination').attr( "page-count" ));
        $('#planet-pagination').attr( "current_page", page_count);
        update();
    });

    $( "#planet-pagination-next" ).click( function () {
        var page_count = parseInt($('#planet-pagination').attr( "page-count" ));
        var current_page = parseInt($('#planet-pagination').attr( "current_page"));
        if (current_page < page_count)
        {
            $('#planet-pagination').attr( "current_page", current_page + 1);
        }
        update();
    });

    $( "#planet-pagination-back" ).click( function () {
        var current_page = parseInt($('#planet-pagination').attr( "current_page"));
        if (current_page > 1)
        {
            $('#planet-pagination').attr( "current_page", current_page - 1);
        }
        update();
    });
});