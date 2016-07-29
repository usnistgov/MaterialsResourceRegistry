var emptyEntry = '----------'
//Refresh Time in second
var refreshTime = 30;
////////////////////////////////////////////////
///////// OAI Data Provider Management /////////
////////////////////////////////////////////////

/**
 * Clear DP add form
 */
clearAdd = function ()
{
    clearAddError();
    $( "#form_add" )[0].reset();
}

/**
 * Clear DP add error banner
 */
clearAddError = function ()
{
    $("#banner_add_errors").hide()
    $("#form_add_errors").html("");
}

/**
 * Clear DP edit error banner
 */
clearEditError = function ()
{
    $("#banner_edit_errors").hide()
    $("#form_edit_errors").html("");
}

/**
 * Display the add form
 */
displayAddRegistry = function()
{
 $(function() {
    clearAdd();
    $( "#dialog-registry" ).dialog({
      modal: true,
      width: 550,
      height: 'auto',
      buttons:
    	  [
    	  {
               text: "Cancel",
               click: function() {
                        $( this ).dialog( "close" );
                    }
           },
           {
               text: "Add",
               click: function() {
                    clearAddError();
                    if(validateRegistry())
                    {
                       $("#banner_add_wait").show(200);
                       var formData = new FormData($( "#form_add" )[0]);
	            	   $.ajax({
	            	        url: "add/registry",
	            	        type: 'POST',
	            	        data: formData,
	            	        cache: false,
	            	        contentType: false,
	            	        processData: false,
	            	        async:true,
	            	   		success: function(data){
                                window.location = 'oai-pmh'
	            	        },
	            	        error:function(data){
	            	            $("#banner_add_wait").hide(200);
	            	        	$("#form_add_errors").html(data.responseText);
                                $("#banner_add_errors").show(200)
	            	        },
	            	    })
	            	    ;
                    }
               }
           }
          ]
    });
  });
}

/**
 * Validate add registry entries
 */
validateRegistry = function()
{
    errors = ""
    if ($( "#id_url" ).val().trim() == ""){
        errors += "<li>Please enter a URL.</li>"
    }
    harvest = $( "#id_harvestrate" ).val();
    if (!(Math.floor(harvest) == harvest && $.isNumeric(harvest) && harvest > 0)){
        errors += "<li>Please enter a positive integer.</li>"
    }
	if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_add_errors").html(errors);
		$("#banner_add_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}

/**
 * Validate edit registry entries
 */
validateRegistryEdit = function()
{
    errors = ""

    harvest = $( "#form_edit_current #id_harvestrate" ).val();
    if (harvest.trim() == ''){
        errors += "<li>Please enter an  harvest rate.</li>"
    }
    else if (!(Math.floor(harvest) == harvest && $.isNumeric(harvest) && harvest > 0)){
        errors += "<li>Please enter a positive integer.</li>"
    }

    if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_edit_errors").html(errors);
		$("#banner_edit_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}


/**
 * AJAX call, Show a dialog for editing DP values
 */
editRegistry = function(registryId)
{
    exist = load_edit_form(registryId);
    $(function() {
        $( "#dialog-edit" ).dialog({
          modal: true,
          width: 400,
          height: 'auto',
          buttons:
              [
               {
                   text: "Edit",
                   click: function() {
                        clearEditError();
                        if(validateRegistryEdit())
                        {
                            var formData = new FormData($( "#form_edit" )[0]);
                            $.ajax({
                                url: "update/registry",
                                type: 'POST',
                                data: formData,
                                cache: false,
                                contentType: false,
                                processData: false,
                                async:false,
                                success: function(data){
                                    window.location = 'oai-pmh'
                                },
                                error:function(data){
                                    $("#form_edit_errors").html(data.responseText);
                                    $("#banner_edit_errors").show(200)
                                },
                            })
                            ;
                        }
                   }
               }
              ]
        });
    });
}

/**
 * AJAX call, Load the edit form
 * @param registry Id
 */
load_edit_form = function(registryId){
	$.ajax({
        url : "update/registry",
        type : "GET",
        dataType: "json",
        data : {
            registry_id : registryId,
        },
        success: function(data){
            $("#form_edit_errors").html("");
            $("#form_edit_current").html(data.template);
            Reinit();
        }
    });
}

/**
 * Delete the registry
 * @param registry_id Registry Id
 */
deleteRegistry = function(registry_id)
{
 $(function() {
    $( "#dialog-confirm-delete" ).dialog({
      modal: true,
      buttons:{
                Cancel: function() {
	                $( this ).dialog( "close" );
                },
            	Delete: function() {
            		delete_registry(registry_id);
                },

		    }
    });
  });
}

/**
 * AJAX call, deletes a Registry
 * @param registry_id id of the registry
 */
delete_registry = function(registry_id){
    $("#banner_delete_wait").show(200);
    $.ajax({
        url : 'delete/registry',
        type : "POST",
        dataType: "json",
        data : {
        	RegistryId : registry_id,
        },
        success: function(data){
            window.location = 'oai-pmh'
        },
        error:function(data){
            $("#banner_delete_wait").hide(200);
            $("#form_delete_errors").html(data.responseText);
            $("#banner_delete_errors").show(200);
	    }
    });
}


/**
 * Deactive the registry
 * @param registry_id Registry Id
 */
deactivateRegistry = function(registry_id)
{
 $(function() {
    $( "#dialog-confirm-delete" ).dialog({
      modal: true,
      buttons:{
                Cancel: function() {
	                $( this ).dialog( "close" );
                },
            	Delete: function() {
            		deactivate_registry(registry_id);
                },

		    }
    });
  });
}

/**
 * AJAX call, Deactive a Registry
 * @param registry_id id of the registry
 */
deactivate_registry = function(registry_id){
    $("#banner_delete_wait").show(200);
    $.ajax({
        url : 'deactivate/registry',
        type : "POST",
        dataType: "json",
        data : {
        	RegistryId : registry_id,
        },
        success: function(data){
            window.location = 'oai-pmh'
        },
        error:function(data){
            $("#banner_delete_wait").hide(200);
            $("#form_delete_errors").html(data.responseText);
            $("#banner_delete_errors").show(200);
	    }
    });
}

/**
 * AJAX call, Reactive a Registry
 * @param registry_id id of the registry
 */
reactivateRegistry = function(registry_id){
    $("#banner_delete_wait").show(200);
    $.ajax({
        url : 'reactivate/registry',
        type : "POST",
        dataType: "json",
        data : {
        	RegistryId : registry_id,
        },
        success: function(data){
            window.location = 'oai-pmh'
        },
        error:function(data){

	    }
    });
}

/**
 * AJAX call, Check all status
 */
checkAllStatus = function ()
{
    var registriesCheck = $("td[id^=Status]")

    $.each(registriesCheck, function(index, props) {
         checkStatus($(props).attr('registryID'), $(props).attr('url'));
    });
}

/**
 * AJAX call, check status of a registry
 * @param registry_id id of the registry
 */
checkStatus = function (registry_id, url)
{
    $("#Status"+registry_id).css("color", "#000000");
    $("#Status"+registry_id).html('<i class="fa fa-spinner fa-spin"></i>');
    $.ajax({
        url : 'check/registry',
        type : "POST",
        dataType: "json",
        async: true,
        data : {
        	url : url,
        },

        success: function(data){
            if (data.isAvailable)
            {
                $("#Status"+registry_id).html('<i class="fa fa-signal"></i> Available');
                $("#Status"+registry_id).css("color", "#5cb85c");
            }
            else {
                $("#Status"+registry_id).html('<i class="fa fa-signal"></i> Unavailable');
                $("#Status"+registry_id).css("color", "#d9534f");
            }
        },
        error:function(data){
            $("#Status"+registry_id).html('<i class="fa fa-warning"></i> Error while checking');
            $("#Status"+registry_id).css("color", "#d9534f");
        },
    });
}

/**
 * AJAX call, view registry's information
 * @param registry_id of the registry
 */
viewRegistry = function(registry_id){
    $( "#pleaseWaitDialog").show();
	$.ajax({
        url : "oai-pmh-detail-registry?id=" + registry_id,
        type : "GET",
        success: function(data){
            $( "#pleaseWaitDialog").hide();
        	$("#registry_detail").html(data);
        	$(function() {
                $( "#dialog-detail-registry" ).dialog({
                    modal: true,
                    height: 530,
                    width: 700,
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

/**
 * AJAX call, harvest all data
 */
harvestAllData = function ()
{
    var registriesCheck = $("span[id^=harvest]:visible")

    $.each(registriesCheck, function(index, props) {
         harvestData($(props).attr('registryID'));
    });
}


/**
 * AJAX call, harvest data for a Registry
 * @param registry_id id of the registry
 */
harvestData = function(registry_id){
    $("#banner"+registry_id).show(200);
    $("#harvest"+registry_id).hide(200);
    $.ajax({
        url : 'harvest',
        type : "POST",
        dataType: "json",
        async: true,
        data : {
        	registry_id : registry_id,
        },
        success: function(data){
            checkHarvestData();
        },
        error:function(data){
	    }
    });
}

/**
 * AJAX call, check harvest data for all Registries
 */
checkHarvestData = function()
{
    return $.ajax({
        url : 'check/harvest-data',
        type : "POST",
        dataType: "json",
        async: true,
        data : {
        },
        success: function(data){
            $.map(data, function (item) {
                if(item.isHarvesting)
                {
                    $("#harvest" + item.registry_id).hide(200);
                    $("#banner"+ item.registry_id).show(200);
                }
                else
                {
                    $("#banner"+ item.registry_id).hide(200);
                    $("#harvest" + item.registry_id).show(200);
                    if(item.lastUpdate != '')
                        $("#lastUpdate"+ item.registry_id).html(item.lastUpdate);
                }
             });
        },
        error:function(data){
	    }
    });
}

/**
 * AJAX call, Show a dialog for editing DP values
 */
updateRegistryInfos = function(registry_id)
{
    $("#bannerUpdate"+registry_id).show(200);
    $("#update"+registry_id).hide(200);
    $.ajax({
        url: "update/registry-info",
        type : "POST",
        dataType: "json",
        async: true,
        data : {
        	registry_id : registry_id,
        },
        success: function(data){
            checkUpdateData();
        },
        error:function(data){
        },
    });
}

/**
 * AJAX call, check update data for all Registries
 */
checkUpdateData = function()
{
    return $.ajax({
        url : 'check/update-info',
        type : "POST",
        dataType: "json",
        async: true,
        data : {
        },
        success: function(data){
            $.map(data, function (item) {
                if(item.isUpdating)
                {
                    $("#update" + item.registry_id).hide(200);
                    $("#bannerUpdate"+ item.registry_id).show(200);
                }
                else
                {
                    $("#bannerUpdate"+ item.registry_id).hide(200);
                    $("#update" + item.registry_id).show(200);
                    $("#name"+ item.registry_id).html(item.name);
                }
             });
        },
        error:function(data){
	    }
    });
}


/**
 * AJAX call, check data providers info
 */
checkInfo = function() {
    $.when(checkUpdateData(), checkHarvestData()).done(function(a1, a2){
        $('#Refreshing').hide();
        $('#RefreshInfo').show();
        //Refresh every 30 seconds
        refreshInfo(refreshTime);
    });
}

refreshInfo = function(remaining) {
    if(remaining === 0)
    {
        $('#RefreshInfo').hide();
        $('#Refreshing').show();
        checkInfo();
        return;
    }
    $('#countdown').html(remaining);
    setTimeout(function(){ refreshInfo(remaining - 1); }, 1000);
}

////////////////////////////////////////////////
////////////////////////////////////////////////
////////////////////////////////////////////////



////////////////////////////////////////////////
/////////////// Build Request //////////////////
////////////////////////////////////////////////

/**
* Perform check before submit
*/
checkSubmit = function() {
    $("#build_errors").html("");
    $("#banner_build_errors").hide(200);
    $("#downloadXML").hide();
    $("#result").text('');
    var label = '';
    if ($("select#id_dataProvider").val() == '0') {
        label = 'Please pick a data provider.';
    } else if ($("select#id_verb").val() == '0') {
        label = 'Please pick a verb.';
    } else {
        if ($("select#id_verb").val() == '2') {
            if ($("select#id_metadataprefix").val() == '0') {
                label = 'Please pick a metadata prefix.';
            } else if ($("#id_identifiers").val().trim() == '') {
                label = 'Please provide an identifier.';
            }
        } else if ($("select#id_verb").val() == '3' || $("select#id_verb").val() == '5') {
            if ($("select#id_metadataprefix").val() == '0' && $("#id_resumptionToken").val() == '') {
                label = 'Please pick a metadata prefix.';
            }
        }
    }
    if (label == '') {
        submit();
    } else {
        $("#banner_build_errors").show(200);
        $("#build_errors").html(label);
    }
}

submit = function() {
   $("#submitBtn").attr("disabled","disabled");
   $("#banner_submit_wait").show(200);
   var data_url = {};

    if ($("select#id_set").val() != '0')
    {
        data_url['set'] = $("select#id_set").val();
    }

    if ($("select#id_metadataprefix").val() != '0')
    {
        data_url['metadataPrefix'] = $("select#id_metadataprefix").val();
    }

    if ($("#id_identifiers").val() != '')
    {
        data_url['identifier'] = $("#id_identifiers").val();
    }

    if ($("#id_resumptionToken").val() != '')
    {
        data_url['resumptionToken'] = $("#id_resumptionToken").val();
    }

    if ($("#id_From").val() != '')
    {
        data_url['from'] = $("#id_From").val();
    }

    if ($("#id_until").val() != '')
    {
        data_url['until'] = $("#id_until").val();
    }

    var callURL = '';
    if ($("select#id_dataProvider").val() != '0')
    {
        callURL = $("select#id_dataProvider").val().split('|')[1];
    }
    switch($("select#id_verb").val())
    {
       case '1': data_url['verb'] = 'Identify'; break;
       case '2': data_url['verb'] = 'GetRecord'; break;
       case '3': data_url['verb'] = 'ListRecords'; break;
       case '4': data_url['verb'] = 'ListSets'; break;
       case '5': data_url['verb'] = 'ListIdentifiers'; break;
       case '6': data_url['verb'] = 'ListMetadataFormats'; break;
    }

   $.ajax({
            url : 'getdata/',
            type : "POST",
            dataType: "json",
            data : {
                url : callURL,
                args_url : JSON.stringify(data_url),
            },
            success: function(data){
                $("#banner_submit_wait").hide(200);
                $("#result").html(data.message);
                $("#downloadXML").show(100);
            },
            complete: function(data){
                $("#submitBtn").removeAttr("disabled");
                $("#banner_submit_wait").hide(200);
            },
            error:function(data){
                $("#banner_submit_wait").hide(200);
                $("#banner_build_errors").show(200);
                $("#build_errors").html(data.responseText);
            }
        });
}

populateSelect = function() {
    if ($("select#id_dataProvider").val() == '0')
    {
         $("select#id_set").html("<option>"+emptyEntry+'</option>');
         $("select#id_set").attr('disabled', true);
         $("select#id_metadataprefix").html('<option>'+emptyEntry+'</option>');
         $("select#id_metadataprefix").attr('disabled', true);
    }
    else
    {
        var id = $("select#id_dataProvider").val().split('|')[0];
        $.ajax({
            url : 'registry/' + id + '/all_sets/',
            type : "POST",
            dataType: "json",
            success: function(data){
                var options = '<option value="0">'+emptyEntry+'</option>';
                 for (var i = 0; i < data.length; i++) {
                    options += '<option value="' + data[i]['value'] + '">' + data[i]['key'] + '</option>';
                 }
                 $("select#id_set").attr('disabled', false);
                 $("select#id_set").html(options);
                 $("select#id_set option:first").attr('selected', 'selected');
            },
        });

        $.ajax({
            url : 'registry/' + id + '/all_metadataprefix/',
            type : "POST",
            dataType: "json",
            success: function(data){
                var options = '<option value="0">'+emptyEntry+'</option>';
                 for (var i = 0; i < data.length; i++) {
                    options += '<option value="' + data[i] + '">' + data[i] + '</option>';
                 }
                 $("select#id_metadataprefix").attr('disabled', false);
                 $("select#id_metadataprefix").html(options);
                 $("select#id_metadataprefix option:first").attr('selected', 'selected');
            },
        });
    }
}

/**
 * AJAX call, get XML data and redirects to download view
 */
downloadXmlBuildReq = function(){
    $.ajax({
        url : "download-xml-build-req",
        type : "POST",
        dataType: "json",
        success : function(data) {
            window.location = "download-xml-build-req?id="+ data.xml2downloadID
        },
        error : function(data) {
            $("#banner_build_errors").show(200);
            $("#build_errors").html(data.responseText);
        }
    });
}


////////////////////////////////////////////////
////////////////////////////////////////////////
////////////////////////////////////////////////


////////////////////////////////////////////////
////////// My server's Information /////////////
////////////////////////////////////////////////

/**
 * Clear edit errors banner
 */
clearMyEditError = function ()
{
    $("#banner_edit_my_errors").hide()
    $("#form_edit_errors").html("");
}

editMyRegistry = function()
{
 clearMyEditError();
 exist = load_edit_my_registry_form();
 $(function() {
    $( "#dialog-edit-my-registry" ).dialog({
      modal: true,
      width: 550,
      height: 'auto',
      buttons:
    	  [
    	  {
               text: "Cancel",
               click: function() {
                        $( this ).dialog( "close" );
                    }
           },
           {
               text: "Edit",
               click: function() {
                    clearMyEditError();
                    if(validateEditMyRegistry())
                    {
                       $("#banner_add_wait").show(200);
                       var formData = new FormData($( "#form_edit_my_registry" )[0]);
	            	   $.ajax({
	            	        url: "update/my-registry",
	            	        type: 'POST',
	            	        data: formData,
	            	        cache: false,
	            	        contentType: false,
	            	        processData: false,
	            	        async:true,
	            	   		success: function(data){
                                window.location = 'oai-pmh-my-infos'
	            	        },
	            	        error:function(data){
	            	        	$("#form_edit_errors").html(data.responseText);
                                $("#banner_edit_my_errors").show(200)
	            	        },
	            	    })
	            	    ;
                    }
               }
           }
          ]
    });
  });
}

/**
* Load edit form for my registry
*/
checkSubmit
load_edit_my_registry_form = function(registryId){
	$.ajax({
        url : "update/my-registry",
        type : "GET",
        dataType: "json",
        data : {
        },
        success: function(data){
            $("#form_edit_errors").html("");
            $("#form_edit_current").html(data.template);
            Reinit();
        }
    });
}

/**
* Validate edit form entries
*/
validateEditMyRegistry = function()
{
    errors = ""
    if ($( "#id_name" ).val().trim() == ""){
        errors += "<li>Please enter a name.</li>"
    }
	if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_edit_errors").html(errors);
		$("#banner_edit_my_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}

/**
* Clear add my metadata format form
*/
clearAddMF = function ()
{
    clearAddMFError();
    $( "#form_add_MF" )[0].reset();
}

/**
* Clear add my metadata format error banner
*/
clearAddMFError = function ()
{
    $("#banner_add_MF_errors").hide()
    $("#form_add_MF_errors").html("");
}

/**
* Validate add my metadata format form
*/
validateMetadataFormat = function()
{
    errors = ""

    if ($( "#form_add_MF #id_metadataPrefix" ).val().trim() == ""){
        errors += "<li>Please enter a Metadata Prefix.</li>"
    }

    if ($( "#form_add_MF #id_schema" ).val().trim() == ""){
        errors += "<li>Please enter a schema.</li>"
    }

	if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_add_MF_errors").html(errors);
		$("#banner_add_MF_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}

/**
* Disaply add my metadata format form
*/
displayAddMetadataFormat = function()
{
 $(function() {
    clearAddMF();
//    $('#duration').durationPicker();

    $( "#dialog-add-metadataformat" ).dialog({
      modal: true,
      width: 550,
      height: 'auto',
      buttons:
      [
      {
           text: "Cancel",
           click: function() {
                    $( this ).dialog( "close" );
                }
       },
       {
           text: "Add",
           click: function() {
                clearAddMFError();
                if(validateMetadataFormat())
                {
//                       $("#banner_add_wait").show(200);
                   var formData = new FormData($( "#form_add_MF" )[0]);
                   $.ajax({
                        url: "add/my-metadataFormat",
                        type: 'POST',
                        data: formData,
                        cache: false,
                        contentType: false,
                        processData: false,
                        async:true,
                        success: function(data){
                            window.location = 'oai-pmh-my-infos'
                        },
                        error:function(data){
//	            	            $("#banner_add_wait").hide(200);
                            $("#form_add_MF_errors").html(data.responseText);
                            $("#banner_add_MF_errors").show(200)
                        },
                    })
                    ;
                }
           }
       }
      ]
    });
  });
}

/**
* Display add template metadata format form
*/
displayAddTemplateMetadataFormat = function()
{
 $(function() {
    clearAddTemplateMF();
    $( "#dialog-add-template-metadataformat" ).dialog({
      modal: true,
      width: 550,
      height: 'auto',
      buttons:
      [
      {
           text: "Cancel",
           click: function() {
                $( this ).dialog( "close" );
            }
       },
       {
           text: "Add",
           click: function() {
                clearAddTemplateMFError();
                if(validateTemplateMetadataFormat())
                {
//                       $("#banner_add_wait").show(200);
                   var formData = new FormData($( "#form_add_template_MF" )[0]);
                   $.ajax({
                        url: "add/my-template-metadataFormat",
                        type: 'POST',
                        data: formData,
                        cache: false,
                        contentType: false,
                        processData: false,
                        async:true,
                        success: function(data){
                            window.location = 'oai-pmh-my-infos'
                        },
                        error:function(data){
//	            	            $("#banner_add_wait").hide(200);
                            $("#form_add_template_MF_errors").html(data.responseText);
                            $("#banner_add_template_MF_errors").show(200)
                        },
                    })
                    ;
                }
           }
       }
      ]
    });
  });
}

/**
* Clear add my template metadata format form
*/
clearAddTemplateMF = function ()
{
    clearAddMFError();
    $( "#form_add_template_MF" )[0].reset();
}

/**
* Clear add my template metadata format error banner
*/
clearAddTemplateMFError = function ()
{
    $("#banner_add_template_MF_errors").hide()
    $("#form_add_template_MF_errors").html("");
}

/**
* Validate add template my metadata format form
*/
validateTemplateMetadataFormat = function()
{
    errors = ""

    if ($( "#form_add_template_MF #id_metadataPrefix" ).val().trim() == ""){
        errors += "<li>Please enter a Metadata Prefix.</li>"
    }

    if ($( "#form_add_template_MF  #id_template" ).val().trim() == ""){
        errors += "<li>Please choose a template.</li>"
    }

	if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_add_template_MF_errors").html(errors);
		$("#banner_add_template_MF_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}

/**
* Delete my metadata format form
*/
deleteMetadataFormat = function(metadataformat_id)
{
 $(function() {
    $( "#dialog-mf-confirm-delete" ).dialog({
      modal: true,
      buttons:{
                Cancel: function() {
	                $( this ).dialog( "close" );
                },
            	Delete: function() {
            		delete_metadata_format(metadataformat_id);
                },

		    }
    });
  });
}

/**
 * AJAX call, deletes one of my Metadata format
 * @param registry_id id of the registry
 */
delete_metadata_format = function(metadataformat_id){
    $("#banner_mf_delete_wait").show(200);
    $.ajax({
        url : 'delete/my-metadataFormat',
        type : "POST",
        dataType: "json",
        data : {
        	MetadataFormatId : metadataformat_id,
        },
        success: function(data){
            window.location = 'oai-pmh-my-infos'
        },
        error:function(data){
            $("#banner_mf_delete_wait").hide(200);
            $("#form_mf_delete_errors").html(data.responseText);
            $("#banner_mf_delete_errors").show(200);
	    }
    });
}


/**
* Clear edit my metadata format form
*/
clearMFEditError = function ()
{
    $("#banner_edit_mf_errors").hide()
    $("#form_edit_mf_errors").html("");
}

/**
* Validate edit my metadata format form
*/
validateMetadataFormatEdit = function()
{
    errors = ""
    if ($( "#form_edit_mf_current #id_metadataPrefix" ).val().trim() == ""){
        errors += "<li>Please enter a Metadata Prefix.</li>"
    }
	if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_edit_mf_errors").html(errors);
		$("#banner_edit_mf_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}


/**
 * Show a dialog when a result is selected
 */
editMetadataFormat = function(metadataFormatId)
{
    clearMFEditError()
    exist = load_mf_edit_form(metadataFormatId);
    $(function() {
        $( "#dialog-mf-edit" ).dialog({
          modal: true,
          width: 400,
          height: 'auto',
          buttons:
              [
               {
                   text: "Cancel",
                   click: function() {
                            $( this ).dialog( "close" );
                        }
               },
               {
                   text: "Edit",
                   click: function() {
                        clearMFEditError();
                        if(validateMetadataFormatEdit())
                        {
                            var formData = new FormData($( "#form_edit_mf" )[0]);
                            $.ajax({
                                url: "update/my-metadataFormat",
                                type: 'POST',
                                data: formData,
                                cache: false,
                                contentType: false,
                                processData: false,
                                async:false,
                                success: function(data){
                                    window.location = 'oai-pmh-my-infos'
                                },
                                error:function(data){
                                    $("#form_edit_mf_errors").html(data.responseText);
                                    $("#banner_edit_mf_errors").show(200)
                                },
                            })
                            ;
                        }
                   }
               }
              ]
        });
    });
}


/**
* Load edit my metadata format form
*/
load_mf_edit_form = function(metadataFormatId){
	$.ajax({
        url : "update/my-metadataFormat",
        type : "GET",
        dataType: "json",
        data : {
            metadata_format_id : metadataFormatId,
        },
        success: function(data){
            $("#form_edit_mf_errors").html("");
            $("#form_edit_mf_current").html(data.template);
            enterKeyPressSubscription();
        }
    });
}



//////////////////////////// SETS

/**
* Clear add my set form
*/
clearAddSet = function ()
{
    clearAddMFError();
    $( "#form_add_set" )[0].reset();
}

/**
* Clear add my set error banner
*/
clearAddSetError = function ()
{
    $("#banner_add_set_errors").hide()
    $("#form_add_set_errors").html("");
}

/**
* Validate add my set form
*/
validateSet = function()
{
    errors = ""

    if ($( "#id_setSpec" ).val().trim() == ""){
        errors += "<li>Please enter a set spec.</li>"
    }

    if ($( "#id_setName" ).val().trim() == ""){
        errors += "<li>Please enter a set name.</li>"
    }

	if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_add_set_errors").html(errors);
		$("#banner_add_set_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}

/**
* Display add my set form
*/
displayAddSet = function()
{
 $(function() {
    clearAddSet();
    $( "#dialog-add-set" ).dialog({
      modal: true,
      width: 720,
      height: 560,
      buttons:
      [
      {
           text: "Cancel",
           click: function() {
                    $( this ).dialog( "close" );
                }
       },
       {
           text: "Add",
           click: function() {
                clearAddSetError();
                if(validateSet())
                {
                   $("#banner_add_set_wait").show(200);
                   var formData = new FormData($( "#form_add_set" )[0]);
                   $.ajax({
                        url: "add/my-set",
                        type: 'POST',
                        data: formData,
                        cache: false,
                        contentType: false,
                        processData: false,
                        async:true,
                        success: function(data){
                            window.location = 'oai-pmh-my-infos'
                        },
                        error:function(data){
                            $("#banner_add_set_wait").hide(200);
                            $("#form_add_set_errors").html(data.responseText);
                            $("#banner_add_set_errors").show(200)
                        },
                    })
                    ;
                }
           }
       }
      ]
    });
  });
}

/**
* Delete one of my set
*/
deleteSet = function(set_id)
{
 $(function() {
    $( "#dialog-set-confirm-delete" ).dialog({
      modal: true,
      buttons:{
                Cancel: function() {
	                $( this ).dialog( "close" );
                },
            	Delete: function() {
            		delete_set(set_id);
                },

		    }
    });
  });
}

/**
 * AJAX call, deletes one of my set
 * @param set_id id of the set
 */
delete_set = function(set_id){
    $("#banner_set_delete_wait").show(200);
    $.ajax({
        url : 'delete/my-set',
        type : "POST",
        dataType: "json",
        data : {
        	set_id : set_id,
        },
        success: function(data){
            window.location = 'oai-pmh-my-infos'
        },
        error:function(data){
            $("#banner_set_delete_wait").hide(200);
            $("#form_set_delete_errors").html(data.responseText);
            $("#banner_set_delete_errors").show(200);
	    }
    });
}

/**
* Clear edit my set error banner
*/
clearSetEditError = function ()
{
    $("#banner_edit_set_errors").hide()
    $("#form_edit_set_errors").html("");
}

/**
* Validate edit my set form
*/
validateSetEdit = function()
{
    errors = ""
    if ($( "#form_edit_set_current #id_setSpec" ).val().trim() == ""){
        errors += "<li>Please enter a set spec.</li>"
    }
    if ($( "#form_edit_set_current #id_setName" ).val().trim() == ""){
        errors += "<li>Please enter a set name.</li>"
    }

	if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_edit_set_errors").html(errors);
		$("#banner_edit_set_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}


/**
 * Show a dialog when a result is selected
 */
editSet = function(setId)
{
    clearSetEditError();
    exist = load_set_edit_form(setId);
    $(function() {
        $( "#dialog-set-edit" ).dialog({
          modal: true,
          width: 720,
          height: 560,
          buttons:
              [
               {
                   text: "Cancel",
                   click: function() {
                            $( this ).dialog( "close" );
                        }
               },
               {
                   text: "Edit",
                   click: function() {
                        clearSetEditError();
                        $("#banner_edit_set_wait").show(200);
                        if(validateSetEdit())
                        {
                            var formData = new FormData($( "#form_edit_set" )[0]);
                            $.ajax({
                                url: "update/my-set",
                                type: 'POST',
                                data: formData,
                                cache: false,
                                contentType: false,
                                processData: false,
                                async:false,
                                success: function(data){
                                    window.location = 'oai-pmh-my-infos'
                                },
                                error:function(data){
                                    $("#banner_edit_set_wait").hide(200);
                                    $("#form_edit_set_errors").html(data.responseText);
                                    $("#banner_edit_set_errors").show(200)
                                },
                            })
                            ;
                        }
                   }
               }
              ]
        });
    });
}

/**
* Load edit my set form
*/
load_set_edit_form = function(setId){
	$.ajax({
        url : "update/my-set",
        type : "GET",
        dataType: "json",
        data : {
            set_id : setId,
        },
        success: function(data){
            $("#form_edit_set_errors").html("");
            $("#form_edit_set_current").html(data.template);
            InitSelectMultipleTemplates("#form_edit_set_current #id_templates");
        }
    });
}


//////////////////////HARVEST

/**
* Validate registry-edit-harvest my set form
*/
validateRegistryEditHarvest = function()
{
    errors = ""

    harvest = $( "#form_edit_harvest_current #id_harvestrate" ).val();
    if (harvest.trim() == ''){
        errors += "<li>Please enter an  harvest rate.</li>"
    }

    if (errors != ""){
	    error = "<ul>";
	    error += errors
	    error += "</ul>";
		$("#form_edit_harvest_errors").html(errors);
		$("#banner_edit_harvest_errors").show(200)
		return (false);
	}else{
		return (true)
	}
    return true;
}


/**
 * Show a dialog to edit harvest registry configuration
 * @param registry_id Registry ID
 */
editHarvestRegistry = function(registry_id)
{
    $("#form_edit_harvest_current").html("");
    exist = load_edit_harvest_form(registry_id);
    $(function() {
        $( "#dialog-edit-harvest" ).dialog({
          modal: true,
          width: 700,
          height: 600,
          buttons:
              [
                {
                   text: "Cancel",
                   click: function() {
                            $( this ).dialog( "close" );
                    }
                },
                {
                   text: "Edit",
                   click: function() {
                        clearEditError();
//                      if(validateRegistryEdit())
                        if(true)
                        {
                            var formData = new FormData($( "#form_edit_harvest" )[0]);
                            $.ajax({
                                url: "update/registry-harvest",
                                type: 'POST',
                                data: formData,
                                cache: false,
                                contentType: false,
                                processData: false,
                                async:false,
                                success: function(data){
                                    window.location = 'oai-pmh'
                                },
                                error:function(data){
                                    $("#form_edit_harvest_errors").html(data.responseText);
                                    $("#banner_edit_harvest_errors").show(200)
                                },
                            })
                            ;
                        }
                   }
                }
              ]
        });
    });
}

/**
* Load edit-harvest form
*/
load_edit_harvest_form = function(registry_id){
	$.ajax({
        url : "update/registry-harvest",
        type : "GET",
        dataType: "json",
        data : {
            registry_id : registry_id,
        },
        success: function(data){
            $("#form_edit_harvest_errors").html("");
            $("#form_edit_harvest_current").html(data.template);
            HarvestButton();
        }
    });
}

/**
* Init buttonset
*/
HarvestButton = function(){
    var buttonsetElts = $("#form_edit_harvest td[id^=ButtonSet]")
    $.each(buttonsetElts, function(index, props) {
         $("#"+props.id).buttonset();
         $(props).css("visibility", "visible");
    });
    enterKeyPressSubscription();
}

////////////////////////////////////////////////
////////////////////////////////////////////////
////////////////////////////////////////////////

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
 * Avoid errors when the enter key is pressed
 */
enterKeyPressSubscription = function ()
{
    $('#id_name').keypress(function(event) {
        if(event.which == $.ui.keyCode.ENTER){
            event.preventDefault();
            event.stopPropagation();
        }
    });

    $('#id_result_name').keypress(function(event) {
        if(event.which == $.ui.keyCode.ENTER){
            event.preventDefault();
            event.stopPropagation();
        }
    });

    $('#id_name').keypress(function(event) {
        if(event.which == $.ui.keyCode.ENTER){
            event.preventDefault();
            event.stopPropagation();
        }
    });

    $('#form_edit_mf_current #id_metadataPrefix').keypress(function(event) {
        if(event.which == $.ui.keyCode.ENTER){
            event.preventDefault();
            event.stopPropagation();
        }
    });

    $('#form_edit_current #id_harvestrate').keypress(function(event) {
        if(event.which == $.ui.keyCode.ENTER){
            event.preventDefault();
            event.stopPropagation();
        }
    });

}

////////////////////////////////////////////////
////////////////   INIT    /////////////////////
////////////////////////////////////////////////

InitBuildRequest = function(){
    populateSelect();
    $("select").on('change', function() {
      $("#build_errors").html("");
      $("#banner_build_errors").hide(200);
    });
    $("input").on('change', function() {
      $("#build_errors").html("");
      $("#banner_build_errors").hide(200);
    });

    $("select#id_dataProvider").on('change', function() {
      populateSelect();
    });

    $('#id_until').datetimepicker({
        weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		forceParse: 0,
        showMeridian: 1
    });
    $('#id_From').datetimepicker({
        weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		forceParse: 0,
        showMeridian: 1
    });
}

InitOaiPmh = function(){
    var buttonsetElts = $("td[id^=ButtonSet]")
    $.each(buttonsetElts, function(index, props) {
         $("#"+props.id).buttonset();
         $(props).css("visibility", "visible");
    });
    enterKeyPressSubscription();

    //Refresh every 30 seconds
    refreshInfo(refreshTime);
}

InitOaiPmhMyInfos = function(){
    var buttonsetElts = $("td[id^=ButtonSet]")
    $.each(buttonsetElts, function(index, props) {
         $("#"+props.id).buttonset();
         $(props).css("visibility", "visible");
    });
    enterKeyPressSubscription();

    InitSelectMultipleTemplates("#id_templates");
}

InitSelectMultipleTemplates = function (path_elt)
{
    $(path_elt).fSelect({
                placeholder: 'Select templates',
                numDisplayed: 500,
                overflowText: '{n} selected',
                searchText: 'Search',
                showSearch: true
            });
}

Reinit = function(){
    var buttonsetElts = $("#form_edit_current td[id^=ButtonSet]")
    $.each(buttonsetElts, function(index, props) {
         $("#"+props.id).buttonset();
         $(props).css("visibility", "visible");
    });
    enterKeyPressSubscription();
}
