$( document ).ready(function() {
    var current_page = 1;
    var base_url = $('#planet-pagination').attr( "base-url" );
    var page_count = $('#planet-pagination').attr( "page-count" );

    function update(page){
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

    update(current_page);

    $( "#planet-pagination-first" ).click( function () {
        current_page = 1;
        update(current_page);
    });

    $( "#planet-pagination-last" ).click( function () {
        current_page = page_count;
        update(current_page);
    });

    $( "#planet-pagination-next" ).click( function () {
        if (current_page < page_count)
        {
            current_page++;
        }
        update(current_page);
    });

    $( "#planet-pagination-back" ).click( function () {
        if (current_page > 1)
        {
            current_page--;
        }
        update(current_page);
    });
});