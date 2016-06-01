/**
 * 
 * File Name: composer.js
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
 * AJAX call, checks that a template is selected
 * @param selectedLink redirection link
 */
verifyTemplateIsSelected = function(selectedLink)
{
    console.log('BEGIN [verifyTemplateIsSelected]');

    $.ajax({
        url : "/compose/verify_template_is_selected",
        type : "GET",
        dataType: "json",
        success: function(data){
            verifyTemplateIsSelectedCallback(data, selectedLink);
        }
    });

    console.log('END [verifyTemplateIsSelected]');
}


/**
 * AJAX callback, redirects to selected link if authorized
 * @param data data from server
 * @param selectedLink redirection link
 */
verifyTemplateIsSelectedCallback = function(data, selectedLink)
{
    console.log('BEGIN [verifyTemplateIsSelectedCallback]');

    if (data.templateSelected == 'no') {
        $(function() {
            $( "#dialog-error-message" ).dialog({
                modal: true,
                buttons: {
                    Ok: function() {
                    $( this ).dialog( "close" );
                    }
                }
            });
        });
    } else {
        location.href = selectedLink;
    }

    console.log('END [verifyTemplateIsSelectedCallback]');
}


/**
 * Load controllers of the template selection page.
 */
loadTemplateSelectionControllers = function()
{
    console.log('BEGIN [loadTemplateSelectionControllers]');    
    $('.btn.set-compose-template').on('click', setComposeCurrentTemplate);
    $('.btn.set-compose-user-template').on('click', setComposeCurrentUserTemplate);
    console.log('END [loadTemplateSelectionControllers]');
}

/**
 * Check that a template is selected.
 */
verifyTemplateIsSelectedBuild = function(){
    console.log('BEGIN [verifyTemplateIsSelected]');

    verify_template_is_selected_build(); 

    console.log('END [verifyTemplateIsSelected]');
}


/**
 * AJAX call, checks that a template has been selected
 * @param callback
 */
verify_template_is_selected_build = function(){
    $.ajax({
        url : "/compose/verify_template_is_selected",
        type : "GET",
        dataType: "json",
        success: function(data){
        	verifyTemplateIsSelectedBuildCallback(data);
        }
    });
}


/**
 * The template is not selected, redirect to main page.
 * @param data 'yes' or 'no'
 */
verifyTemplateIsSelectedBuildCallback = function(data)
{
    console.log('BEGIN [verifyTemplateIsSelectedCallback]');

    if (data.templateSelected == 'no') {
        location.href = "/compose";
    }else{
    	loadComposeBuildTemplate();
    	verifyNewTemplate();
    }

    console.log('END [verifyTemplateIsSelectedCallback]');
}


/**
 * Check if the selected template is a new template
 */
verifyNewTemplate = function(){
	is_new_template();
}


/**
 * AJAX call, checks if the template is a new template
 */
is_new_template = function(){
    $.ajax({
        url : "/compose/is_new_template",
        type : "GET",
        dataType: "json",
        success: function(data){
        	newTemplateCallback(data);
        }
    });
}


/**
 * If new template, need to give it a name
 * @param data 'yes' or 'no'
 */
newTemplateCallback = function(data){
	if (data.newTemplate == 'yes'){
		$("#newTemplateTypeNameError").html("");
		$(function() {
		    $( "#dialog-new-template" ).dialog({
		      modal: true,
		      width:400,
		      height:270,
		      buttons: {
		        Start: function() {
		          if ($("#newTemplateTypeName").val() == ""){
		        	  $("#newTemplateTypeNameError").html("The name can't be empty.");
		          }else if ( !$("#newTemplateTypeName").val().match(/^[a-zA-Z]*$/)){
		        	  $("#newTemplateTypeNameError").html("The name can only contains letters.");
		          }else{
		        	  $("#XMLHolder").find(".type").html($("#newTemplateTypeName").val());
		        	  typeName = $("#newTemplateTypeName").val();
		        	  change_root_type_name(typeName);
		        	  $( this ).dialog( "close" );
		          }
		        }
		      }
		    });
		  });
	} 
}


/**
 * AJAX call, change the name of the root type
 * @param typeName name of the root type
 */
change_root_type_name = function(typeName){
    $.ajax({
        url : "/compose/change_root_type_name",
        type : "POST",
        dataType: "json",
        data:{
        	typeName: typeName
        },
    });
}


/**
 * Set a template to be current
 */
setComposeCurrentTemplate = function()
{
    var tdElement = $(this).parent();
    var templateID = $(this).parent().parent().children(':first').attr('templateid');
		
    tdElement.html('<img src="/static/resources/img/ajax-loader.gif" alt="Loading..."/>');
    $('.btn.set-template').off('click');

    set_current_template(templateID);

    return false;
}


/**
 * AJAX call, sets the current template
 * @param templateID id of the template
 */
set_current_template = function (templateID){
    $.ajax({
        url : "/compose/set_current_template",
        type : "POST",
        dataType: "json",
        data:{
        	templateID: templateID
        },
        success: function(data){
        	setCurrentTemplateCallback();
        }
    });
}


/**
 * Set a user template to be current
 */
setComposeCurrentUserTemplate = function()
{
    var templateName = $(this).parent().parent().children(':first').text();
    var tdElement = $(this).parent();
    var templateID = $(this).parent().parent().children(':first').attr('templateid');
		
    tdElement.html('<img src="/static/resources/img/ajax-loader.gif" alt="Loading..."/>');
    $('.btn.set-template').off('click');

    set_current_user_template(templateID);

    return false;
}


/**
 * AJAX call, sets the current user template
 * @param templateID id of the template
 */
set_current_user_template = function (templateID){
    $.ajax({
        url : "/compose/set_current_user_template",
        type : "POST",
        dataType: "json",
        data:{
        	templateID: templateID
        },
        success: function(data){
        	setCurrentTemplateCallback();
        }
    });
}


/**
 * AJAX callback
 * @param data
 */
setCurrentTemplateCallback = function()
{
    console.log('BEGIN [setCurrentTemplateCallback]');

    $('#template_selection').load(document.URL +  ' #template_selection', function() {
		loadTemplateSelectionControllers();
		displayTemplateSelectedDialog();
    });
    console.log('END [setCurrentTemplateCallback]');
}

/**
 * show success dialog
 */
displayTemplateSelectedDialog = function()
{
 $(function() {
    $( "#dialog-message" ).dialog({
      modal: true,
      buttons: {
        Ok: function() {
          $( this ).dialog( "close" );
        }
      }
    });
  });
}


/**
 * Load controllers for build template page 
 */
loadComposeBuildTemplate = function(){
	console.log('BEGIN [loadComposeBuildTemplate]');
		
	$('.btn.download').on('click', downloadTemplate);
	$('.btn.save.template').on('click', saveTemplate);
	$('.btn.save.types').on('click', saveType);
	$(document).on('click', function(event) {
	  if (!$(event.target).closest('#XMLHolder').length) {
	    $("#menu").remove();
	  }
	});
	
	load_xml();
	console.log('END [loadComposeBuildTemplate]');
}


/**
 * AJAX call, load xml document
 */
load_xml = function(){
    $.ajax({
        url : "/compose/load_xml",
        type : "GET",
        dataType: "json",
        success: function(data){
        	$("#XMLHolder").html(data.XMLHolder);
        }
    });
}


/**
 * Download a composed template
 */
downloadTemplate = function(){
	console.log('BEGIN [downloadTemplate]');
	
	download_template();
	
	console.log('END [downloadTemplate]');
}



/**
 * AJAX call, download a composed template
 */
download_template = function(){
    $.ajax({
        url : "/compose/download_template",
        type : "GET",
        dataType: "json",
        success: function(data){
        	window.location = "/compose/download-XSD?id=" + data.xml2downloadID
        }
    });
}


/**
 * Save a composed template
 */
saveTemplate = function(){
	console.log('BEGIN [saveTemplate]');
	
	$("#new-template-error").html("");
	
	$(function() {
		$("#dialog-save-template").dialog({
		  modal: true,
		  width: 400,
		  height: 250,
		  buttons: {
			Save: function() {
					templateName = $("#newTemplateName").val();
					if (templateName.length > 0){						
						save_template(templateName);						
					}else{
						$( "#new-template-error" ).html("The name can't be empty.")
					}					 
			   	},		      
		    Cancel: function() {
		    		$( this ).dialog( "close" );
		        }
		      }
		    });
	  });
	
	console.log('END [saveTemplate]');
}



/**
 * AJAX call, saves a template
 * @param templateName
 */
save_template = function(templateName){
    $.ajax({
        url : "/compose/save_template",
        type : "POST",
        dataType: "json",
        data:{
        	templateName: templateName
        },
        success: function(data){
        	if('errors' in data){
        		$("#new-template-error").html("<font color='red'>Not a valid XML schema.</font><br/>" + data.errors);
        	}else{
        		saveTemplateCallback();
                $("#dialog-save-template").dialog("close");
        	}
        }
    });
}



/**
 * Save a composed type
 */
saveType = function(){
	console.log('BEGIN [saveType]');
	
	$("#new-type-error").html("");
	
	$(function() {
		$("#dialog-save-type").dialog({
		  modal: true,
		  width: 400,
		  height: 250,
		  buttons: {
			Save: function() {
					typeName = $("#newTypeName").val();
					if (typeName.length > 0){	
						save_type(typeName);						
					}else{
						$( "#new-type-error" ).html("The name can't be empty.")
					}
			   	},			      
		    Cancel: function() {
		    		$( this ).dialog( "close" );
		        }
		      }
		    });
	  });
	
	console.log('END [saveType]');
}


/**
 * AJAX call, saves a type
 * @param templateName
 */
save_type = function(typeName){
    $.ajax({
        url : "/compose/save_type",
        type : "POST",
        dataType: "json",
        data:{
        	typeName: typeName
        },
        success: function(data){
        	if('errors' in data){
        		if ("message" in data){
        			$("#new-type-error").html("<font color='red'>" + data.errors + "</font><br/>" + data.message);
        		}else{
        			$("#new-type-error").html("<font color='red'>" + data.errors + "</font><br/>");
        		}     
        	}else{
        		saveTemplateCallback();
                $("#dialog-save-type").dialog("close");
        	}
        }
    });
}


/**
 * Show success message
 */
saveTemplateCallback = function(){
	console.log('BEGIN [saveTemplateCallback]');	
	
	$(function() {
        $( "#dialog-saved-message" ).dialog({
            modal: true,
            buttons: {
		Ok: function() {
                    $( this ).dialog( "close" );
                }
            }
        });
    });
	
	console.log('END [saveTemplateCallback]');
}

/**
 * Show/hide
 * @param event
 */
showhide = function(event){
	console.log('BEGIN [showhide]');
	button = event.target
	parent = $(event.target).parent()
	$(parent.children()[3]).toggle("blind",500);
	if ($(button).attr("class") == "expand"){
		$(button).attr("class","collapse");
	}else{
		$(button).attr("class","expand");
	}
		
	console.log('END [showhide]');
}

var target;

var showMenuSequence=function(event){
	$("#menu").remove();
	
	target = event.target;
	$("<ul id='menu' style='position:absolute;z-index:9999;'>" + 
      "<li><span onclick='displayInsertElementSequenceDialog()'>Add Element</span></li>" +
      "<li><span onclick='displayChangeTypeDialog()'>Change Type</span></li>" +
      "</ul>")
		.menu()
		.appendTo("body")
		.position({
	        my: "left top",
	        at: "left bottom",
	        of: event.target
	      }).show();
};		

var showMenuElement=function(event){
	$("#menu").remove();
	
	
	target = event.target;
	parentPath = $(target).parent().parent().parent().parent().siblings('.path').text();
	
	// if root element
	if(parentPath.indexOf('schema') > -1){
		$("<ul id='menu' style='position:absolute;z-index:9999;'>" + 
	      "<li><span onclick='displayRenameElementDialog()'>Rename</span></li>" +
	      "</ul>")
			.menu()
			.appendTo("body")
			.position({
		        my: "left top",
		        at: "left bottom",
		        of: event.target
		      }).show();
	}else{ // not root element
		$("<ul id='menu' style='position:absolute;z-index:9999;'>" + 
	      "<li><span onclick='displayRenameElementDialog()'>Rename</span></li>" +
	      "<li><span onclick='displayOccurrencesElementDialog()'>Manage Occurrences</span></li>" +
	      "<li><span onclick='displayDeleteElementDialog()'>Delete</span></li>" +
	      "</ul>")
			.menu()
			.appendTo("body")
			.position({
		        my: "left top",
		        at: "left bottom",
		        of: event.target
		      }).show();
	}	
};	

displayInsertElementSequenceDialog = function()
{
 $(function() {
	$("#table_types").find(".btn.insert").each(function(){
		$(this).attr('onclick','insertElementSequence(event)');
	});	
    $( "#dialog-insert-element-sequence" ).dialog({
      modal: true,
      width: 600,
      height: 400,
      open: function(){
    	  $('#table_types').accordion({
    		  	header: "h3",
    			collapsible: true,
    			active: false,
    			heightStyle: "content",
		  });
      },
      buttons: {
        Cancel: function() {
          $( this ).dialog( "close" );
        }
      }
    });
  });
}

displayChangeTypeDialog = function()
{
	 $(function() {
	    $( "#dialog-change-xsd-type" ).dialog({
	      modal: true,
	      width: 275,
	      height: 185,
	      buttons: {
	    	Change: function() {
	    		  newType = $("#newXSDtype").val();
	    		  xpath = getXPath();
	    		  oldType = $(target).text().split(":")[1];
	    		  $(target).html($(target).html().replace(oldType,newType));
	    		  $(target).parent().siblings(".path").html($(target).parent().siblings(".path").html().replace(oldType,newType));
	    		  change_xsd_type(xpath, newType);
		          $( this ).dialog( "close" );
		    },
	        Cancel: function() {
	          $( this ).dialog( "close" );
	        }
	      }
	    });
	  });
	}

function isInt(value) {
  return !isNaN(value) && parseInt(Number(value)) == value && !isNaN(parseInt(value, 10));
}


/**
 * AJAX call, cahnges the type of a element
 * @param xpath Xpath to the element
 * @param newType new type of the element
 */
change_xsd_type = function(xpath, newType){
    $.ajax({
        url : "/compose/change_xsd_type",
        type : "POST",
        dataType: "json",
        data:{
        	xpath: xpath,
        	newType: newType
        },
        success: function(data){

        }
    });
}


/**
* Management of the unbounded checkbox
*/

OnClickUnbounded = function()
{
    unbounded = document.getElementById('unbounded').checked

    if(unbounded)
    {
        $("#maxOccurrences").prop('disabled', true);
        $("#maxOccurrences").val("unbounded");
    }
    else
    {
        $("#maxOccurrences").prop('disabled', false);
        $("#maxOccurrences").val("");
    }
}

/**
 * Show dialog to set occurrences
 */
displayOccurrencesElementDialog = function()
{
	 $( "#manage-occurrences-error" ).html("");
	 $(function() {
		xpath = getXPath();
		get_occurrences(xpath);
	    $( "#dialog-occurrences-element" ).dialog({
	      modal: true,
	      width: 600,
	      height: 350,
	      buttons: {
			Save: function() {
				minOccurs = $("#minOccurrences").val();
				maxOccurs = $("#maxOccurrences").val();

				errors = ""

				if (! isInt(minOccurs)){
					errors += "minOccurs should be an integer.<br/>";
				}else {
					if (minOccurs < 0){
						errors += "minOccurs should be superior or equal to 0.<br/>";
					}
					if (! isInt(maxOccurs)){
						if (maxOccurs != "unbounded"){
							errors += "maxOccurs should be an integer or 'unbounded'.<br/>";
						}
					}else {
						if (maxOccurs < 1){
							errors += "maxOccurs should be superior or equal to 1.<br/>";
						}else if (maxOccurs < minOccurs){
							errors += "maxOccurs should be superior or equal to minOccurs.<br/>";
						}
					}
				}
				
				if (errors == ""){
					set_occurrences(xpath, minOccurs, maxOccurs);
					occursStr = "( " + minOccurs + " , ";
					if (maxOccurs == "unbounded"){
						occursStr += "*";
					}else{
						occursStr += maxOccurs;
					}
					occursStr += " )";
					$(target).parent().siblings(".occurs").html(occursStr)
					$( this ).dialog( "close" );
				}else{
					$( "#manage-occurrences-error" ).html(errors);
				}
			},
			Cancel: function() {
			  $( this ).dialog( "close" );
			}
	      }
	    });
	  });
}



/**
 * AJAX call, gets element occurrences from the server
 * @param xpath
 */
get_occurrences = function(xpath){
    $.ajax({
        url : "/compose/get_occurrences",
        type : "POST",
        dataType: "json",
        data:{
        	xpath: xpath,
        },
        success: function(data){
        	$("#minOccurrences").val(data.minOccurs);
        	$("#maxOccurrences").val(data.maxOccurs);

        	if(data.maxOccurs == 'unbounded')
        	{
        	    $("#maxOccurrences").prop('disabled', true);
        	    $('#unbounded').prop('checked', true);
        	}
        	else
        	{
        	    $("#maxOccurrences").prop('disabled', false);
        	    $('#unbounded').prop('checked', false);
        	}
        }
    });
}


/**
 * AJAX call, sets the occurrences of an element
 * @param xpath xpath of the element
 * @param minOccurs minimun occurrences
 * @param maxOccurs maximum occurrences
 */
set_occurrences = function(xpath, minOccurs, maxOccurs){
    $.ajax({
        url : "/compose/set_occurrences",
        type : "POST",
        dataType: "json",
        data:{
        	xpath: xpath,
        	minOccurs: minOccurs,
        	maxOccurs: maxOccurs,
        },
        success: function(data){

        }
    });
}

displayDeleteElementDialog = function()
{
	 $(function() {
		xpath = getXPath();
	    $( "#dialog-delete-element" ).dialog({
	      modal: true,
	      width: 400,
	      height: 170,
	      buttons: {
			Delete: function() {
				manageXPath();
				$(target).parent().parent().parent().remove();				
				delete_element(xpath);
				$( this ).dialog( "close" );
			},
			Cancel: function() {
				$( this ).dialog( "close" );
			}
	      }
	    });
	  });
}


/**
 * AJAX call, deletes an element
 * @param xpath
 */
delete_element = function(xpath){
    $.ajax({
        url : "/compose/delete_element",
        type : "POST",
        dataType: "json",
        data:{
        	xpath: xpath,
        },
        success: function(data){

        }
    });
}


/**
 * Show dialog to rename an element
 */
displayRenameElementDialog = function()
{
	$( "#rename-element-error" ).html("");
	$("#newElementName").val($(target).parent().siblings('.name').html());
	$(function() {
		$( "#dialog-rename-element" ).dialog({
		  modal: true,
		  width: 400,
		  height: 250,
		  buttons: {
			Rename: function() {
					newName = $("#newElementName").val();
					if (newName.length > 0){
						xpath = getXPath();
						rename_element(xpath, newName);
						$(target).parent().siblings('.name').html(newName);
						$( this ).dialog( "close" );
					}else{
						$( "#rename-element-error" ).html("The name can't be empty.")
					}					 
			   	},			      
		    Cancel: function() {
		    		$( this ).dialog( "close" );
		        }
		      }
		    });
	  });
}


/**
 * AJAX call, renames an element
 * @param xpath xpath of the element
 * @param newName new name of the element
 */
rename_element = function(xpath, newName){
    $.ajax({
        url : "/compose/rename_element",
        type : "POST",
        dataType: "json",
        data:{
        	xpath: xpath,
        	newName: newName
        },
        success: function(data){

        }
    });
}


/**
 * Insert an element in the XML tree
 * @param event
 */
insertElementSequence = function(event){
	// change the sequence style
	parent = $(target).parent()
	if ($(parent).attr('class') == "element"){
		$(parent).before("<span class='collapse' style='cursor:pointer;' onclick='showhide(event);'></span>");
		$(parent).after("<ul></ul>");
		$(parent).attr('class','category');
	}
	
	insertButton = event.target;
	typeName = $(insertButton).parent().siblings(':first').text();
	typeID = $(insertButton).parent().siblings(':first').attr('templateid');
	namespace = $(target).text().split(":")[0];
	
	nbElement = $(parent).parent().children("ul").children().length;
	console.log(nbElement)
	if (nbElement == 0){
		path = namespace + ":element";
//	}else if (nbElement == 1){
//		path = namespace + ":element[2]";
//		$($(parent).parent().find("ul").children()[0]).find(".element-wrapper").find(".path").text(namespace + ":element[0]");
	}else{
		path = namespace + ":element[" + String(nbElement + 1) + "]";
	}	
	
	xpath = getXPath();

	//console.log($(parent).parent().find("ul"));
	// add the new element
	$(parent).parent().children("ul").append("<li>" +
											"<div class='element-wrapper'>" +
												"<span class='path'>"+
												 path +
												"</span>" +
												"<span class='newElement'>" +
													"<span onclick='showMenuElement(event)' style='cursor:pointer;'>" +
													namespace + ":element : "+ 
													"</span>" +													
												"</span>" +
												"<span class='name'>"+ typeName +"</span>" +
												"<span class='type'>"+ typeName +"</span>" +
												"<span class='occurs'>( 1 , 1)</span>" +
											"</div>"+
										"</li>")
	
	$( "#dialog-insert-element-sequence" ).dialog("close");
	
	insert_element_sequence(typeID, xpath, typeName);
}



/**
 * AJAX call, inserts an element in an XML sequence
 */
insert_element_sequence = function(typeID, xpath, typeName){
    $.ajax({
        url : "/compose/insert_element_sequence",
        type : "POST",
        dataType: "json",
        data:{
        	typeID: typeID,
        	xpath: xpath,
        	typeName: typeName
        },
        success: function(data){

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