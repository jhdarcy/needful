{# This is the JavaScript portion of needful. This has been placed in a separate file
to make the JS development easier. This file is processed and inserted into the final
HTML output file, and should not be edited lest needful be broken forever. #}

var {{config_var}} = {
    "pageNumbers" : {{ page_numbers | lower() }},
    "width" : {{size[0]}},
    "height" : {{size[1]}},
    "autoScale" : {{ autoscale | lower() }},
    "navMenu" : {{ nav_menu | lower() }},
    "overflow" : {{ overflow | lower() }}
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
            {{slide.plotly_plot_func}}
        },
        "purge" : function purge() {
            {{slide.plotly_purge_func}}
        },
        "pageNumber" : {{ config_var + ".pageNumbers" if slide._page_number == None else slide._page_number | lower() }},
        "navMenu" : {{ config_var + ".navMenu" if slide._nav_menu == None else slide._nav_menu | lower() }},
        "autoScale" : {{ config_var + ".autoScale" if slide._autoscale == None else slide._autoscale | lower() }},
        "overflow" : {{ config_var + ".overflow" if slide._overflow == None else slide._overflow | lower() }},
        "disable_mathjax" : {{ slide._disable_mathjax | lower() }}
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

function showSlide(slide) {
    // As implied, display the given slide.

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
    var slideNumber = $("#slide-number-span");
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
}

function scaleContent(){
    // Update content scaling if we need to fit everything to screen.

    // First, fix size of the slide container.
    var slideContainer = $("#slide-container");
    if (slideData[slideIndex].overflow) {
        slideContainer.css("overflow", "");
    }
    else {
        slideContainer.css("overflow", "hidden");
    }

    // If we don't need to further autoscale, stop here.
    if (!slideData[slideIndex].autoScale){
        slideContainer.css({"width": "", "height": ""});
        slideContainer.css({"left": "", "top": ""});
        slideContainer.css({"transform": "", "transform-origin": ""});
        return;
    };

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

    slideData[slideIndex].purge();

    // Display the new slide:
    showSlide(slideData[slideIndex += n]);

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
    if (!slideData[slideIndex].navMenu){
        $("#slide-number-span").css("cursor", "auto");
        return;
    }

    $("#slide-number-span").css("cursor", "pointer");

    // Get position of page number - left, right or centre.
    var navMenu = $("#nav-menu-content");
    var slideNumPos = $("#slide-number").css("text-align");

    if (slideNumPos.trim() == "right"){
        // If page number is on right, nav menu will appear off page.
        var right = window.innerWidth - $("#slide-number-span").position().left;
        navMenu.css("right", right);
    }
    else
    {
        navMenu.css("right", "auto");
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
    showSlide(slideData[0]);

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
$("#slide-number-span").hover(
    showNavMenu, // on hover
    function(){ $("#nav-menu-content").css("display", "none"); }, // unhover
);
// Similarly, this will maintain hover until the user moves away from the menu.
$("#nav-menu-content").hover(
    showNavMenu, // on hover
    function(){ $("#nav-menu-content").css("display", "none"); }, // unhover
);