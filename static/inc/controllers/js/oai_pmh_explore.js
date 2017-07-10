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
			   $("#" + result_id).remove();
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
    $("#btn_errors").html('');
    $("#banner_errors").hide(200);
    $("#results_errors").html('');
    $("#banner_results_errors").hide(200);
    $("#results").html('');
    $("#results_local").html('');
    $("#results_infos").html('');
    $("#results_infos_local").html('');
}

verificationSearch = function() {
    isOK = true;
    if($("#id_my_schemas").length == 0)
    {
        $("#results_errors").html("<i class='fa fa-info fa-2x'></i>  Please wait for schemas.");
        $("#banner_results_errors").show(200);
        isOK = false;
    }
    return isOK;
}

/**
 * AJAX call, gets query results
 * @param numInstance
 */
get_results_keyword = function(numInstance){
    $("#id_search_entry").tagit("createTagIfNeeded");
    // clear the timeout
	clearTimeout(timeout);
	// send request if no parameter changed during the timeout
    if (verificationSearch())
    {
        timeout = setTimeout(function(){
            clearSearch();
            $("#banner_results_wait").show(200);
            var keyword = $("#id_search_entry").val();
            //Call to AJAX functions and wait for the end
//            $.when(AJAXOAIPMH(keyword), AJAXLocal(keyword)).done(function(a1, a2){
            $.when(AJAXOAIPMH(keyword)).done(function(a1){
                $("#banner_results_wait").hide(200);
            });
        }, 1000);
    }
}

AJAXOAIPMH = function (keyword)
{
    //OAI-PMH Search
    $("#banner_tab_results_wait").show(200);
    return $.ajax({
        url : "get_results_by_instance_keyword",
        type : "POST",
        dataType: "json",
        data : {
            keyword: keyword,
            schemas: getSchemas(),
            onlySuggestions: false,
        },
        success: function(data){
            if(data.count > 1)
                $("#results_infos").html(data.count + " results");
            else
                $("#results_infos").html(data.count + " result");
            $("#results").html(data.resultString);
            $("#banner_tab_results_wait").hide(200);
        }
    });
}

AJAXLocal = function (keyword)
{
    //LOCAL Search
    var localSchemas = getLocalSchema();
    if(localSchemas.length > 0)
    {
       $("#banner_tab_results_local_wait").show(200);
       return $.ajax({
            url : "/explore/get_results_by_instance_keyword",
            type : "POST",
            dataType: "json",
            data : {
                keyword: keyword,
                schemas: localSchemas,
                onlySuggestions: false,
            },
            success: function(data){
                if(data.count > 1)
                    $("#results_infos_local").html(data.count + " results");
                else
                    $("#results_infos_local").html(data.count + " result");
                $("#results_local").html(data.resultString);
                $("#banner_tab_results_local_wait").hide(200);
            }
        });
    }
}


initAutocomplete = function() {
         $("#id_search_entry").tagit({
            allowSpaces: false,
            placeholderText : 'Enter keywords, or leave blank to retrieve all records',
            afterTagRemoved: function(event, ui) {
                clearSearch();
                $("#id_search_entry").tagit("addPlaceHolder", this.value);
            },
            onTagAdded: function(event, ui) {
                $("#id_search_entry").tagit("removePlaceHolder", this.value);
            },
            afterTagAdded: function(event, ui) {
                get_results_keyword();
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
                $.post("get_results_by_instance_keyword", { keyword: request.term, schemas: getSchemas(),
                 onlySuggestions: true, csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val() },
                function (data) {
                    response($.map(data.resultsByKeyword, function (item) {
                        if(item.label != '')
                        {
                            return {
                            label: item.label,
                            value: item.label
                            }
                        }
                 }));}, 'json'
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

getLocalSchema = function(numInstance){
    var values = [];
    $('#id_my_schemas input:checked').each(function() {
        var obj = jQuery.parseJSON(this.value);
        if(obj.local)
            values.push(obj.local);
    });

    return values;
}


getRegistries = function(numInstance){
    var values = [];
    $('#id_my_registries input:checked').each(function() {
        values.push(this.value);
    });

    return values;
}

initResources = function(){
	$("#refine_resource").find("input[type=checkbox]").change(function(){
	    get_results_keyword();
	});
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

initMetadataFormats = function(){
	$("#registries").find("input[type=checkbox]").change(function(){
	    get_metadata_formats();
	});
	get_metadata_formats();
}


disableKeywordSearch = function()
{
    $('#submit').prop('disabled', true)
    $('.ui-autocomplete-input').prop('disabled', true).val('');
}

enableKeywordSearch = function()
{
    $('.ui-autocomplete-input').prop('disabled', false);
    $('#submit').prop('disabled', false)
}


/**
 * AJAX call, get metadata format for the selected registries
 * @param
 */
get_metadata_formats = function(){
    disableKeywordSearch();
    $("#metadataFormats").html("");
    $("#metadataFormats").hide(200);
    $("#wait_metadat_formats").show(200);
    clearSearch();
    // clear the timeout
	clearTimeout(timeout);
	// send request if no parameter changed during the timeout
    timeout = setTimeout(function(){
        $.ajax({
            url : "get_metadata_formats",
            type : "GET",
            dataType: "json",
            data : {
                registries: getRegistries(),
            },
            success: function(data){
                $("#wait_metadat_formats").hide(200);
                $("#metadataFormats").html(data.form);
                $("#metadataFormats").show(200);
                enableKeywordSearch();
//                $("<span>Select/Deselect All</span>").insertBefore("ul[id^=id_my_schemas_]");
//                $("<input checked='' type='checkbox' style='float: left;' onclick='handleCheckBoxMDF(this);'>").insertBefore("#id_my_schemas > li");
            }
        });
    }, 1000);
}


viewMetadataFormats = function(metadataFormats){
	$.ajax({
        url : "get_metadata_formats_detail",
        type : "GET",
        dataType: "json",
        data : {
            metadataFormats: metadataFormats,
        },
        success: function(data){
        	$("#metadataformats_detail").html(data);
        	$(function() {
                $( "#dialog-detail-metadataformats" ).dialog({
                    modal: true,
                    height: 'auto',
                    width: 'auto',
                    buttons: {
                        Ok: function() {
                            $( this ).dialog( "close" );
                        }
                    }
                });
            });
        }
    });
}