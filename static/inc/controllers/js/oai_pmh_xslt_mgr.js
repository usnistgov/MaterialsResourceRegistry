/**
 * Clear DP add error banner
 */
clearError = function ()
{
    $("#banner_oai_pmh_errors").hide()
    $("#form_oai_pmh_start_errors").html("");
}

displayOaiImport = function()
{
 clearError();
 $(function() {
    $("#form_oai_pmh_start_errors").html("");
    $( "#dialog-oai-pmh-message" ).dialog({
      modal: true,
      width: 500,
      buttons:
    	  [
           {
               text: "Upload",
               click: function() {
                    if(validateOaiExport())
                    {
                       var formData = new FormData($( "#form_oai_pmh_start" )[0]);
	            	   $.ajax({
	            	        url: "/oai_pmh/admin/manage-xslt",
	            	        type: 'POST',
	            	        data: formData,
	            	        cache: false,
	            	        contentType: false,
	            	        processData: false,
	            	        async:false,
	            	   		success: function(data){
                                window.location = '/admin/xml-schemas/manage-xslt'
	            	        },
	            	        error:function(data){
	            	            $("#banner_oai_pmh_errors").show(200);
	            	        	$("#form_oai_pmh_start_errors").html(data.responseText);
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


validateOaiExport = function()
{
    clearError();
    errors = ""
    if ($( "#id_oai_name" ).val().trim() == ""){
        errors = "Please enter a name."
    }
	// check if an option has been selected
    else if ($( "#id_oai_pmh_xslt_file" ).val() == ""){
        errors = "Please select an XSLT file."
    }

	if (errors != ""){
	    $("#banner_oai_pmh_errors").show(200);
		$("#form_oai_pmh_start_errors").html(errors);
		return (false);
	}else{
		return (true)
	}
}



deleteOaiXSLT = function(xslt_id)
{
 $(function() {
    $( "#dialog-deletexslt-message" ).dialog({
      modal: true,
      buttons:{
                Cancel: function() {
	                $( this ).dialog( "close" );
                },
            	Delete: function() {
            		delete_OAI_XSLT(xslt_id);
            		$( this ).dialog( "close" );
                },
		    }
    });
  });
}

/**
 * AJAX call, deletes an XSLT File
 * @param bucket_id id of the bucket
 */
delete_OAI_XSLT = function(elt){
    var xslt_id = $(elt).attr("objectid");
    var typeXSLT = $(elt).attr("typeXSLT");

    var urlDelete = "/oai_pmh/admin/delete-xslt"
    $.ajax({
        url : urlDelete,
        type : "POST",
        dataType: "json",
        data : {
        	xslt_id : xslt_id,
        },
        success: function(data){
            window.location = '/admin/xml-schemas/manage-xslt'
        },
        error:function(data){
            $("#form_start_errors").html(data.responseText);
            $( "#form_start_errors").dialog({
                modal: true,
                buttons: {
                Ok: function() {
                    $( this ).dialog( "close" );
                  },
                }
            });
	    }
    });
}


/**
 * Clear DP edit error banner
 */
clearEditError = function ()
{
    $("#banner_oai_pmh_edit_errors").hide()
    $("#form_oai_pmh_edit_errors").html("");
}

/**
 * Edit general information of a template or a type
 */
editOaiInformation = function(objectID)
{
    clearEditError();
    var objectName = $(this).parent().siblings(':first').text();
    var objectID = $(this).attr("objectid");
    var typeXSLT = $(this).attr("typeXSLT");
    $("#form_oai_pmh_edit_errors").html("");
    $("#edit-oai_pmh_name")[0].value = objectName;

	$(function() {
        $( "#dialog-oai-pmh-edit-message" ).dialog({
            modal: true,
            width: 500,
            buttons: {
                Cancel: function() {
                    $( this ).dialog( "close" );
                },
            	Ok: function() {
            	    clearEditError();
					var newName = $("#edit-oai_pmh_name")[0].value;
					if (newName == ""){
					    $("#banner_oai_pmh_edit_errors").show(200)
                        $("#form_oai_pmh_edit_errors").html("Please enter a name.");
                    }
                    else
                    {
					    edit_oai_information(objectID, newName, typeXSLT);
					}
                },
            }
        });
    });
}


/**
 * AJAX call, edit information of an object
 * @param objectID id of the object
 * @param newName new name of the object
 */
edit_oai_information = function(objectID, newName, typeXSLT){
    clearEditError();
    var urlEdit = "/oai_pmh/admin/edit-xslt"
    $.ajax({
        url : urlEdit,
        type : "POST",
        dataType: "json",
        data : {
        	object_id : objectID,
        	new_name : newName,
        },
        success: function(data){
            window.location = '/admin/xml-schemas/manage-xslt'
        },
        error:function(data){
            $("#banner_oai_pmh_edit_errors").show(200)
            $("#form_oai_pmh_edit_errors").html(data.responseText);
        }
    });
}



enterKeyPressSubscriptionOAI = function ()
{
    $('#id_oai_pmh_name').keypress(function(event) {
        if(event.which == $.ui.keyCode.ENTER){
            event.preventDefault();
            event.stopPropagation();
        }
    });
}


InitOai = function(){
    $('.editOaiPmh').on('click', editOaiInformation);
    enterKeyPressSubscriptionOAI();
}

InitConfXSLT = function() {
    var buttonsetElts = $("td[id^=ButtonSet]")
    $.each(buttonsetElts, function(index, props) {
         $("#"+props.id).buttonset();
         $(props).css("visibility", "visible");
    });
}

saveMyTemplate = function ()
{
   $("#form_start_errors").html('');
   $("#banner_errors").hide(200)
   var formData = new FormData($( "#form_start" )[0]);
   $.ajax({
        url: "oai-pmh-conf-xslt",
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        async:false,
        success: function(data){
            saveTemplateCallback();
        },
        error:function(data){
            $("#banner_errors").show(200)
            $("#form_start_errors").html(data.responseText);
        },
    })
    ;
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
