/**
 * 
 * File Name: xsd_mgr.js
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
 * Load controllers for template/type upload management
 */
loadUploadManagerHandler = function()
{
    console.log('BEGIN [loadUploadManagerHandler]');
    $('.retrieve').on('click',restoreObject);
    $('.edit').on('click',editInformation);
    $('.modules').on('click', manageModules);
    $('.exporters').on('click', manageExporters);
    $('.resultXslt').on('click', manageResultXslt);
    $('.delete').on('click', deleteObject);
    $('.buckets').on('click', manageBuckets);
    $('.oaiPmh').on('click', manageOaiPmhXslt);
    console.log('END [loadUploadManagerHandler]');
}

/**
 * Redirects to OAI-PMH XSLT management page
 */
manageOaiPmhXslt = function()
{
    var modelName = $(this).parent().siblings(':first').text();
    var modelFilename = $(this).parent().siblings(':nth-child(2)').text();
    var tdElement = $(this).parent();
    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objectType");

    window.location = "/oai_pmh/admin/oai-pmh-conf-xslt?id=" + objectID
}

/**
 * Redirects to result XSLT management page
 */
manageResultXslt = function()
{
    var modelName = $(this).parent().siblings(':first').text();
    var modelFilename = $(this).parent().siblings(':nth-child(2)').text();
    var tdElement = $(this).parent();
    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objectType");

    window.location = "/admin/resultXslt?id=" + objectID
}


/**
 * Redirects to exporter management page
 */
manageExporters = function()
{
    var modelName = $(this).parent().siblings(':first').text();
    var modelFilename = $(this).parent().siblings(':nth-child(2)').text();
    var tdElement = $(this).parent();
    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objectType");

    window.location = "/admin/exporters?id=" + objectID
}

/**
 * Redirects to module management page
 */
manageModules = function()
{
    var modelName = $(this).parent().siblings(':first').text();
    var modelFilename = $(this).parent().siblings(':nth-child(2)').text();
    var tdElement = $(this).parent();
    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objectType");

    window.location = "/admin/modules?id=" + objectID  + '&type=' + objectType
}


/**
 * Set the current version to be used on the user side
 * @param setCurrent
 */
setCurrentVersion = function(setCurrent)
{
	current = document.getElementById(setCurrent);
	var objectid = $(current).attr("objectid");
	var objectType = $(current).attr("objectType");
	
	set_current_version(objectid, objectType);
}


/**
 * AJAX call, sets the current version
 * @param objectid id of the object
 * @param objectType type of the object
 */
set_current_version = function(objectid, objectType){
    $.ajax({
        url : "/admin/set_current_version",
        type : "GET",
        dataType: "json",
        data : {
        	objectid : objectid,
        	objectType : objectType,
        },
        success: function(data){
            $("#delete_custom_message").html("");   
            $('#model_version').load(document.URL +  ' #model_version', function() {});   
        }
    });
}


/**
 * Delete a version
 * @param toDelete
 */
deleteVersion = function(toDelete)
{			
	current = document.getElementById(toDelete);
	var objectid = $(current).attr("objectid");
	var objectType = $(current).attr("objectType");
	assign_delete_custom_message(objectid, objectType);
	$(function() {
			$('#dialog-deleteversion-message').dialog({
	            modal: true,
	            buttons: {
	            	Yes: function() {	
						var newCurrent = ""
						try{
							var idx = $("#selectCurrentVersion")[0].selectedIndex
							newCurrent = $("#selectCurrentVersion")[0].options[idx].value
						}
						catch(e){}
						delete_version(objectid, objectType, newCurrent);
	                    $( this ).dialog( "close" );
	                },
	                No: function() {
	                    $( this ).dialog( "close" );
	                }
		    }
	        });
	    });
}


/**
 * AJAX call, get delete message 
 * @param objectid id of the object to delete
 * @param objectType type of the object
 */
assign_delete_custom_message = function(objectid, objectType){
    $.ajax({
        url : "/admin/assign_delete_custom_message",
        type : "GET",
        dataType: "json",
        data : {
        	objectid : objectid,
        	objectType : objectType,
        },
        success: function(data){
        	$('#delete_custom_message').html(data.message);
        }
    });
}


/**
 * AJAX call, delete a version
 * @param objectid id of the object
 * @param objectType type of the object
 * @param newCurrent new object set current
 */
delete_version = function(objectid, objectType, newCurrent){
    $.ajax({
        url : "/admin/delete_version",
        type : "POST",
        dataType: "json",
        data : {
        	objectid : objectid,
        	objectType : objectType,
        	newCurrent : newCurrent,
        },
        success: function(data){
        	if(data.deleted == 'object'){
                $("#delete_custom_message").html("");
                if (objectType === "Template"){
                    window.location = '/admin/xml-schemas';
                }else if (objectType === "Type"){
                    window.location = '/admin/xml-schemas/manage-types';
                }
        	}else if(data.deleted == 'version'){
                $("#delete_custom_message").html("");   
                $('#model_version').load(document.URL +  ' #model_version', function() {}); 
        	}
        }
    });
}


/**
 * Restore a template or a type
 */
restoreObject = function()
{
    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objectType");
    
    restore_object(objectID, objectType);
}


/**
 * AJAX call, restores an object
 * @param objectID id of the object
 * @param objectType type of the object
 */
restore_object = function(objectID, objectType){
    $.ajax({
        url : "/admin/restore_object",
        type : "POST",
        dataType: "json",
        data : {
        	objectID : objectID,
        	objectType : objectType,
        },
        success: function(data){
            location.reload();
        }
    });
}


/**
 * Restore a version of a template or a type
 * @param toRestore
 */
restoreVersion = function(toRestore)
{
	current = document.getElementById(toRestore);
	var objectID = $(current).attr("objectid");
	var objectType = $(current).attr("objectType");
	
	restore_version(objectID, objectType);
}


/**
 * AJAX call, restore a version
 * @param objectID id of the object
 * @param objectType type of the object
 */
restore_version = function(objectID, objectType){
    $.ajax({
        url : "/admin/restore_version",
        type : "POST",
        dataType: "json",
        data : {
        	objectID : objectID,
        	objectType : objectType,
        },
        success: function(data){
            $("#delete_custom_message").html("");
            $('#model_version').load(document.URL +  ' #model_version', function() {}); 
        }
    });
}


/**
 * Edit general information of a template or a type
 */
editInformation = function()
{
    var objectName = $(this).parent().siblings(':first').text();
    var objectFilename = $(this).parent().siblings(':nth-child(2)').text();
    var buckets = [] 
    
    $(this).parent().siblings(':nth-child(3)').children().each(function(){
    	buckets.push($(this).attr('bucketid'));
    });
    $("#select_edit_buckets").children().each(function(){
      $(this).prop('selected',false);
	  if(buckets.indexOf($(this).attr('bucketid')) > -1 ){
	    $(this).prop('selected',true);
	  }
	})

    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objectType");
    
    $("#edit-name")[0].value = objectName;
    $("#edit-filename")[0].value = objectFilename;
    
	$(function() {
        $( "#dialog-edit-info" ).dialog({
            modal: true,
            buttons: {
            	Ok: function() {	
					var newName = $("#edit-name")[0].value;
					var newFilename = $("#edit-filename")[0].value;
					var newBuckets = [] 				    
					$("#select_edit_buckets").children().each(function(){
						if($(this).prop('selected') == true ){
							newBuckets.push($(this).attr('bucketid'))
						}
					})
					edit_information(objectID, objectType, newName, newFilename, newBuckets);
                },
                Cancel: function() {
                    $( this ).dialog( "close" );
                }
            }
        });
    });
}


/**
 * AJAX call, edit information of an object
 * @param objectID id of the object
 * @param objectType type of the object
 * @param newName new name of the object
 * @param newFilename new filename of the object
 * @param newBuckets new buckets for the object
 */
edit_information = function(objectID, objectType, newName, newFilename, newBuckets){
    $.ajax({
        url : "/admin/edit_information",
        type : "POST",
        dataType: "json",
        data : {
        	objectID : objectID,
        	objectType : objectType,
        	newName : newName,
        	newFilename : newFilename,
        	newBuckets : newBuckets,
        },
        success: function(data){
            if ('errors' in data){
            	showErrorEditType();
            }else{
                $("#dialog-edit-info").dialog( "close" );
                location.reload();
            }
        }
    });
}


/**
 * Delete a template or a type
 */
deleteObject = function()
{
    console.log('BEGIN [deleteObject]');
    var objectName = $(this).parent().siblings(':first').text();
    var objectFilename = $(this).parent().siblings(':nth-child(2)').text();
    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objectType");

    document.getElementById("object-to-delete").innerHTML = objectName;

    $(function() {
        $( "#dialog-deleteconfirm-message" ).dialog({
            modal: true,
            buttons: {
		Yes: function() {
					delete_object(objectID, objectType);
                    $( this ).dialog( "close" );
                },
		No: function() {
                    $( this ).dialog( "close" );
                }
	    }
        });
    });
	
    console.log('END [deleteObject]');
}



/**
 * AJAX call, delete an object
 * @param objectID id of the object
 * @param objectType type of the object
 */
delete_object = function(objectID, objectType){
    $.ajax({
        url : "/admin/delete_object",
        type : "POST",
        dataType: "json",
        data : {
        	objectID : objectID,
        	objectType : objectType,
        },
        success: function(data){
            location.reload();
        }
    });
}

/**
 * Resolve dependencies
 */
resolveDependencies = function()
{
    var schemaLocations = []
	var dependencies = [];

	$("#dependencies").find("tr:not(:first)").each(function(){
        schemaLocation = $(this).find(".schemaLocation").html();
        dependency = $(this).find(".dependency").val();
        schemaLocations.push(schemaLocation)
        dependencies.push(dependency);
    });

	resolve_dependencies(schemaLocations, dependencies);
}

/**
 * AJAX call, resolves dependencies
 * @param dependencies
 */
resolve_dependencies = function(schemaLocations, dependencies){
    $.ajax({
        url : "/admin/resolve_dependencies",
        type : "POST",
        dataType: "json",
        data : {
            schemaLocations: schemaLocations,
        	dependencies : dependencies,
        },
        success: function(data){
            if ("errorDependencies" in data){
            	$("#errorDependencies").html("<font color='red'>Not a valid XML schema.</font><br/>" + data.errorDependencies);
            }else{
                console.log(data.redirect);
                window.location = data.redirect
            }
        }
    });
}


/**
 * Display error message when bad edition of type
 */
showErrorEditType = function(){
	$(function() {
        $( "#dialog-error-edit" ).dialog({
            modal: true,
            buttons: {
			Ok: function() {
                $( this ).dialog( "close" );
	          },
		    }
        });
    });
}


/**
 * Display window to manage buckets
 */
manageBuckets = function(){
	$(function() {
        $( "#dialog-buckets" ).dialog({
            modal: true,
            buttons: {
			Ok: function() {
                $( this ).dialog( "close" );
	          },
		    }
        });
    });
}

/**
 * Display window to add a bucket
 */
addBucket = function(){
	$(function() {
		$('#label_bucket').val('');
        $( "#dialog-add-bucket" ).dialog({
            modal: true,
            buttons: {
            	Add: function() {
            		$("#errorAddBucket").html("");
            		var label = $('#label_bucket').val();
            		if (label == ""){
            			$("#errorAddBucket").html("<font color='red'>Please enter a name.</font><br/>");
            		}else{
            			add_bucket(label);
            		}                    
    	          },
				Cancel: function() {
	                $( this ).dialog( "close" );
		          },
		    }
        });
    });	
}


/**
 * AJAX call, adds a bucket
 * @param label label of the bucket
 */
add_bucket = function(label){
    $.ajax({
        url : "/admin/add_bucket",
        type : "POST",
        dataType: "json",
        data : {
        	label : label,
        },
        success: function(data){
            if ("errors" in data){
            	$("#errorAddBucket").html("<font color='red'>A bucket with the same label already exists.</font><br/>");
            } else if("errors" in data) {
                $("#errorsTemplateName").html("<font color='red'>The template's name is already used. Please give another name to the template.</font><br/>");
            } else {
                $('#dialog-add-bucket').dialog('close');
                $('#model_buckets').load(document.URL +  ' #model_buckets', function() {});
                $('#model_select_buckets').load(document.URL +  ' #model_select_buckets', function() {});
                $('#model_select_edit_buckets').load(document.URL +  ' #model_select_edit_buckets', function() {});
            }
        }
    });
}

/**
 * Display window to delete a bucket
 */
deleteBucket = function(bucket_id){
	$(function() {
        $( "#dialog-delete-bucket" ).dialog({
            modal: true,
            buttons: {
            	Delete: function() {
            		delete_bucket(bucket_id);
            		$( this ).dialog( "close" );
            		},
				Cancel: function() {
	                $( this ).dialog( "close" );
		          },
		    }
        });
    });	
}



/**
 * AJAX call, deletes a buckets
 * @param bucket_id id of the bucket
 */
delete_bucket = function(bucket_id){
    $.ajax({
        url : "/admin/delete_bucket",
        type : "POST",
        dataType: "json",
        data : {
        	bucket_id : bucket_id,
        },
        success: function(data){
            $('#model_buckets').load(document.URL +  ' #model_buckets', function() {});
            $('#model_select_buckets').load(document.URL +  ' #model_select_buckets', function() {});
            $('#model_selection').load(document.URL +  ' #model_selection', function() {
              loadUploadManagerHandler();
            });
            $('#model_select_edit_buckets').load(document.URL +  ' #model_select_edit_buckets', function() {});
        }
    });
}