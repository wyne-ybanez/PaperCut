$(document).ready(function () {
    $('.sidenav').sidenav({edge: 'right'});
    $('textarea#post-content').characterCounter(); // Character counter
    $('select').formSelect(); // Form select
    $('.modal').modal(); // Initialize Modals 

    // Scroll effect Navbar interactivity
    function checkScroll(){
        var startY = $('.navbar').height() * 2; 

        if($(window).scrollTop() > startY){
            $('.fa-bars').addClass('scrolled');
            $('.nav-wrapper').addClass('scrolled');
            $('.brand-logo').removeClass('black-text');
            $('.nav-search-bar').addClass('white-text');
            $('.nav-search-icon').css('color','#fff');
        }else{
            $('.fa-bars').removeClass("scrolled");
            $('.nav-wrapper').removeClass('scrolled');
            $('.brand-logo').addClass('black-text');
            $('.nav-search-bar').removeClass('white-text');
            $('.nav-search-icon').css('color','#000');
        }
    }

    if($('.navbar').length > 0){
        $(window).on("scroll load resize", function(){
            checkScroll();
        });
    }    

    // Code Institute Validation Code
    validateMaterializeSelect();
    function validateMaterializeSelect() {
        let classValid = { "border-bottom": "1px solid #4caf50", "box-shadow": "0 1px 0 0 #4caf50" };
        let classInvalid = { "border-bottom": "1px solid #f44336", "box-shadow": "0 1px 0 0 #f44336" };
        if ($("select.validate").prop("required")) {
            $("select.validate").css({ "display": "block", "height": "0", "padding": "0", "width": "0", "position": "absolute" });
        }
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () { })) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }
});
