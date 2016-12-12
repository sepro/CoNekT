function init_planet_loader() {
    var tl = new TimelineMax({repeat:-1, repeatDelay:1}),
        stem = document.getElementById("stem"),
        leafs_01 = document.getElementById("leaf_pair_01"),
        leafs_02 = document.getElementById("leaf_pair_02"),
        leafs_03 = document.getElementById("leaf_pair_03"),
        leafs_04 = document.getElementById("leaf_pair_04"),
        leafs_05 = document.getElementById("leaf_pair_05");

    tl.set([leafs_01,leafs_02,leafs_03,leafs_04,leafs_05], {scale:0, transformOrigin:"50% 50%"})
      .to(stem , 1.2, {  opacity:1 , ease:Power1.easeInOut })

      .to(leafs_01, 1.2, { scale:1, ease:Elastic.easeInOut }, "-=0.7")
      .to(leafs_01 , 1, {  opacity:1 , ease:Power1.easeInOut }, "-=1")

      .to(leafs_02, 1.2, { scale:1, ease:Elastic.easeInOut }, "-=0.7")
      .to(leafs_02 , 1, {  opacity:1 , ease:Power1.easeInOut }, "-=1")

      .to(leafs_03, 1.2, { scale:1, ease:Elastic.easeInOut }, "-=0.7")
      .to(leafs_03 , 1, {  opacity:1 , ease:Power1.easeInOut }, "-=1")

      .to(leafs_04, 1.2, { scale:1, ease:Elastic.easeInOut }, "-=0.7")
      .to(leafs_04 , 1, {  opacity:1 , ease:Power1.easeInOut }, "-=1")

      .to(leafs_05, 1.2, { scale:1, ease:Elastic.easeInOut }, "-=0.7")
      .to(leafs_05 , 1, {  opacity:1 , ease:Power1.easeInOut }, "-=1");

    tl.timeScale(1.5);
};