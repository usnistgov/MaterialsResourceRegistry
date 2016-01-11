/**
 * 
 * File Name: XMLTree.js
 * Author: Sharief Youssef
 * 		   sharief.youssef@nist.gov
 *
 *        Guillaume SOUSA AMARAL
 *        guillaume.sousa@nist.gov
 * 
 * Sponsor: National Institute of Standards and Technology (NIST)
 * 
 */


/**
 * Expand/Collapse elements from the XML tree on Curate page
 */
showhideCurate = function(event){
	console.log('BEGIN [showhideCurate]');
	button = event.target
	parent = $(event.target).parent();
	$(parent.children("ul")).toggle("blind",500);
	if ($(button).attr("class") == "expand"){
		$(button).attr("class","collapse");
	}else{
		$(button).attr("class","expand");
	}
	console.log('END [showhideCurate]');
}