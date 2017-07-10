/* Copyright (c) 2008 Kean Loong Tan http://www.gimiti.com/kltan
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
 * jFlow
 * Version: 1.2 (July 7, 2008)
 * Requires: jQuery 1.2+
 * 
 * This is a modified version of the original jFlow with automatic scroll:
 * you can choose the scroll direction, modifing the 'direction' parameter 
 * ('left' or 'right') when calling the function on your document.
 * Edited by Mauro Belgiovine (geek89@gmail.com) on October 20, 2010.
 *
 * Modified again by Josh Darvill for spyka Webmaster templates, removing
 * the annoying Javascript Messages in IE6-8
 */
 
(function($) {

	$.fn.jFlow = function(options) {
		var opts = $.extend({}, $.fn.jFlow.defaults, options);
		var randNum = Math.floor(Math.random()*11);
		var jFC = opts.controller;
		var jFS =  opts.slideWrapper;
		var jSel = opts.selectedWrapper;

		var cur = 0;
		var timer;
		var maxi = $(jFC).length - 1;
		var autoMove = opts.next;
		var displayDuration = 7500;
		
		// sliding function
		var slide = function (dur, i) {
			$(opts.slides).children().css({
				overflow:"hidden"
			});
			$(opts.slides + " iframe").hide().addClass("temp_hide");
			$(opts.slides).animate({
				marginLeft: "-" + (i * $(opts.slides).find(":first-child").width() + "px")
				},
				opts.duration*(dur),
				opts.easing,
				function(){
					$(opts.slides).fadeIn('200');
					$(opts.slides).children().css({
						overflow:"hidden"
					});
					$(".temp_hide").show();
				}
			);
			
		}
		$(this).find(jFC).each(function(i){
			$(this).click(function(){
				dotimer();
				if ($(opts.slides).is(":not(:animated)")) {
					$(jFC).removeClass(jSel);
					$(this).addClass(jSel);
					if(opts.direction == 'right'){ //direction edit for controller
						that = maxi - i;
					} else {
						that = i;
					}
					var dur = Math.abs(cur-that);
					slide(dur,that);
					cur = that;
				}
			});
		});	
		
		$(opts.slides).before('<div id="'+jFS.substring(1, jFS.length)+'"></div>').appendTo(jFS);
		
		$(opts.slides).find("div").each(function(){
			$(this).before('<div class="jFlowSlideContainer"></div>').appendTo($(this).prev());
		});
		
		//direction settings
		if(opts.direction == 'right'){
			cur = maxi; //starting from last slide
			autoMove = opts.prev; //changing the auto-scroll direction
			$(opts.slides).children().each(function(e){ //inverting the slide order
				if(e > 0){
					var child = $(this).detach();
					$(opts.slides).prepend(child);
				}
			});
		}
		
		
		//initialize the controller
		$(jFC).eq(cur).addClass(jSel);
		
		var resize = function (x){
			$(jFS).css({
				position:"relative",
				width: opts.width,
				height: opts.height,
				overflow: "hidden"
			});
			//opts.slides or #mySlides container
			$(opts.slides).css({
				position:"relative",
				width: $(jFS).width()*$(jFC).length+"px",
				height: $(jFS).height()+"px",
				overflow: "hidden"
			});
			// jFlowSlideContainer
			$(opts.slides).children().css({
				position:"relative",
				width: $(jFS).width()+"px",
				height: $(jFS).height()+"px",
				"float":"left",
				overflow:"hidden"
			});
			
			$(opts.slides).css({
				marginLeft: "-" + (cur * $(opts.slides).find(":eq(0)").width() + "px")
			});
		}
		
		// sets initial size
		resize();

		// resets size
		$(window).resize(function(){
			resize();						  
		});
		
		$(opts.prev).click(function(){
			dotimer();
			doprev();
			
		});
		
		$(opts.next).click(function(){
			dotimer();
			donext();
			
		});
		
		var doprev = function (x){
			if ($(opts.slides).is(":not(:animated)")) {
				var dur = 1;
				if (cur > 0)
					cur--;
				else {
					cur = maxi;
					dur = cur;
				}
				$(jFC).removeClass(jSel);
				slide(dur,cur);
				$(jFC).eq(cur).addClass(jSel);
			}
		}
		
		var donext = function (x){
			if ($(opts.slides).is(":not(:animated)")) {
				var dur = 1;
				if (cur < maxi)
					cur++;
				else {
					cur = 0;
					dur = maxi;
				}
				$(jFC).removeClass(jSel);
				//$(jFS).fadeOut("fast");
				slide(dur, cur);
				//$(jFS).fadeIn("fast");
				$(jFC).eq(cur).addClass(jSel);
			}
		}
		
		var dotimer = function (x){
			if((opts.auto) == true) {
				if(timer != null) 
					clearInterval(timer);
			    
        		timer = setInterval(function() {
	                	$(autoMove).click();
						}, displayDuration);
			}
		}

		dotimer();
	};
	
	$.fn.jFlow.defaults = {
		controller: ".jFlowControl", // must be class, use . sign
		slideWrapper : "#jFlowSlide", // must be id, use # sign
		selectedWrapper: "jFlowSelected",  // just pure text, no sign
		auto: false,
		direction: 'left', //'left' (default) or 'right'
		easing: "swing",
		duration: 400,
		width: "100%",
		prev: ".jFlowPrev", // must be class, use . sign
		next: ".jFlowNext" // must be class, use . sign
	};
	
})(jQuery);


