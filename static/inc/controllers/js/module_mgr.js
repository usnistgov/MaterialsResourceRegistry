/**
 * 
 * File Name: module_mgr.js
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
 * Show/hide
 * @param event
 */
showhide = function(event){
	console.log('BEGIN [showhide]');
	
	button = event.target
	parent = $(event.target).parent()
	$(parent.children('ul')).toggle("blind",500);
	if ($(button).attr("class") == "expand"){
		$(button).attr("class","collapse");
	}else{
		$(button).attr("class","expand");
	}
		
	console.log('END [showhide]');
}

var target;

var showModuleManager = function(event){
	target = event.target;
	hideAutoKeys();
	$( "#dialog-modules" ).dialog({
      modal: true,
      width: 600,
      height: 400,
      buttons: {
        Cancel: function() {
          $( this ).dialog( "close" );
        }
      }
    });
};		

/**
 * hideAutoKeys
 * Hide modules for generation of automatic keys
 */
hideAutoKeys = function(){
    $("#dialog-modules").find("table").find("tr:not(:first)").each(function(){
      $(this).show();
      if ($($(this).children("td")[1]).html().indexOf('auto-key') > 0){
        $(this).hide();
      }
    });
}

var showAutoKeyManager=function(event){
	target = event.target;
	showAutoKeys();
	$( "#dialog-modules" ).dialog({
      modal: true,
      width: 600,
      height: 400,
      buttons: {
        Cancel: function() {
          $( this ).dialog( "close" );
        }
      }
    });
};

/**
 * showAutoKeys
 * Show only modules for generation of automatic keys
 */
showAutoKeys = function(){
    $("#dialog-modules").find("table").find("tr:not(:first)").each(function(){
      $(this).show();
      if ($($(this).children("td")[1]).html().indexOf('auto-key') < 0){
        $(this).hide();
      }
    });
}


/**
 * Build xpath of selected element
 * @returns
 */
getXPath = function(){
	current = $(target).parent().siblings('.path');
	xpath = $(current).text();	
	current = $(current).parent().parent().parent().siblings('.path');
	while(current != null){
		current_path = $(current).text() ;
		if (current_path.indexOf("schema") != -1){
			current = null;
		}else{			
			xpath = current_path + "/" + xpath;	
			current = $(current).parent().parent().parent().siblings('.path');
		}		
	}
	
	return xpath;
}


manageXPath = function(){	
	namespace = $(target).text().split(":")[0];
	i = 1;
	$(target).closest("ul").children().each(function(){
	  if(!($(this).find(".path").html() == $(target).closest("li").find(".path").html() )){
		  $(this).find(".path").html(namespace + ":element["+i+"]");
		  i += 1;
	  }	  
	})
}



/**
 * Insert a module in the XML tree
 * @param event
 */
insertModule = function(event){	
	// change the sequence style
	parent = $(target).parent()
	
	insertButton = event.target;
	moduleURL = $(insertButton).parent().siblings(':nth-of-type(2)').text();
	moduleID = $(insertButton).parent().siblings(':first').attr('moduleID');
	
	xpath = getXPath();
	
	// add the module attribute
	if ($(parent).parent().find('.module').length == 1 ){
		$(parent).parent().find(".module").html(moduleURL);
	}else{
		$(parent).after("<span class='module'>"+
						moduleURL +
						"</span>");
	}
	
	
	$( "#dialog-modules" ).dialog("close");
	
	insert_module(moduleID, xpath);
}



/**
 * AJAX call, inserts a module
 */
insert_module = function(moduleID, xpath){
    $.ajax({
        url : "/admin/insert_module",
        type : "POST",
        dataType: "json",
        data:{
        	moduleID: moduleID,
        	xpath: xpath,
        },
        success: function(data){

        }
    });
}



/**
 * Remove a module
 * @param event
 */
noModule = function(event){	
	// change the sequence style
	parent = $(target).parent()
	
	insertButton = event.target;
	
	xpath = getXPath();
	
	// remove the module
	$(parent).parent().find('.module').remove()	
	
	$( "#dialog-modules" ).dialog("close");
	
	no_module(xpath);
}


/**
 * AJAX call, removes a module
 */
no_module = function(xpath){
    $.ajax({
        url : "/admin/remove_module",
        type : "POST",
        dataType: "json",
        data:{
        	xpath: xpath,
        },
        success: function(data){

        }
    });
}

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

saveTemplateUser = function(){
    var type = getUrlParameter('type');
    $.ajax({
        url : "/admin/save_modules",
        type : "POST",
        dataType: "json",
        data: {
            'type': type
        },
        success: function(data){
        	$(function() {
                $("#dialog-save").dialog({
                  modal: true,
                  buttons: {
                    OK: function() {
                        if(type == "template") {
                            window.location = '/dashboard/templates'
                        } else {
                            window.location = '/dashboard/types'
                        }
                    }
                  }
            });
        });
        }
    });
}

saveTemplate = function(){
    $.ajax({
        url : "/admin/save_modules",
        type : "POST",
        dataType: "json",
        data: {
            'type': getUrlParameter('type')
        },
        success: function(data){
        	saveTemplateCallback();
        }
    });
}

/**
 * Display success window
 */
saveTemplateCallback = function(){
	console.log('BEGIN [saveTemplate]');
	
	$(function() {
		$("#dialog-save").dialog({
		  modal: true,
		  buttons: {
			OK: function() {
					window.location = '/admin/xml-schemas/manage-schemas'
			   	}
		      }
		    });
	  });
	
	console.log('END [saveTemplate]');
}