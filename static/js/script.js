$(document).ready(function () {
    $(".sidenav").sidenav({edge: "right"});
    $('textarea#post-content').characterCounter(); // Character counter
    $("select").formSelect();                      // Form select

    // Scroll effect interactivity - Editted: https://stackoverflow.com/questions/29646622/set-bootstrap-navbar-transparency-on-scroll
    function checkScroll(){
        var startY = $('.navbar').height() * 2; 

        if($(window).scrollTop() > startY){
            $('.fa-bars').addClass("scrolled");
        }else{
            $('.fa-bars').removeClass("scrolled");
        }
    }

    if($('.navbar').length > 0){
        $(window).on("scroll load resize", function(){
            checkScroll();
        });
    }    
});