$(function(){
    // Used for collapsable box,
    // you can refer this in find-coach/coach_profile in coach experience section
    $("body .collapsable-box").each(function(){
        var thispanel = $(this);
        var originalHeight = thispanel.height();
        
        if(thispanel.height() > 90){
            thispanel.addClass('blur');
            thispanel.height('90');
        }

        $('.more').click(function(){
            thispanel.height(originalHeight);
            thispanel.removeClass('blur');
        })
    });

    // Sticky top menu on scrolling down
    // at this time only apply on homepage with 'on-home' class
    // Animate top menu when scrolling down
    $(document).bind("scroll", function() {
        // Set height limit to fix/unfix div
        if($(this).scrollTop() > 350){
            $('.on-home').addClass('fixed');
        }
        else{
            $('.on-home').removeClass('fixed');
        }
    });

    // Activate Ion.RangeSlider with options

});