$( document ).ready(function() {
    var current_page = 1;
    var base_url = $('#genes').attr( "base-url" );
    var loader_url = $('#genes').attr( "loader-url" );

    $( "#genes" ).html('<div class="loading-indication"><img src="'+loader_url+'" /> Loading...</div>');
    $( "#genes" ).load( base_url + current_page );

    $( "#page-next" ).click( function () {
        current_page++;
        $( "#genes" ).html('<div class="loading-indication"><img src='+loader_url+' /> Loading...</div>');
        $( "#genes" ).load( base_url + current_page );
    });
});