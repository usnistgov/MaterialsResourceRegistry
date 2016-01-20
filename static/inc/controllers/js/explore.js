/**
 * 
 * File Name: explore.js
 * Author: Sharief Youssef
 * 		   sharief.youssef@nist.gov
 *
 *         Guillaume SOUSA AMARAL
 *         guillaume.sousa@nist.gov
 * 
 * Sponsor: National Institute of Standards and Technology (NIST)
 * 
 */

var timeout;

/**
 * AJAX call, checks that a template is selected
 * @param selectedLink redirection link
 */
verifyTemplateIsSelected = function(selectedLink)
{
    console.log('BEGIN [verifyTemplateIsSelected]');

    $.ajax({
        url : "/explore/verify_template_is_selected",
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
 * Load controllers for the template selection
 */
loadTemplateSelectionControllers = function()
{
    console.log('BEGIN [loadTemplateSelectionControllers]');
    $('.btn.set-explore-template').on('click', setExploreCurrentTemplate);
    $('.btn.set-explore-user-template').on('click', setExploreCurrentUserTemplate);
    console.log('END [loadTemplateSelectionControllers]');
}


/**
 * set the current template
 * @returns {Boolean}
 */
setExploreCurrentTemplate = function()
{
    var templateID = $(this).parent().parent().children(':first').attr('templateID');
    var tdElement = $(this).parent();
		
    tdElement.html('<img src="/static/resources/img/ajax-loader.gif" alt="Loading..."/>');
    $('.btn.set-template').off('click');
    
    set_current_template(templateID);

    return false;
}


/**
 * AJAX call, sets the current template
 * @param templateFilename name of the selected template
 * @param templateID id of the selected template
 */
set_current_template = function(templateID){
    $.ajax({
        url : "/explore/set_current_template",
        type : "POST",
        dataType: "json",
        data : {
            templateID: templateID
        },
        success: function(){
        	setCurrentTemplateCallback();
        }
    });
}



/**
 * AJAX call, get custom form from server
 */
get_custom_form = function(){
    $.ajax({
        url : "/explore/get_custom_form",
        type : "GET",
        dataType: "json",
        success: function(data){
        	if ('queryForm' in data){
        		$('#queryForm').html(data.queryForm);
        	}  
        	$("#customForm").html(data.customForm);

        }
    });
}


/**
 * set the current user template
 * @returns {Boolean}
 */
setExploreCurrentUserTemplate = function()
{
    var templateName = $(this).parent().parent().children(':first').text();
    var templateID = $(this).parent().parent().children(':first').attr('templateID');
    var tdElement = $(this).parent();
		
    tdElement.html('<img src="/static/resources/img/ajax-loader.gif" alt="Loading..."/>');
    $('.btn.set-template').off('click');

    set_current_user_template(templateID);

    return false;
}


/**
 * AJAX call, sets the current user defined template
 * @param templateID
 */
set_current_user_template = function(templateID){
    $.ajax({
        url : "/explore/set_current_user_template",
        type : "POST",
        dataType: "json",
        data : {
            templateID: templateID
        },
        success: function(){
        	setCurrentTemplateCallback();
        }
    });
}


/**
 * Set template Callback. Updates the template display.
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
 * Shows a dialog when the template is selected
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
 * When an element is selected in the query builder, input fields are added to the form regarding the type of the element.
 * @param fromElementID
 * @param criteriaID
 */
function updateUserInputs(fromElementID, criteriaID){
	$("input").each(function(){
	    $(this).attr("value", $(this).val());
	});
	$('select option').each(function(){ this.defaultSelected = this.selected; });
	var html = $("#queryForm").html();
	update_user_inputs(html, fromElementID, criteriaID);
}


/**
 * AJAX call, update user inputs for the selected element type 
 */
update_user_inputs = function(html, fromElementID, criteriaID){
    $.ajax({
        url : "/explore/update_user_inputs",
        type : "POST",
        dataType: "json",
        data : {
        	html: html,
        	fromElementID: fromElementID,
        	criteriaID: criteriaID
        },
        success: function(data){
            $("#queryForm").html(data.queryForm);
        }
    });
}


/**
 * Submit a query
 */
function query(){
	$("input").each(function(){
	    $(this).attr("value", $(this).val());
	});
	$('select option').each(function(){ this.defaultSelected = this.selected; });
	var queryForm = $("#queryForm").html()
	
	var elems = $("#fed_of_queries_instances")[0].getElementsByTagName("input");
    for(var i = 0; i < elems.length; i++) {
    	if(elems[i].checked == true)
    	{
    		elems[i].setAttribute("checked","checked");
    	}else
    	{
    		elems[i].removeAttribute('checked');
    	}
    }
	var fedOfQueries = $("#fed_of_queries_instances").html()
	
	execute_query(queryForm, fedOfQueries);
}


/**
 * AJAX call, execute query and redirects to result page
 * @param queryForm for that hosts the query builder
 * @param fedOfQueries list of selected repositories
 */
execute_query = function(queryForm, fedOfQueries){
    $.ajax({
        url : "/explore/execute_query",
        type : "POST",
        dataType: "json",
        data : {
        	queryForm: queryForm,
        	fedOfQueries: fedOfQueries
        },
        success: function(data){
            if ('errors' in data){
            	if (data.errors == 'zero'){
            		showErrorInstancesDialog();
            	}
            }else if ('listErrors' in data){
                $('#listErrors').html(data.listErrors);
                displayErrors();
            }else{
            	window.location = "/explore/results"
            }
        }
    });
}


/**
 * Get results asynchronously (disabled)
 * @param numInstance
 */
getAsyncResults = function(numInstance)
{
	/*for (i=0; i < Number(nbInstances); ++i){
		Dajaxice.explore.getResultsByInstance(Dajax.process,{"numInstance": i});		
	}*/
	get_results_by_instance(numInstance);
}

/**
 * AJAX call, gets query results
 * @param numInstance
 */
get_results_by_instance = function(numInstance){
    $("#banner_results_wait").show(200);
    $.ajax({
        url : "/explore/get_results_by_instance",
        type : "GET",
        dataType: "json",
        data : {
        	numInstance: numInstance,
        },
        success: function(data){
            $("#banner_results_wait").hide(200);
        	$("#results").html(data.results);
        }
    });
}

/**
 * AJAX call, gets the results
 */
get_results = function(){
    $.ajax({
        url : "/explore/get_results",
        type : "GET",
        dataType: "json",
        success: function(data){
        	getAsyncResults(data.numInstance);
        }
    });	
}


/**
 * Add an empty field to the query builder
 */
function addField(){
	$("input").each(function(){
	    $(this).attr("value", $(this).val());
	});
	$('select option').each(function(){ this.defaultSelected = this.selected; });
	var htmlForm = $("#queryForm").html()
	add_field(htmlForm);
}


/**
 * AJAX call, add field to the form
 * @param htmlForm
 */
add_field = function(htmlForm){
    $.ajax({
        url : "/explore/add_field",
        type : "POST",
        dataType: "json",
        data : {
        	htmlForm: htmlForm,
        },
        success: function(data){
            $("#queryForm").html(data.queryForm);
        }
    });
}


/**
 * Remove a field from the query builder
 * @param tagID
 */
function removeField(criteriaID){
	$("input").each(function(){
	    $(this).attr("value", $(this).val());
	});
	$('select option').each(function(){ this.defaultSelected = this.selected; });
	var queryForm = $("#queryForm").html()
	remove_field(queryForm, criteriaID);
}


/**
 * AJAX call, remove field from the form
 * @param htmlForm
 */
remove_field = function(queryForm, criteriaID){
    $.ajax({
        url : "/explore/remove_field",
        type : "POST",
        dataType: "json",
        data : {
        	queryForm: queryForm,
        	criteriaID: criteriaID
        },
        success: function(data){
        	$("#queryForm").html(data.queryForm);
        }
    });
}


/**
 * Save the current query
 */
function saveQuery(){
	$("input").each(function(){
	    $(this).attr("value", $(this).val());
	});
	$('select option').each(function(){ this.defaultSelected = this.selected; });
	var queryForm = $("#queryForm").html()
	
	save_query(queryForm);
}


/**
 * AJAX call, save the query
 * @param htmlForm
 */
save_query = function(queryForm){
    $.ajax({
        url : "/explore/save_query",
        type : "POST",
        dataType: "json",
        data : {
        	queryForm: queryForm,
        },
        success: function(data){
        	if ('listErrors' in data){
        		$('#listErrors').html(data.listErrors);
            	displayErrors();
        	}else{
        		$('#queriesTable').load(document.URL +  ' #queriesTable', function() {});
        	}
        }
    });
}


/**
 * Insert a saved query in the query builder
 * @param savedQueryID
 */
function addSavedQueryToForm(savedQueryID){
	$("input").each(function(){
	    $(this).attr("value", $(this).val());
	});
	$('select option').each(function(){ this.defaultSelected = this.selected; });
	var queryForm = $("#queryForm").html()
	
	add_saved_query_to_form(queryForm, savedQueryID);
} 


/**
 * AJAX call, insert a saved query in the query builder
 * @param queryForm form
 * @param savedQueryID id of the query to insert
 */
add_saved_query_to_form = function(queryForm, savedQueryID){
    $.ajax({
        url : "/explore/add_saved_query_to_form",
        type : "POST",
        dataType: "json",
        data : {
        	queryForm: queryForm,
        	savedQueryID: savedQueryID
        },
        success: function(data){
        	$("#queryForm").html(data.queryForm);
        }
    });
}


/**
 * Delete a saved query
 * @param savedQueryID
 */
function deleteQuery(savedQueryID){
	$(function() {
        $( "#dialog-DeleteQuery" ).dialog({
            modal: true,
            buttons: {		
            	Delete: function(){
		        	delete_query(savedQueryID);
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
 * AJAX call, delete a saved query
 * @param savedQueryID
 */
delete_query = function(savedQueryID){
    $.ajax({
        url : "/explore/delete_query",
        type : "POST",
        dataType: "json",
        data : {
        	savedQueryID: savedQueryID
        },
        success: function(data){
        	$('#queriesTable').load(document.URL +  ' #queriesTable', function() {});
        }
    });
}


/**
 * Clear the current criterias
 */
function clearCriterias(){
	$("input").each(function(){
	    $(this).attr("value", $(this).val());
	});
	$('select option').each(function(){ this.defaultSelected = this.selected; });
	var queryForm = $("#queryForm").html()
	
	clear_criterias(queryForm);
}


/**
 * AJAX call, clear current criterias
 * @param queryForm
 */
clear_criterias = function(queryForm){
    $.ajax({
        url : "/explore/clear_criterias",
        type : "POST",
        dataType: "json",
        data : {
        	queryForm: queryForm
        },
        success: function(data){
        	$("#queryForm").html(data.queryForm);
        }
    });	
}


/**
 * Delete all saved queries 
 */
clearQueries = function()
{
	$(function() {
        $( "#dialog-DeleteAllQueries" ).dialog({
            modal: true,
            buttons: {		
        		Delete: function(){
		        	$("input").each(function(){
		        	    $(this).attr("value", $(this).val());
		        	});
		        	$('select option').each(function(){ this.defaultSelected = this.selected; });
		        	clear_queries();
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
 * AJAX call, delete all saved queries
 */
clear_queries = function(){
    $.ajax({
        url : "/explore/clear_queries",
        type : "GET",
        dataType: "json",
        success: function(data){
        	$('#queriesTable').load(document.URL +  ' #queriesTable', function() {}); 
        }
    });	
}


/**
 * Save the custom form
 */
exploreData = function()
{
    console.log('BEGIN [exploreData]');

    // Need to Set input values explicitiy before sending innerHTML for save
    var elems = document.getElementsByName("xsdForm")[0].getElementsByTagName("input");
    for(var i = 0; i < elems.length; i++) {
    	// sent attribute to property value
    	elems[i].setAttribute("value", elems[i].checked);
    	if(elems[i].checked == true)
    	{
    		elems[i].setAttribute("checked","checked");
    	}
    }
    $('select option').each(function(){ this.defaultSelected = this.selected; }); 
    formContent = document.getElementById('xsdForm').innerHTML;
    save_custom_data(formContent);

    console.log('END [exploreData]');
}


/**
 * AJAX call, save the custom form and redirects to perform search
 * @param formContent
 */
save_custom_data = function(formContent){
	$.ajax({
        url : "/explore/save_custom_data",
        type : "POST",
        dataType: "json",
        data : {
        	formContent : formContent,
        },
        success: function(data){
        	window.location = "/explore/perform-search"
        }
    });
}


/**
 * Change a choice in the XSD form
 * @param selectObj
 */
changeChoice = function(selectObj)
{
    console.log('BEGIN [changeChoice(' + selectObj.id + ' : ' + selectObj.selectedIndex + ')]');

    // get the index of the selected option 
    var idx = selectObj.selectedIndex;  

    for (i=0; i < selectObj.options.length;i++) {
    	if (i == idx){
    		$("#" + selectObj.id + "-" + i).removeAttr("class");
		} else {
			$("#" + selectObj.id + "-" + i).attr("class","notchosen");
		}
    	
    }

    console.log('END [changeChoice(' + selectObj.id + ' : ' + selectObj.selectedIndex + ')]');
}

/**
 * Check that a template is selected
 */
verifyTemplateIsSelectedCustomize = function(){
    console.log('BEGIN [verifyTemplateIsSelected]');

    verify_template_is_selected_customize(); 

    console.log('END [verifyTemplateIsSelected]');
}


/**
 * AJAX call, checks that a template has been selected
 * @param callback
 */
verify_template_is_selected_customize = function(){
    $.ajax({
        url : "/explore/verify_template_is_selected",
        type : "GET",
        dataType: "json",
        success: function(data){
        	verifyTemplateIsSelectedCustomizeCallback(data);
        }
    });
}


/**
 * Callback of check template selected. Display an error message if not selected.
 * @param data
 */
verifyTemplateIsSelectedCustomizeCallback = function(data)
{
    console.log('BEGIN [verifyTemplateIsSelectedCallback]');

    if (data.templateSelected == 'no') {
        location.href = "/explore";
    }else{
    	loadExploreCurrentTemplateForm();
    }

    console.log('END [verifyTemplateIsSelectedCallback]');
}


/**
 * Generate a form to select fields to use in the query builder
 */
loadExploreCurrentTemplateForm = function()
{
    console.log('BEGIN [loadExploreCurrentTemplateForm]');

    $('.btn.clear-fields').on('click', clearFields);

    generate_xsd_tree_for_querying_data(); 

    console.log('END [loadExploreCurrentTemplateForm]');
}


/**
 * AJAX call, generates HTML tree from XSD
 */
generate_xsd_tree_for_querying_data = function(){
    $.ajax({
        url : "/explore/generate_xsd_tree_for_querying_data",
        type : "GET",
        dataType: "json",
        success: function(data){
            $("#xsdForm").html(data.xsdForm);
        }
    });
}


/**
 * Clear all check boxes of the form
 */
clearFields = function()
{
    console.log('BEGIN [clearFields]');

    // reset all select to their 0 index
    $('#dataQueryForm').find("select").each(function(){
	  this.selectedIndex = 0;
	  for (i=0; i < this.options.length;i++) {
	    if (i == 0){
	    		$("#" + this.id + "-" + i).removeAttr("style");
			} else {
	        $("#" + this.id + "-" + i).attr("style","display:none");
			}
	    	
	    }
	});
    // clear all checkboxes
    $("#dataQueryForm").find("input").each(function() {
    	$( this ).removeAttr('checked');
    });
    // display a message
    $(function() {
        $( "#dialog-cleared-message" ).dialog({
            modal: true,
            buttons: {
		Ok: function() {
                    $( this ).dialog( "close" );
                }
	    }
        });
    });
	
    console.log('END [clearFields]');
}

/**
 * Display errors
 */
displayErrors = function()
{
	$(function() {
        $( "#dialog-errors-message" ).dialog({
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
 * Comes back to the query, keeping the current criterias
 */
backToQuery = function()
{
	console.log('BEGIN [backToQuery]');
	
	back_to_query();
	
	console.log('END [backToQuery]');
}


/**
 * AJAX call, redirects to query builder
 */
back_to_query = function(){
    $.ajax({
        url : "/explore/back_to_query",
        type : "GET",
        dataType: "json",
        success: function(data){
        	window.location = "/explore/perform-search"    	
        }
    });
}

/**
 * Show the custom tree to choose a field for the query builder
 * @param criteriaID
 */
showCustomTree = function(currentCriteriaID)
{
	console.log('BEGIN [showCustomTree]');
	
	set_current_criteria(currentCriteriaID);
	
	$(function() {
        $( "#dialog-customTree" ).dialog({
            modal: true,
            width: 500,
            height: 620,
            buttons: {
		Close: function() {
                    $( this ).dialog( "close" );
                }
	    }
        });
    });
	
	console.log('END [showCustomTree]');
}


/**
 * AJAX call, set the id of the current criteria to be set
 * @param currentCriteriaID
 */
set_current_criteria = function(currentCriteriaID){
	$.ajax({
        url : "/explore/set_current_criteria",
        type : "POST",
        dataType: "json",
        data : {
        	currentCriteriaID : currentCriteriaID,
        }
    });
}


/**
 * Select an element to insert in the query builder
 * @param elementID
 */
selectElement = function(elementID)
{
	console.log('BEGIN [selectElement]');
		
	var elementName = $("#" + elementID).text().trim();
	select_element(elementID, elementName);
	
	console.log('END [selectElement]');
}


/**
 * AJAX call, select an element to insert in the query
 * @param elementID
 * @param elementName
 */
select_element = function(elementID, elementName){
	$.ajax({
        url : "/explore/select_element",
        type : "POST",
        dataType: "json",
        data : {
        	elementID: elementID,
        	elementName: elementName
        },
		success: function(data){
            $($("#" + data.criteriaTagID).children()[1]).val(elementName);
            $($("#" + data.criteriaTagID).children()[1]).attr("class","elementInput");
            updateUserInputs(elementID, data.criteriaID); 
            $("#dialog-customTree").dialog("close");    
	    }
    });
}

/**
 * Select an element from the custom tree, for subelement query
 * @param leavesID
 */
selectParent = function(leavesID)
{
	console.log('BEGIN [selectParent]');
	
	try{
		$("#dialog-customTree").dialog("close"); 
		subElementQuery(leavesID);
	}catch(err)
	{
		
	}
	console.log('END [selectParent]');
}

/**
 * Open the dialog to create a query on subelements of the same document
 * @param leavesID
 */
subElementQuery = function(leavesID)
{
	console.log('BEGIN [subElementQuery]');
	$(function() {
        $( "#dialog-subElementQuery" ).dialog({
            modal: true,
            width: 670,
            height: 420,
            buttons: {
		Close: function() {
                    $( this ).dialog( "close" );
                },
        Insert: function(){
        			var checkboxes = $("#subElementQueryBuilder").find("input:checkbox");
        			for(var i = 0; i < checkboxes.length; i++) {
        				checkboxes[i].setAttribute("value", checkboxes[i].checked);
        		    	if(checkboxes[i].checked == true)
        		    	{
        		    		checkboxes[i].setAttribute("checked","checked");
        		    	}
        		    }
        			$("input").each(function(){
        			    $(this).attr("value", $(this).val());
        			});
        			$('select option').each(function(){ this.defaultSelected = this.selected; });
        			var form = $("#subElementQueryBuilder").html();
        			insert_sub_element_query(leavesID, form);
        		}
            }
        });
    });
	
	prepare_sub_element_query(leavesID);
	console.log('END [subElementQuery]');
}


/**
 * AJAX call, inserts a sub query in the form
 * @param leavesID
 * @param form
 */
insert_sub_element_query = function(leavesID, form){
	$.ajax({
        url : "/explore/insert_sub_element_query",
        type : "POST",
        dataType: "json",
        data : {
        	leavesID: leavesID,
        	form: form
        },
		success: function(data){
			if ('listErrors' in data){
				$('#listErrors').html(data.listErrors);
				displayErrors();
			}else{
				// insert the pretty query in the query builder
	            $($("#" + data.criteriaID).children()[1]).attr("value", data.prettyQuery);
	            var field = $("#" + data.criteriaID).children()[1]
	            // replace the pretty by an encoded version
	            $(field).attr("value",$(field).html($(field).attr("value")).text())
	            // set the class to query
	            $($("#" + data.criteriaID).children()[1]).attr("class","queryInput");
	            // remove all other existing inputs
	            $("#" +data.uiID).children().remove();
	            // close the dialog
	            $("#dialog-subElementQuery").dialog("close");  
			}
	    }
    });
}


/**
 * AJAX call, preapres the sub element query
 * @param leavesID
 */
prepare_sub_element_query = function(leavesID){
	$.ajax({
        url : "/explore/prepare_sub_element_query",
        type : "GET",
        dataType: "json",
        data : {
        	leavesID: leavesID,
        },
		success: function(data){
			$("#subElementQueryBuilder").html(data.subElementQueryBuilder);    
	    }
    });
}


/**
 * Show an error message when no repository are selected
 */
showErrorInstancesDialog = function()
{
	$(function() {
        $( "#dialog-Instances" ).dialog({
            modal: true,
            buttons: {
            	OK: function() {
                    $( this ).dialog( "close" );
                }
            }
        });
    });
}

showhideResults = function(event)
{
	console.log('BEGIN [showhideResults]');
	button = event.target
	parent = $(event.target).parent()
	$(parent.children(".xmlResult")).toggle("blind",500);
	if ($(button).attr("class") == "expand"){
		$(button).attr("class","collapse");
	}else{
		$(button).attr("class","expand");
	}
		
	console.log('END [showhideResults]');
}

/**
 * Delete a curated document
 * @param result_id
 */
deleteResult = function(result_id){
	$(function() {
        $( "#dialog-delete-result" ).dialog({
            modal: true,
            buttons: {
            	Cancel: function() {
                    $( this ).dialog( "close" );
                },
            	Delete: function() {
                    $( this ).dialog( "close" );
                    delete_result(result_id);
                },
            }
        });
    });
}

/**
 * AJAX call, delete a curated document
 * @param result_id
 */
delete_result = function(result_id){
	$.ajax({
        url : "/explore/delete_result",
        type : "GET",
        dataType: "json",
        data : {
        	result_id: result_id,
        },
		success: function(data){
		        location.reload(true);
	    }
    });
}

/**
 * Publish a curated document
 * @param result_id
 */
updatePublish = function(result_id){
	$(function() {
        $( "#dialog-publish" ).dialog({
            modal: true,
            buttons: {
            	Cancel: function() {
                    $( this ).dialog( "close" );
                },
            	Publish: function() {
                    $( this ).dialog( "close" );
                    update_publish(result_id);
                },
            }
        });
    });
}

/**
 * AJAX call, update the publish state and date of a XMLdata
 * @param result_id
 */
update_publish = function(result_id){
	$.ajax({
        url : "/explore/update_publish",
        type : "GET",
        dataType: "json",
        data : {
        	result_id: result_id,
        },
		success: function(data){
		    $("#" + result_id).load(document.URL +  " #" + result_id);
	    }
    });
}

/**
 * Unpublish a curated document
 * @param result_id
 */
updateUnpublish = function(result_id){
	$(function() {
        $( "#dialog-unpublish" ).dialog({
            modal: true,
            buttons: {
            	Cancel: function() {
                    $( this ).dialog( "close" );
                },
            	Unpublish: function() {
                    $( this ).dialog( "close" );
                    update_unpublish(result_id);
                },
            }
        });
    });
}

/**
 * AJAX call, update the publish state of a XMLdata
 * @param result_id
 */
update_unpublish = function(result_id){
	$.ajax({
        url : "/explore/update_unpublish",
        type : "GET",
        dataType: "json",
        data : {
        	result_id: result_id,
        },
		success: function(data){
            $("#" + result_id).load(document.URL +  " #" + result_id);
	    }
    });
}

/**
 * Show/hide
 * @param event
 */
showhide = function(event){
	console.log('BEGIN [showhide]');
	button = event.target
	parent = $(event.target).parent()
	$(parent.children()[2]).toggle("blind",500);
	if ($(button).attr("class") == "expand"){
		$(button).attr("class","collapse");
	}else{
		$(button).attr("class","expand");
	}

	console.log('END [showhide]');
}

/**
 * Comes back to the query, keeping the current criterias
 */
backToResults = function()
{
	console.log('BEGIN [backToResults]');

	window.history.back()

	console.log('END [backToResults]');
}


clearExport = function() {
    $("#btn_errors").html("")
    $("#banner_errors").hide(200)
    $("#form_start_errors").html("");
    $("#form_start_current").html("");
    $("#results_errors").html("")
    $("#banner_results_errors").hide(200);
}


/**
* Export files
*/
exportRes = function() {

	console.log('BEGIN [downloadSelectedResults]');
    clearExport();
    var existOne = false;
    // Need to Set input values explicitiy before sending innerHTML for save
    var elems = document.getElementById("results").getElementsByTagName("input")
    var listId = [];
    for(var i = 0; i < elems.length; i++) {
    	if(elems[i].checked == true)
    	{
    	    existOne = true;
    	    listId.push(elems[i].getAttribute("result_id"));
    	}
    }

    if(existOne > 0){
        displayExportSelectedDialog(listId);
    }
    else
    {
        $("#btn_errors").html("Please select results to export");
        $("#banner_errors").show(500)
    }

	console.log('END [downloadSelectedResults]');
}


/**
 * Show a dialog when a result is selected
 */
displayExportSelectedDialog = function(listId)
{
    exist = load_start_form(listId);
    $(function() {
        $( "#dialog-message" ).dialog({
          modal: true,
          buttons:
              [
               {
                   text: "Export",
                   click: function() {

                            if(validateExport())
                            {
                               $(form_start).submit();
                               $( this ).dialog( "close" );
                            }
                   }
               }
              ]
        });
    });
}


load_start_form = function(listId){
	$.ajax({
        url : "/explore/start_export",
        type : "GET",
        dataType: "json",
        data : {
            listId : listId,
        },
        success: function(data){
            $("#form_start_errors").html("");
            $("#form_start_current").html(data.template);
        }
    });
}

validateExport = function(){
	errors = ""
	// check if an option has been selected
	selected_option = $( "#form_start" ).find("input:checkbox[name='my_exporters']:checked").val()
	selected_option_XSLT = $( "#form_start" ).find("input:checkbox[name='my_xslts']:checked").val()
	if (selected_option == undefined && selected_option_XSLT == undefined){
		errors = "No option selected. Please check export format."
	}

	if (errors != ""){
		$("#form_start_errors").html(errors);
		return (false);
	}else{
		return (true)
	}
}


clearSearch = function() {
    $("#results").html('Please wait...');
    $("#banner_errors").hide(200);
    $("#results_errors").html('');
    $("#banner_results_errors").hide(200);
    $("#results_infos").html('');
}

initAutocomplete = function() {
         $("#id_search_entry").tagit({
            allowSpaces: false,
            placeholderText : 'Enter keywords, or leave blank to retrieve all records',
            afterTagRemoved: function(event, ui) {
                clearSearch();
                $("#id_search_entry").tagit("addPlaceHolder", this.value);
                get_results_keyword_refined();
            },
            onTagAdded: function(event, ui) {
                $("#id_search_entry").tagit("removePlaceHolder", this.value);
            },
            afterTagAdded: function(event, ui) {
                get_results_keyword_refined();
            },
            autocomplete: ({
                search: function(event, ui) {
                    $("#loading").addClass("isloading");
                },
                response: function(event, ui) {
                    $("#loading").removeClass("isloading");
                },
                focus: function (event, ui) {
                   this.value = ui.item.label;
                   event.preventDefault(); // Prevent the default focus behavior.
                },
                source: function(request, response) {
                $.getJSON("/explore/get_results_by_instance_keyword", { keyword: request.term, schemas: getSchemas(), userSchemas: [], onlySuggestions: true, },
                function (data) {
                    response($.map(data.resultsByKeyword, function (item) {
                        if(item.label != '')
                        {
                            return {
                            label: item.label,
                            value: item.label
                            }
                        }
                 }));}
                )},
              minLength: 2,              
                select: function( event, ui ) {
                  this.value = ui.item.label;
                  $("#id_search_entry").tagit("createTag", this.value);
                return false;
                }
            })
        })
}


getSchemas = function(numInstance){
    var values = [];
    $('#id_my_schemas input:checked').each(function() {
        values.push(this.value);
    });

    return values;
}

showHide = function(button, id){
    $("#"+id).toggle("slow");
    var color = $(button).css("background-color");
    $("#"+id).css("color", color);
}

initBanner = function()
{
    $("[data-hide]").on("click", function(){
        $(this).closest("." + $(this).attr("data-hide")).hide(200);
    });
}
