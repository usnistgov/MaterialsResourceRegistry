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
    $('.version').on('click', manageVersions);
    $('.modules').on('click', manageModules);
    $('.exporters').on('click', manageExporters);
    $('.resultXslt').on('click', manageResultXslt);
    $('.delete').on('click', deleteObject);
    $('.upload').on('click', uploadObject);
    $('.buckets').on('click', manageBuckets);
    console.log('END [loadUploadManagerHandler]');
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
    
    window.location = "/admin/modules?id=" + objectID 
}

/**
 * Open a window for the version management
 */
manageVersions = function()
{
    var modelName = $(this).parent().siblings(':first').text();
    var modelFilename = $(this).parent().siblings(':nth-child(2)').text();
    var tdElement = $(this).parent();
    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objectType");
    
   
	versionDialog = $('<div title="Manage Versions" id="dialog-manage-versions">'+
			'<iframe id="version-upload-frame" style="width:500px;height:auto; min-height:400px;" src="/admin/manage-versions?id='+ objectID +'&type='+ objectType +'">'+
			'</iframe>'+	
	  '</div>' ).dialog({
        modal: true,
        width:520,
        height:510,
        resizable:false,
        close: function(event, ui){
        	$(this).dialog('destroy').remove();
        	$('#model_selection').load(window.parent.document.URL +  ' #model_selection', function() {
        	      loadUploadManagerHandler();
        	});  
        },
        buttons: {
        	OK: function() {
        		$(this).dialog('close');
                $('#model_selection').load(document.URL +  ' #model_selection', function() {
                    loadUploadManagerHandler();
                }); 
            },
            Cancel: function() {
            	$(this).dialog('close');
                $('#model_selection').load(document.URL +  ' #model_selection', function() {
                    loadUploadManagerHandler();
                }); 
            }
    }
    });   
}


/**
 * Handler for the reading of version of a template
 * @param evt
 */
function handleSchemaVersionUpload(evt) {
	var files = evt.target.files; // FileList object
    reader = new FileReader();
    reader.onload = function(e){
    	versionContent = reader.result;
    	versionFilename = files[0].name;
    	set_schema_version_content(versionContent, versionFilename);
    }
    reader.readAsText(files[0]);
}


/**
 * AJAX call, send content of the file
 * @param versionContent content of the file
 * @param versionFilename name of the file
 */
set_schema_version_content = function(versionContent, versionFilename){
    $.ajax({
        url : "/admin/set_schema_version_content",
        type : "POST",
        dataType: "json",
        data : {
        	versionContent : versionContent,
        	versionFilename : versionFilename,
        },
        success: function(data){
            
        }
    });
}


/**
 * Handler for the reading of version of a type
 * @param evt
 */
function handleTypeVersionUpload(evt) {
	var files = evt.target.files; // FileList object
    reader = new FileReader();
    reader.onload = function(e){
    	versionContent = reader.result;
    	versionFilename = files[0].name;
    	set_type_version_content(versionContent, versionFilename);
    }
    reader.readAsText(files[0]);
}


/**
 * AJAX call, send content of the file
 * @param versionContent content of the file
 * @param versionFilename name of the file
 */
set_type_version_content = function(versionContent, versionFilename){
    $.ajax({
        url : "/admin/set_type_version_content",
        type : "POST",
        dataType: "json",
        data : {
        	versionContent : versionContent,
        	versionFilename : versionFilename,
        },
        success: function(data){
            
        }
    });
}


/**
 * Upload a version
 */
uploadVersion = function()
{
	var objectVersionID = $("#updateVersionBtn").attr("versionid");
	var objectType = $("#updateVersionBtn").attr("objectType");	
	
	upload_version(objectVersionID, objectType);
}



/**
 * AJAX call, uploads a version
 * @param objectVersionID id of the version manager
 * @param objectType type of the version file
 */
upload_version = function(objectVersionID, objectType){
    $.ajax({
        url : "/admin/upload_version",
        type : "POST",
        dataType: "json",
        data : {
        	objectVersionID : objectVersionID,
        	objectType : objectType,
        },
        success: function(data){
            if ('errors' in data){
            	if ("message" in data){
        			$("#objectUploadErrorMessage").html("<font color='red'>" + data.errors + "</font><br/>" + data.message);
        		}else{
        			$("#objectUploadErrorMessage").html("<font color='red'>" + data.errors + "</font><br/>");
        		} 
            }else{
            	$("#objectUploadErrorMessage").html("<font color='green'>The uploaded template is valid. You can now save it.</font>   <span class='btn' onclick='saveVersion()'>Save</span>");
            }
        }
    });
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
                window.parent.versionDialog.dialog("close");  
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
 * Upload a template or a type
 */
uploadObject = function()
{
    console.log('BEGIN [uploadObject]');

    document.getElementById('object_name').value = ""
    document.getElementById('files').value = ""
    document.getElementById('list').innerHTML = ""
    document.getElementById('objectUploadErrorMessage').innerHTML = ""

    $(function() {
        $( "#dialog-upload-message" ).dialog({
            modal: true,
            width: 500,
            open: function(event, ui){
            	clear_object();
            },
            close: function(event, ui){
            	clear_object();
            },
            buttons: {
				Cancel: function() {
		                    $( this ).dialog( "close" );
		                }
			    }
        	});
    	});
	
    console.log('END [uploadObject]');
}


/**
 * AJAX call, clears objects in session
 */
clear_object = function(){
    $.ajax({
        url : "/admin/clear_object",
        type : "GET",
        dataType: "json",
        success: function(data){
           
        }
    });
}


/**
 * Save a template or a type
 */
saveObject = function() 
{
	console.log('BEGIN [saveObject]');
	
	var buckets = [];
	$("#select_buckets option:selected").each(function(){
		buckets.push($(this).attr('bucketid'));
	});
	
	save_object(buckets);
	console.log('END [saveObject]');
}

/**
 * AJAX call, save an object
 * @param buckets
 */
save_object = function(buckets){
    $.ajax({
        url : "/admin/save_object",
        type : "POST",
        dataType: "json",
        data : {
        	buckets : buckets,
        },
        success: function(data){
        	if('errors' in data){
        		$("#objectUploadErrorMessage").html("<font color='red'>Please upload a valid XML schema.</font>");
        	} else {
                $( "#dialog-upload-message" ).dialog("close");
                location.reload();
        	}
        }
    });
}

/**
 * Save a version of a template or a type
 */
saveVersion = function() 
{
	console.log('BEGIN [saveVersion]');
	save_version();
	console.log('END [saveVersion]');
}


/**
 * AJAX call, saves a version
 */
save_version = function(){
    $.ajax({
        url : "/admin/save_version",
        type : "GET",
        dataType: "json",
        success: function(data){
        	if('errors' in data){
        		$("#objectUploadErrorMessage").html("<font color='red'>Please upload a valid XML schema first.</font>");
        	}else{
                $("#delete_custom_message").html("");
                $('#model_version').load(document.URL +  ' #model_version', function() {}); 
        	}        	
        }
    });
}


/**
 * Resolve dependencies
 */
resolveDependencies = function()
{
	var dependencies = [];
	
	$("#dependencies").find(".dependency").each(function(){
		dependencies.push($($(this)[0].options[$(this)[0].selectedIndex]).attr('objectid'));
	});    	
	resolve_dependencies(dependencies);
}


/**
 * AJAX call, resolves dependencies
 * @param dependencies
 */
resolve_dependencies = function(dependencies){
    $.ajax({
        url : "/admin/resolve_dependencies",
        type : "POST",
        dataType: "json",
        data : {
        	dependencies : dependencies,
        },
        success: function(data){
            if ("errors" in data){
            	$("#objectUploadErrorMessage").html("<font color='red'>" + data.errors + "</font>");
            }else if ("errorDependencies" in data){
            	$("#errorDependencies").html("<font color='red'>Not a valid XML schema.</font><br/>" + data.errorDependencies);
            }else{
            	$("#objectUploadErrorMessage").html("<font color='green'>" + data.message + "</font>");
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
 * AJAX call, check the name of the template
 * @param name name of the object
 */
check_name = function(name){
    success = false;
    $.ajax({
        url : "/admin/check_name",
        type : "POST",
        dataType: "json",
        async: false,
        data : {
        	name : name,
        },
        success: function(data){
            if ("errors" in data){
                success = false;
            } else {
                success = true;
            }
        }
    });

    return success;
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


/**
 * AJAX call, uploads an object
 * @param objectName name of the object
 * @param objectFilename name of the file
 * @param objectContent content of the file
 * @param objectType type of object
 */
upload_object = function(objectName, objectFilename, objectContent, objectType){
    $.ajax({
        url : "/admin/upload_object",
        type : "POST",
        dataType: "json",
        data : {
        	objectName : objectName,
        	objectFilename : objectFilename,
        	objectContent : objectContent,
        	objectType : objectType,
        },
        success: function(data){
        	if ("errors" in data){
        		if ("message" in data){
        			$("#objectUploadErrorMessage").html("<font color='red'>" + data.errors + "</font><br/>" + data.message);
        		}else{
        			$("#objectUploadErrorMessage").html("<font color='red'>" + data.errors + "</font><br/>");
        		}        		
        	}else{
        		$("#objectUploadErrorMessage").html("<font color='green'>The uploaded template is valid. You can now save it.</font>   <span class='btn' onclick='saveObject()'>Save</span>");
        	}
        }
    });
}
