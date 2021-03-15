{# This is the JavaScript portion of needful. This has been placed in a separate file
to make the JS development easier. This file is processed and inserted into the final
HTML output file, and should not be edited lest needful be broken forever. #}

var {{config_var}} = {
    "pageNumbers" : {{ page_numbers | lower() }},
    "width" : {{size[0]}},
    "height" : {{size[1]}},
    "autoScale" : {{ autoscale | lower() }}
}

// Define globals first:
var slideData = [
{% for slide in slides %}
    {
        "id" : "{{slide.id}}",
        "title" : "{{slide.title}}",
        "theme_id" : {{ "null" if slide.theme == None else '"' + slide.theme.id + '"'}},
        "html" : `{{ slide.html | replace("\\", "\\\\") }}`,
        "layout" : "grid-template-columns: repeat({{slide.n_cols}}, 1fr)",
        "plotly" : function plot() {
            {{slide.plotly_func}}
        },
        "purge" : function purge() {
            {{slide.purge_func}}
        },
        "pageNumber" : {{ config_var + ".pageNumbers" if slide.page_number == None else slide.page_number | lower() }},
        "disable_mathjax" : {{ slide.disable_mathjax | lower() }}
    } {% if not loop.last %},{% endif %}
{% endfor %}
];

var slideIndex = 0;
var maxIndex = slideData.length - 1;

// Map slide IDs to their position in the slideData array.
var slideIDToIndex = {};
for (var i = 0; i <= maxIndex; i++){
  var slideID = slideData[i].id;
  slideIDToIndex[slideID] = i;
}

// Create a dictionary containing CSS theme IDs and their variables.
var cssThemes = {
{% for theme in css_themes %}
    "{{theme.id}}" : {{theme.get_js()}}{% if not loop.last %},{% endif %}
{% endfor %}

}

// This is stupid, but for themes to work properly we need to extract all CSS :root variables
// and store them.
var initialCSS = Array.from(document.styleSheets).map( (style) => Array.from(style.cssRules) ).flat();

// Filter for :root, extract variables and their values, store in array.
var cssRootStyle = initialCSS.filter( (sel) => sel.selectorText == ":root" );
if (cssRootStyle.length > 0){
    cssRootStyle = cssRootStyle[0].style;
    var cssVarNames = Array.from(cssRootStyle).filter( (name) => name.startsWith("--") );

    // Create list of --name, value pairs, assign to "default" in cssThemes.
    cssThemes["default"] = cssVarNames.map( (name) => [name, cssRootStyle.getPropertyValue(name)] );
}
else
{
    cssThemes["default"] = [];
}

// Define functions:

function showSlide(slide, prevSlide) {
    // As implied, display the given slide.

    // Note: was getting nonspecific NS_ERROR_NOT_AVAILABLE on cssThemes.default.forEach... below, which *seem* to
    // disappear when this function is thrown into jQuery below. This is equivalent to $(document).ready(...).
    $(function() {

        if (prevSlide != null) {
            prevSlide.purge();
        }

        // Clear existing title, replace with new one.
        var titleSpan = $("#slide-title");
        titleSpan.empty();
        titleSpan.append(slide.title);

        // Clear existing content.
        var slideContent = $("#slide-content");
        slideContent.empty();

        // Update CSS grid layout/number of columns.
        slideContent.attr("style", slide.layout);

        // Apply default CSS theme before we show anything.
        cssThemes.default.forEach( ([name, val]) => cssRootStyle.setProperty(name, val) );

        // Apply slide's CSS theme, if one is set.
        if (slide.theme_id != null & cssThemes.default.length > 0) {
            cssThemes[slide.theme_id].forEach( ([name, val]) => cssRootStyle.setProperty(name, val) );
        }

        // Shove in new slide's HTML content, call plotting function.
        slideContent.append(slide.html);
        slide.plotly();

        // Update slide number.
        var slideNumber = $("#slide-number");
        slideNumber.empty();
        if (slide.pageNumber){
            slideNumber.append(slideIndex + 1);
        }

        // Typeset any maths that may be present.
        if (typeof MathJax !== "undefined" & !slide.disable_mathjax) {
          MathJax.typeset();
        }

        // Update content scaling if necessary. Note: if there's issues, this call
        // may be moved to some page ready event.
        scaleContent();
    });
}

function scaleContent(){
    // Update content scaling if we need to fit everything to screen.
    if (!{{config_var}}.autoScale) return;

    // First, fix size of the slide container.
    var slideContainer = $("#slide-container");
    slideContainer.css("width", {{config_var}}.width);
    slideContainer.css("height", {{config_var}}.height);

    // How much space do we have?
    var windowHeight = window.innerHeight;
    var windowWidth = window.innerWidth;

    var widthRatio = windowWidth / {{config_var}}.width;
    var heightRatio = windowHeight / {{config_var}}.height;

    var left = 0;
    var top = 0;

    if (widthRatio > heightRatio)
    {
        // Window is too wide for scaled height to fit without scrolling, therefore fix the height to windowHeight and
        // scale the width accordingly.
        var newWidth = heightRatio * {{config_var}}.width;
        left = 0.5 * (windowWidth - newWidth);
        transform = "scale(" + heightRatio + ")";
    }
    else
    {
        // Window is too tall for scaled width to fit without scrolling, therefore fix the width to windowWidth and
        // scale height accordingly.
        var newHeight = widthRatio * {{config_var}}.height;
        top = 0.5 * (windowHeight - newHeight);
        transform = "scale(" + widthRatio + ")";
    }

    slideContainer.css("left", left);
    slideContainer.css("top", top);
    slideContainer.css("transform", transform);
    slideContainer.css("transform-origin", "0 0");
}

function advanceSlides(n){
    // Advance the presentation by n slides.

    // Sanity check:
    if (slideIndex + n < 0 || slideIndex + n > maxIndex) { return }

    var prevSlideIndex = slideIndex;
    slideIndex += n

    // Display the new slide:
    showSlide(slideData[slideIndex], slideData[prevSlideIndex]);

    // Control visibility of slide controls.
    $("#prev-slide-ctrl").show();
    $("#next-slide-ctrl").show();

    if (slideIndex == maxIndex) {
        $("#next-slide-ctrl").hide();
    }
    if (slideIndex == 0) {
        $("#prev-slide-ctrl").hide();
    }
}

function jumpToSlide(slideID){
    // Map slideID to index in slideData:
    var idx = slideIDToIndex[slideID];

    // Use advanceSlides(n) to jump to slide we need.
    var delta = idx - slideIndex;
    if (delta == 0){
        return;
    }
    else {
        advanceSlides(delta);
    }
}

function showNavMenu() {
    // Get position of page number - left, right or centre.
    var slideNumPos = window.getComputedStyle(document.body).getPropertyValue("--slide-number-position");
    var navMenu = $("#nav-menu-content");

    if (slideNumPos.trim() == "right"){
        navMenu.attr("class", "right");
    }
    navMenu.css("display", "inline-block");
}

function toggleFullScreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
}

$(document).ready( function() {
    // Show the first slide!
    showSlide(slideData[0], null);

    // Hide previous-slide control as we're on the first page.
    $("#prev-slide-ctrl").hide();
    // Also hide next control if there's only one slide.
    if (maxIndex == 0){
        $("#next-slide-ctrl").hide();
    }

    // Add left/right arrow key navigation.
    $(document).keydown( function(e) {
        // left
        if (e.which == 37){
            advanceSlides(-1);
        }
        // right
        else if (e.which == 39){
            advanceSlides(1);
        }
    });
});



// Display the hidden navigation menu when the user hovers over the page number.
$("#slide-number").hover(
    showNavMenu, // on hover
    function(){ $("#nav-menu-content").css("display", "none"); }, // unhover
);
// Similarly, this will maintain hover until the user moves away from the menu.
$("#nav-menu-content").hover(
    showNavMenu, // on hover
    function(){ $("#nav-menu-content").css("display", "none"); }, // unhover
);