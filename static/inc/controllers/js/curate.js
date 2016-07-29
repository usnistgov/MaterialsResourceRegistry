/**
 * 
 * File Name: curate.js
 * Author: Sharief Youssef
 *            sharief.youssef@nist.gov
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
        url : "/curate/verify_template_is_selected",
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
 * Display message to block access to enter data from first step.
 */
enterDataError = function()
{
    $(function() {
        $( "#dialog-enter-error-message" ).dialog({
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
 * Display message to block access to view data from first step.
 */
viewDataError = function()
{
    $(function() {
        $( "#dialog-view-error-message" ).dialog({
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
 * Load controllers for template selection
 */
loadTemplateSelectionControllers = function()
{
    console.log('BEGIN [loadTemplateSelectionControllers]');
    $('.btn.set-template').on('click', setCurrentTemplate);
    $('.btn.set-curate-user-template').on('click', setCurrentUserTemplate);

    init_curate();
    console.log('END [loadTemplateSelectionControllers]');    
}


/**
 * AJAX call, initializes curation
 */
init_curate = function(){
    $.ajax({
        url : "/curate/init_curate",
        type : "GET",
        dataType: "json",
        async: false,
    });
}


/**
 * Clear the fields of the current curated data
 */
clearFields = function()
{
    console.log('BEGIN [clearFields]');

    $(function() {
        $( "#dialog-cleared-message" ).dialog({
            modal: true,
            buttons: {
                Clear: function() {
                    clear_fields();
                    $( this ).dialog( "close" );
                },
                Cancel: function() {
                    $( this ).dialog( "close" );
                }
        }
        });
    });

    console.log('END [clearFields]');
}


/**
 * AJAX call, clears fields 
 */
clear_fields = function(){
    $.ajax({
        url : "/curate/clear_fields",
        type : "GET",
        dataType: "json",
        success: function(data){
            $("#xsdForm").html(data.xsdForm);

            $('link.module').each(function(index, item) {
                item.remove();
            });

            $('script.module').each(function(index, item) {
                item.remove();
            });

            initModules();
        }
    });
}

/**
 * Displays the current data to be curated
 */
viewData = function()
{
    console.log('BEGIN [viewData]');

    formContent = document.getElementById('xsdForm').innerHTML
    view_data(formContent);

    console.log('END [viewData]');
}


/**
 * AJAX call, redirects to View Data after sending the current form
 * @param formContent
 */
view_data = function(formContent){
    $.ajax({
        url : "/curate/view_data",
        type : "POST",
        dataType: "json",
        data : {
            form_content : formContent,
        },
        success: function(data){
            window.location = "/curate/view-data"
        }
    });
}


/**
 * Validate the current data to curate.
 */
validateXML = function()
{
    $.ajax({
        url : "/curate/validate_xml_data",
        type : "POST",
        dataType: "json",
        /*data : {
            xmlString : xmlString,
            xsdForm: xsdForm
        },*/
        success: function(data){
            if ('errors' in data){
                 $("#saveErrorMessage").html(data.errors);
                saveXMLDataToDBError();
            } else {
                useErrors = checkElementUse();

                if (useErrors.length > 0) {
                    useErrosAndView(useErrors);
                } else {
                    viewData();
                }
            }
        }
    });
}


function onlyUnique(value, index, self) {
    return self.indexOf(value) === index;
}


/**
 * Update the display regarding the choice of the user.
 * @param selectObj
 */
changeChoice = function(selectObj)
{
    console.log('BEGIN [changeChoice(' + selectObj.id + ' : ' + selectObj.selectedIndex + ')]');

    // get the index of the selected option 
    var idx = selectObj.selectedIndex;

    // change the displayed choice
    for (i=0; i < selectObj.options.length;i++) {
        if (i == idx){
            $("#" + selectObj.id + "-" + i).removeAttr("class");
        } else {
            $("#" + selectObj.id + "-" + i).attr("class","notchosen");
        }
    }
    // the choice is not yet generated
    if ($("#" + selectObj.id + "-" + idx).children().length == 0){
        // save values in the form
        $("input:text").each(function(){
            $(this).attr("value", $(this).val());
        });
        $('select option').each(function(){ this.defaultSelected = this.selected; });
        $("input:checkbox:not(:checked)").each(function(){

            $(this).removeAttr("checked");
        });
        $("input:checkbox:checked").each(function(){
        
            $(this).attr("checked", true);
        });
        $("textarea").each(function(){
            $(this).text($(this).val());
        });
        // generate selected choice
        generate(selectObj.id.substr(6) + "-" + idx, "choice");
    }

    console.log('END [changeChoice(' + selectObj.id + ' : ' + selectObj.selectedIndex + ')]');
}


/**
 * Show a dialog when a template is selected
 */
displayTemplateSelectedDialog = function()
{
    $(function() {
        $( "#dialog-message" ).dialog({
            modal: true,
            buttons: [{
                text: "Start",
                click: function() {
                    displayTemplateProcess();
                }
            }]
        });
    });
}

/**
* AJAX call, show the template
*/
displayTemplateProcess = function ()
{
    if (validateStartCurate()){
       var formData = new FormData($( "#form_start" )[0]);
       $.ajax({
            url: "/curate/start_curate",
            type: 'POST',
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            async:false,
            success: function(data){
                window.location = '/curate/enter-data'
            },
            error:function(data){
                if (data.responseText != ""){
                    $("#form_start_errors").html(data.responseText);
                    $("#banner_errors").show(500)
                    return (false);
                }else{
                    return (true);
                }
            },
        })
        ;
   }
}


/**
 * Check if the template is selected, to prevent manual navigation.
 */
verifyTemplateIsSelectedCurateEnterData = function(){
    console.log('BEGIN [verifyTemplateIsSelected]');

    verify_template_is_selected(verifyTemplateIsSelectedCurateEnterDataCallback);

    console.log('END [verifyTemplateIsSelected]');
}


/**
 * AJAX call, checks that a template has been selected
 * @param callback
 */
verify_template_is_selected = function(callback){
    $.ajax({
        url : "/curate/verify_template_is_selected",
        type : "GET",
        dataType: "json",
        success: function(data){
            callback(data.templateSelected);
        }
    });
}


/**
 * Callback redirects to main page if no templates selected.
 * @param data
 */
verifyTemplateIsSelectedCurateEnterDataCallback = function(templateSelected)
{
    console.log('BEGIN [verifyTemplateIsSelectedCallback]');

    if (templateSelected == 'no') {
        location.href = "/curate";
    }else{
        loadCurrentTemplateFormForCuration();
    }

    console.log('END [verifyTemplateIsSelectedCallback]');
}


/**
 * Load the form to curate data
 */
loadCurrentTemplateFormForCuration = function()
{
    console.log('BEGIN [loadCurrentTemplateFormForCuration]');

    $('.btn.clear-fields').on('click', clearFields);
    //$('.btn.save-form').on('click', saveForm);
    $('.btn.download').on('click', downloadOptions);

    generate_xsd_form();

    console.log('END [loadCurrentTemplateFormForCuration]');
}


/**
 * AJAX call, generates HTML form from XSD
 */
generate_xsd_form = function(){
    $.ajax({
        url : "/curate/generate_xsd_form",
        type : "GET",
        dataType: "json",
        success : function(data) {
            $('#modules').html(data.modules);
            $('#xsdForm').html(data.xsdForm);
            setTimeout(disable_elements ,0);

            initModules();
        },
    });
}


/**
 * Check that the tempalte is selected or redirect to main page
 */
verifyTemplateIsSelectedViewData = function(){
    console.log('BEGIN [verifyTemplateIsSelected]');

    verify_template_is_selected(verifyTemplateIsSelectedViewDataCallback);

    console.log('END [verifyTemplateIsSelected]');
}


/**
 * Check that the tempalte is selected or redirect to main page
 */
verifyTemplateIsSelectedViewDataCallback = function(data)
{
    console.log('BEGIN [verifyTemplateIsSelectedCallback]');

    if (data.templateSelected == 'no') {
        location.href = "/curate";
    }else{
        loadCurrentTemplateView();
        load_xml();
    }

    console.log('END [verifyTemplateIsSelectedCallback]');
}


/**
 * AJAX call, loads XML data into the page for review
 */
load_xml = function(){
    $.ajax({
        url : "/curate/load_xml",
        type : "GET",
        dataType: "json",
        success : function(data) {
            $('#XMLHolder').html(data.XMLHolder);
        }
    });
}


/**
 * Load template view controllers
 */
loadCurrentTemplateView = function()
{
    console.log('BEGIN [loadCurrentTemplateView]');

    $('.btn.download-xml').on('click', downloadXML);
    $('.btn.save-to-repo').on('click', saveToRepository);

    console.log('END [loadCurrentTemplateView]');
}


/**
 * Shows a dialog to choose dialog options
 */
downloadOptions = function()
{
 $(function() {
    $( "#dialog-download-options" ).dialog({
      modal: true,
      buttons: {
        Cancel: function() {
          $( this ).dialog( "close" );
        }
      }
    });
  });
}


/**
 * Download the XML document
 */
downloadXML = function()
{
    console.log('BEGIN [downloadXML]');

    download_xml();

    console.log('END [downloadXML]');
}


/**
 * AJAX call, get XML data and redirects to download view
 */
download_xml = function(){
    window.location = '/curate/download_xml';
}


/**
 * Download the XSD template
 */
downloadXSD = function()
{
    console.log('BEGIN [downloadXSD]');

    console.log('[downloadXSD] Downloading XSD...');
    
    window.location = '/curate/enter-data/download-XSD';
    $( "#dialog-download-options" ).dialog("close");
    
    console.log('[downloadXSD] Schema downloaded');

    console.log('END [downloadXSD]');
}


/**
 * Download the current XML document
 */
downloadCurrentXML = function()
{
    console.log('BEGIN [downloadCurrentXML]');

    window.location = '/curate/enter-data/download_current_xml'

    console.log('END [downloadCurrentXML]');
}


/**
 * Save XML data to repository. Shows dialog.
 */
saveToRepository = function()
{
    console.log('BEGIN [saveToRepository]');
    enterKeyPressSaveRepositorySubscription();

    $(function() {
        $( "#dialog-save-data-message" ).dialog({
          modal: true,
          buttons:
              [
               {
                   text: "Save",
                   click: function() {
	            	   saveToRepositoryProcess();
	            	   $( "#dialog-save-data-message" ).dialog( "close" );
                   }
               }
              ]
        });
      });


    console.log('END [saveToRepository]');
}

saveToRepositoryProcess = function(successFunction)
{
   var formData = new FormData($( "#form_save" )[0]);
   $.ajax({
        url : "/curate/save_xml_data_to_db",
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        async:false,
        success : function(data) {
            successFunction();
        },
        error:function(data){
            $("#saveErrorMessage").html(data.responseText);
        },
    });
}


XMLDataSavedToPublish = function()
{
    console.log('XMLDataSavedToPublish');
    $( "#dialog-save-redirect-dashboard-message" ).dialog({
        modal: true,
        width: 390,
        autoResize: 'auto',
        close: function(){
            window.location = "/"
        },
        buttons: {
            "Home": function() {
                $( this ).dialog( "close" );
                window.location = "/"
            },
            "Go to My Dashboard": function() {
                $( this ).dialog( "close" );
                window.location = "/dashboard/resources?ispublished=false"
            }
        }
    });
}

XMLDataUpdated = function(){
    $( "#dialog-update-redirect-dashboard-message" ).dialog({
        modal: true,
        width: 390,
        autoResize: 'auto',
        close: function(){
            window.location = "/"
        },
        buttons: {
            "Home": function() {
                $( this ).dialog( "close" );
                window.location = "/"
            },
            "Go to My Resources": function() {
                $( this ).dialog( "close" );
                window.location = "/dashboard/resources?ispublished=false"
            }
        }
    });
}


enterKeyPressSaveRepositorySubscription = function ()
{
    $('#id_title').keypress(function(event) {
        if(event.which == $.ui.keyCode.ENTER) {
            event.preventDefault();
            event.stopPropagation();
            saveToRepositoryProcess();
        }
    });
}

/**
 * Saved XML data to DB message.
 */
XMLDataSaved = function()
{
    console.log('BEGIN [savedXMLDataToDB]');


    $( "#dialog-saved-message" ).dialog({
        modal: true,
        width: 350,
        height: 215,
        close: function(){
            window.location = "/dashboard/resources?ispublished=false"
        },
        buttons: {
            Ok: function() {
                $( this ).dialog( "close" );
            }
    }
    });

    
    console.log('END [savedXMLDataToDB]');
}


/**
 * Save XML data to DB error message. 
 */
saveXMLDataToDBError = function()
{
    console.log('BEGIN [saveXMLDataToDBError]');
    
    $(function() {
        $( "#dialog-save-error-message" ).dialog({
            modal: true,
            buttons: {
                Ok: function(){
                    $(this).dialog("close");
                }
            }
        });
    });
    
    console.log('END [saveXMLDataToDBError]');
}


/**
 * Duplicate or remove an element
 * @param operation
 * @param tagID
 * @returns {Boolean}
 */
changeHTMLForm = function(operation, tagID)
{
    console.log('BEGIN [changeHTMLForm(' + operation + ')]');
    
    // save values in the form
    $("input:text").each(function(){
	    $(this).attr("value", $(this).val());
	});
	$('select option').each(function(){ this.defaultSelected = this.selected; });
	$("input:checkbox:not(:checked)").each(function(){
	    
	    $(this).removeAttr("checked");
	});
	$("input:checkbox:checked").each(function(){
    
        $(this).attr("checked", true);
    });
    $("textarea").each(function(){
        $(this).text($(this).val());
    });

    if (operation == 'add') {
        // the element has to be created
        if ($("#element"+tagID).children("ul").length == 0 && // complex element not generated
        $("#element"+tagID).children("input").length == 0 && // input element not generated
        $("#element"+tagID).children("select").length == 0 && // enumeration not generated 
        $("#element"+tagID).children("div.module").length == 0){ // module not generated
            generate(tagID, "element");
        }
        else{
            // the element is already generated
            $("#element"+tagID).children(".expand").attr("class","collapse");
            duplicate(tagID);
        }
    } else if (operation == 'remove') {
        $("#element"+tagID).children(".collapse").attr("class","expand");
        remove(tagID);
    }

    console.log('END [changeHTMLForm(' + operation + ')]');

    return false;
}


/**
 * AJAX call, generate an element from the form
 * @param tagID HTML id of the element to generate
 */
generate = function(tagID, tag){
    var xsdForm = $("#xsdForm").html();
    $.ajax({
        url : "/curate/generate",
        type : "POST",
        dataType: "json",
        data : {
            tagID : tagID,
            tag: tag,
            xsdForm: xsdForm
        },
        success: function(data){
            $("#xsdForm").html(data.xsdForm);
            $("#element" + tagID).prop("disabled",false);
            $("#element" + tagID).children('select').prop("disabled",false);
            $("#element" + tagID).removeClass("removed");
            $("#element" + tagID).children("ul").show(500);

            initModules();
        }
    });
}

/**
 * AJAX call, duplicate an element from the form
 * @param tagID HTML id of the element to duplicate
 */
duplicate = function(tagID){
    $.ajax({
        url : "/curate/can_duplicate",
        type : "POST",
        dataType: "json",
        data : {
            tagID : tagID,
        },
        success: function(data){
            if ('occurs' in data){
                if (data.occurs == "zero"){
                    $('#add' + data.id).attr('style', data.styleAdd);
                    $('#remove' + data.id).attr('style','');
                    $("#" + data.tagID).prop("disabled",false);
                    $("#" + data.tagID).children('select').prop("disabled",false);
                    $("#" + data.tagID).removeClass("removed");
                    $("#" + data.tagID).children("ul").attr('style','');
                    if($("#element"+tagID).attr("class").split(" ").indexOf("choice") > -1 && $("#element"+tagID).children("ul").children().length == 0){ // choice element not generated
                        changeChoice($("#element"+tagID).children("select")[0]);
                    }
                }
                else{
                    var xsdForm = $("#xsdForm").html();

                    $.ajax({
                        url : "/curate/duplicate",
                        type : "POST",
                        dataType: "json",
                        data : {
                            tagID : tagID,
                            xsdForm: xsdForm
                        },
                        success: function(data){
                            $("#xsdForm").html(data.xsdForm);
                        }
                    });
                }
            }
        }
    });
}

/**
 * disable removed element
 * @param tagID HTML id of the element to disable
 */
disable_element = function(tagID){
    $("#" + tagID).children(".collapse").attr("class","expand");
    $('#add' + tagID.substring(7)).attr('style','');
    $('#remove' + tagID.substring(7)).attr('style','display:none');
    $("#" + tagID).prop("disabled",true);
    $("#" + tagID).children('select').prop("disabled",true);
    $("#" + tagID).children("ul").hide();
}

/**
 * disable all removed elements
 * @param tagID HTML id of the element to disable
 */
disable_elements = function(){
    $("#xsdForm").find(".removed").each(function(){
        disable_element($(this).attr('id'));
    });
}

/**
 * AJAX call, remove an element from the form
 * @param tagID HTML id of the element to remove
 */
remove = function(tagID){
$.ajax({
        url : "/curate/can_remove",
        type : "POST",
        dataType: "json",
        data : {
            tagID : tagID,
        },
        success: function(data){
            if ('occurs' in data){
                if (data.occurs === "zero"){
                    $("#" + data.tagID).addClass("removed");
                    $('#add' + data.tagID.substring(7)).attr('style','');
                    $('#remove' + data.tagID.substring(7)).attr('style','display:none');
                    $("#" + data.tagID).prop("disabled",true);
                    $("#" + data.tagID).children('select').prop("disabled",true);
                    $("#" + data.tagID).children("ul").hide(500);
                }else{
                    var xsdForm = $("#xsdForm").html();
                    $.ajax({
                        url : "/curate/remove",
                        type : "POST",
                        dataType: "json",
                        data : {
                            tagID : tagID,
                            xsdForm: xsdForm
                        },
                        success: function(data){
                            $("#xsdForm").html(data.xsdForm);
                        }
                    });
                }
            }
        }
    });
}


/**
 * Set the current template 
 * @returns {Boolean}
 */
setCurrentTemplate = function()
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
        url : "/curate/set_current_template",
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
 * Set current user defined template
 * @returns {Boolean}
 */
setCurrentUserTemplate = function()
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
        url : "/curate/set_current_user_template",
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
 * AJAX call, loads the start curate form
 */
load_start_form = function(){
    $.ajax({
        url : "/curate/start_curate",
        type : "GET",
        dataType: "json",
        data : {

        },
        success: function(data){
            $("#banner_errors").hide()
            $("#form_start_content").html(data.template);
            enterKeyPressSubscription();
        }
    });
}


/**
 * 
 */
enterKeyPressSubscription = function ()
{
    $('#dialog-message').keypress(function(event) {
        if(event.which == $.ui.keyCode.ENTER) {
            event.preventDefault();
            event.stopPropagation();
            displayTemplateProcess();
        }
    });
}


syncRadioButtons =function()
{
	// auto set radio buttons value according to what option the user is choosing
	$("#id_document_name").on("click", function(){$("input:radio[name=curate_form][value='new']").prop("checked", true)});
	$("#id_forms").on("change", function(){$("input:radio[name=curate_form][value='open']").prop("checked", true)});
	$("#id_file").on("change", function(){$("input:radio[name=curate_form][value='upload']").prop("checked", true)});
}


/**
 * Validate fields of the start curate form
 */
validateStartCurate = function(){
    var errors = "";

	$("#banner_errors").hide()
	// check if an option has been selected
	selected_option = $( "#form_start" ).find("input:radio[name='curate_form']:checked").val()
	if (selected_option == undefined){
		errors = "No option selected. Please check one radio button."
		$("#form_start_errors").html(errors);
		$("#banner_errors").show(500)
		return (false);
	}else{
		if (selected_option == "new"){
			if ($( "#id_document_name" ).val().trim() == ""){
				errors = "You selected the option 'Create a new document'. Please provide a name for the document."
			}
		}else if (selected_option == "open"){
			if ($( "#id_forms" ).val() == ""){
				errors = "You selected the option 'Open a Form'. Please select a form from the list."
			}
		}else if (selected_option == "upload"){
			if ($( "#id_file" ).val() == ""){
				errors = "You selected the option 'Upload a File'. Please select an XML file."
			}
		}
	}
		
	if (errors != ""){
		$("#form_start_errors").html(errors);
		$("#banner_errors").show(500)
		return (false);
	}else{
		return (true)
	}	
}


/**
 * Update page when template selected.
 * @param data
 */
setCurrentTemplateCallback = function()
{
    console.log('BEGIN [setCurrentTemplateCallback]');

    $('#template_selection').load(document.URL +  ' #template_selection', function() {
        loadTemplateSelectionControllers();
        displayTemplateSelectedDialog();
    });

    load_start_form();

    console.log('END [setCurrentTemplateCallback]');
}


/**
 * Delete a form
 * @param formID
 */
deleteForm = function(formID){
	$(function() {
        $( "#dialog-delete-form" ).dialog({
            modal: true,
            buttons: {
                Cancel: function() {
                    $( this ).dialog( "close" );
                },
            	Delete: function() {
                    delete_form(formID);
                    $( this ).dialog( "close" );
                },
            }
        });
    });
}


/**
 * AJAX call, delete a form
 * @param formID
 */
delete_form = function(formID){
	$.ajax({
        url : "/curate/delete-form?id=" + formID,
        type : "GET",
        dataType: "json",
        data : {
        	formID: formID,
        },
		success: function(data){
			window.location = "/dashboard/drafts"
	    },
        error:function(data){
        	window.location = "/dashboard/drafts"
        }
    });
}


/**
 * Change form owner
 * @param formID
 */
changeOwnerForm = function(formID){
    $("#banner_errors").hide();
	$(function() {
        $( "#dialog-change-owner-form" ).dialog({
            modal: true,
            buttons: {
                Cancel: function() {
                    $( this ).dialog( "close" );
                },
                "Change": function() {
                    if (validateChangeOwner()){
                        var formData = new FormData($( "#form_start" )[0]);
                        change_owner_form(formID);
                        $( this ).dialog( "close" );
                    }
                },
            }
        });
    });
}

/**
 * Validate fields of the start curate form
 */
validateChangeOwner = function(){
	errors = ""

	$("#banner_errors").hide()
	// check if a user has been selected
    if ($( "#id_users" ).val().trim() == ""){
        errors = "Please provide a user."
    }

	if (errors != ""){
		$("#form_start_errors").html(errors);
		$("#banner_errors").show(500)
		return (false);
	}else{
		return (true);
	}
}


/**
 * AJAX call, change form owner
 * @param formID
 */
change_owner_form = function(formID){
    var userId = $( "#id_users" ).val().trim();
	$.ajax({
        url : "/curate/change-owner-form",
        type : "POST",
        dataType: "json",
        data : {
        	formID: formID,
        	userID: userId,
        },
		success: function(data){
			window.location = "/dashboard/drafts"
	    },
        error:function(data){
        	window.location = "/dashboard/drafts"
        }
    });
}

/**
 * AJAX call, cancel a form currently being entered
 */
cancelForm = function(){
	$(function() {
        $( "#dialog-cancel-message" ).dialog({
            modal: true,
            buttons: {
                Cancel: function() {
                    $( this ).dialog( "close" );
                },
            	Confirm: function() {
            		$.ajax({
            	        url : "/curate/cancel-form",
            	        type : "GET",
            	        dataType: "json",
            			success: function(data){
            				window.location = "/curate"
            		    },
            	    });
                },
            }
        });
    });
}

cancelChanges = function(){
    // GET the form, if not loaded (1 because at least csrf token)
    if( $( "#cancel-form" ).children().size() == 1){
        $.ajax({
            url : "/curate/cancel-changes",
            type : "GET",
            dataType: "json",
            success: function(data){
                $("#cancel-form").append(data.form);
            },
        });
    }

    $( "#dialog-cancel-changes-message" ).dialog({
        modal: true,
        autoResize: 'auto',
        width: 650,
        buttons: {
            "Cancel": function() {
                $( this ).dialog( "close" );
            },
            "OK": function() {
                // POST the form
                var formData = new FormData($( "#cancel-form" )[0]);
                $.ajax({
                    url : "/curate/cancel-changes",
                    type : "POST",
                    cache: false,
                    contentType: false,
                    processData: false,
                    async:false,
                    data: formData,
                    success: function(data){
                        if(data == 'revert'){
                            reload_form();
                        }else{
                            window.location = '/curate';
                        }
                    },
                });
                $( this ).dialog( "close" );
            },
        }
    });
}


reload_form = function(){
    $.ajax({
        url : "/curate/reload-form",
        type : "GET",
        dataType: "json",
        success: function(data){
            $("#xsdForm").html(data.xsdForm);
        },
    });
}


/**
 * Check required, recommended elements
 */
checkElementUse = function(){
    required_count = 0
    $(".required:visible").each(function(){
        if (!$(this).closest("li").hasClass("removed")){
          if($(this).val().trim() == ""){
            required_count += 1;
          }
        }
    });

    recommended_count = 0
    $(".recommended:visible").each(function(){
        if (!$(this).closest("li").hasClass("removed")){
          if($(this).val().trim() == ""){
              recommended_count += 1;
          }
        }
    });

    errors = ""
    if (required_count > 0 || recommended_count > 0){
        errors = "<ul>"
        errors += "<li>" + required_count.toString() + " required element(s) are empty.</li>"
        errors += "<li>" + recommended_count.toString() + " recommended element(s) are empty.</li>"
        errors += "</ul>"
    }

    return errors;
}

/**
 * Displays use error before viewing data
 */
useErrosAndView = function(errors){
	$("#useErrorMessage").html(errors);
	$(function() {
        $( "#dialog-use-message" ).dialog({
            modal: true,
            autoResize: 'auto',
            width: 500,
            buttons: {
            	Cancel: function() {
            		$( this ).dialog( "close" );
                },
                Proceed: function() {
                    viewData();
                },
            },
            close: function(){
            	$("#useErrorMessage").html("");
            }
        });
    });
}

initBanner = function()
{
    $("[data-hide]").on("click", function(){
        $(this).closest("." + $(this).attr("data-hide")).hide(200);
    });
}

check_leaving_page = function(){
    window.btn_clicked = false;         // set btn_clicked to false on load
    document.querySelector('.save-to-repo').addEventListener("click", function(){
        window.btn_clicked = true;      //set btn_clicked to true
    });

    $(window).bind('beforeunload', function(){
        if(!window.btn_clicked){
            return 'Are you sure you want to leave the page. All unsaved changes will be lost.';
        }
    });
}

/**
* AJAX call, redirects to enter data
*/
load_enter_data = function (template_name)
{
    if (validateStartCurate()){
        var formData = new FormData($( "#form_start" )[0]);
        $.ajax({
            url: "/curate/start_curate",
            type: 'POST',
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            async:false,
            success: function(data){
                init_curate();
                window.location = '/curate/enter-data?template=' + template_name
            },
            error:function(data){
                if (data.responseText != ""){
                    $("#form_start_errors").html(data.responseText);
                    $("#banner_errors").show(500)
                    return (false);
                }else{
                    return (true)
                }
            },
        })
        ;
   }
}
