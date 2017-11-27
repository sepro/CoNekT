/*global $, document */
$(document).ready(function () {
    'use strict';
    function update(panel) {
        var base_url = panel.attr("base-url"),
            page_count = parseInt(panel.attr("page-count"), 10),
            page = parseInt(panel.attr("current_page"), 10),
            key = panel.attr("key") !== 'undefined' ? panel.attr("key") :  "gsap_loader_",
            page_count = page_count >=0 ? page_count : 10000; // If pagecount is not known, very large number

        panel.html(get_loader_svg(key)).promise().done(function(){
        init_planet_loader(key);
        panel.load(base_url + page, function() {
            //console.log("Finished loading panel");
            init_qtip();
        });
    });


        if (page === 1) {
            panel.parent().find(".planet-pagination-first").attr("disabled", true);
            panel.parent().find(".planet-pagination-back").attr("disabled", true);
        } else {
            panel.parent().find(".planet-pagination-first").attr("disabled", false);
            panel.parent().find(".planet-pagination-back").attr("disabled", false);
        }

        if (page === page_count) {
            panel.parent().find(".planet-pagination-last").attr("disabled", true);
            panel.parent().find(".planet-pagination-next").attr("disabled", true);
        } else {
            panel.parent().find(".planet-pagination-last").attr("disabled", false);
            panel.parent().find(".planet-pagination-next").attr("disabled", false);
        }
    }

    $(".planet-pagination").each(function () {
        update($(this));
    });

    $(".planet-pagination-first").click(function () {
        var panel = $(this).closest(".planet-pagination-container").find(".planet-pagination");
        panel.attr("current_page", 1);
        update(panel);
    });

    $(".planet-pagination-last").click(function () {
        var panel = $(this).closest(".planet-pagination-container").find(".planet-pagination"),
            page_count = parseInt(panel.attr("page-count"), 10);
        page_count = page_count >=0 ? page_count : 10000; // If pagecount is not known, very large number
        panel.attr("current_page", page_count);
        update(panel);
    });

    $(".planet-pagination-next").click(function () {
        var panel = $(this).closest(".planet-pagination-container").find(".planet-pagination"),
            page_count = parseInt(panel.attr("page-count"), 10),
            current_page = parseInt(panel.attr("current_page"), 10);
        page_count = page_count >=0 ? page_count : 10000; // If pagecount is not known, very large number
        if (current_page < page_count) {
            panel.attr("current_page", current_page + 1);
        }
        update(panel);
    });

    $(".planet-pagination-back").click(function () {
        var panel = $(this).closest(".planet-pagination-container").find(".planet-pagination"),
            current_page = parseInt(panel.attr("current_page"), 10);
        if (current_page > 1) {
            panel.attr("current_page", current_page - 1);
        }
        update(panel);
    });
});
