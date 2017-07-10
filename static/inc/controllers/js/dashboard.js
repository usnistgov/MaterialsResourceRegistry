/**
 *
 * File Name: dashboard.js
 * Author: Sharief Youssef
 * 		   sharief.youssef@nist.gov
 *
 *		   Xavier SCHMITT
 *		   xavier.schmitt@nist.gov
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
    $('.edit').on('click',editInformation);
    $('.delete').on('click', deleteObject);
    console.log('END [loadUploadManagerHandler]');
}


/**
 *
 */
initNmrr = function (roles_list) {
    var btns = $("#my_role").children("input");
    for(var i = 0; i < btns.length; i++) {
        // when value change
        btns[i].onclick = function () {
            var selected_val = $(this).val();
            var td = $("#td_"+selected_val);
            if ($(this).prop('checked') == true) {
                td.addClass("selected_resource");
            } else {
                td.removeClass("selected_resource");
            }
        };
    }
    roles_list = roles_list.split(',');
    for (var i = 0 ; i<roles_list.length; i++) {
        click_role(roles_list[i]);
    }
}

/**
 * Check if all the images are selected
 * @returns {boolean}
 */
is_all_td_selected = function() {
    return $("#Organization").prop('checked') == true
        && $("#Dataset").prop('checked') == true
        && $("#DataCollection").prop('checked') == true
        && $("#ServiceAPI").prop('checked') == true
        && $("#Software").prop('checked') == true
        && $("#WebSite").prop('checked') == true ;
}

/**
 * Click for a role
 */
click_role = function(role) {
    if (role == 'all') {
        $("#my_role").find('input:checked').prop('checked', false);
        $("#td_" + role).addClass("selected_resource");
    } else {
        $("#td_all").css({'class': ''});
        $("#"+role).click();
        if (is_all_td_selected()) {
            $("#my_role").find('input:checked').prop('checked',false);
            $("#td_" + role).removeClass("selected_resource");
        }
    }
}

/**
 * Update URL
 */
get_url = function(ispublished) {
    var url = "/dashboard/resources";
    var published = '';
    var list_role = '';
    var i = 0;
    $('input:checked[name=my_role]').each(function() {
        if (i > 0) {
            list_role += '&';
        }
        list_role += 'role='+$(this).val();
        i++;
    });

    if (ispublished == 'True') {
        published = 'ispublished=true';
    } else if (ispublished == 'False') {
        published = 'ispublished=false';
    }
    if (list_role != '') {
        url += '?'+list_role;
        if (published != '') {
            url += '&' + published;
        }
    } else if (published != '') {
        url += '?' + published;
    }
    window.location.href = url;
}

/**
 * Edit general information of a template or a type
 */
editInformation = function()
{
    var objectName = $(this).parent().siblings(':first').text();
    var objectFilename = $(this).parent().siblings(':nth-child(2)').text();

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
					edit_information(objectID, objectType, newName, newFilename);
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
 */
edit_information = function(objectID, objectType, newName, newFilename){
    $.ajax({
        url : "/dashboard/edit_information",
        type : "POST",
        dataType: "json",
        data : {
        	objectID : objectID,
        	objectType : objectType,
        	newName : newName,
        	newFilename : newFilename,
        },
        success: function(data){
            if ('name' in data){
            	showErrorEditType(true);
            }else if ('filename' in data){
            	showErrorEditType(false);
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
    var objectID = $(this).attr("objectid");
    var objectType = $(this).attr("objecttype");
    var objectFilename = $(this).attr("objectfilename");
    var objectName = $(this).attr("objectname");
    var url = $(this).attr("url");

    document.getElementById("object-to-delete").innerHTML = objectName;

    $(function() {
        $( "#dialog-deleteconfirm-message" ).dialog({
            modal: true,
            buttons: {
		Yes: function() {
					delete_object(objectID, objectType, url);
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
 * @param url mdcs url
 */
delete_object = function(objectID, objectType, url){
    $.ajax({
        url : "/dashboard/delete_object",
        type : "POST",
        dataType: "json",
        data : {
        	objectID : objectID,
        	objectType : objectType,
        	url : url,
        },
        success: function(data){
            if ('Type' in data) {
                var text = 'You cannot delete this Type because it is used by at least one template or type: '+data['Type'];
                showErrorDelete(text);
            } else if('Template' in data) {
                var text = 'You cannot delete this Template because it is used by at least one resource: '+data['Template'];
                showErrorDelete(text);
            } else {
                location.reload();
            }

        }
    });
}

/**
 * Display error message when you have an error while deleting
 */
showErrorDelete = function(text){
	$(function() {
	    $( "#dialog-error-delete" ).html(text);
        $( "#dialog-error-delete" ).dialog({
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
 * Display error message when bad edition of type
 */
showErrorEditType = function(name){
	$(function() {
	    if (name) {
	        $( "#dialog-error-edit" ).html('A type with this name already exists.');
	    } else {
	        $( "#dialog-error-edit" ).html('A type with this filename already exists.');
	    }
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

initBanner = function()
{
    $("[data-hide]").on("click", function(){
        $(this).closest("." + $(this).attr("data-hide")).hide(200);
    });
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
        url : "/dashboard/delete_result",
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
        url : "/dashboard/update_publish",
        type : "GET",
        dataType: "json",
        data : {
        	result_id: result_id,
        },
		success: function(data){
		    location.reload();
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
        url : "/dashboard/update_unpublish",
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
 * Change record owner
 * @param recordID
 */
changeOwnerRecord = function(recordID){
    $("#banner_errors").hide();
    $(function() {
        $( "#dialog-change-owner-record" ).dialog({
            modal: true,
            buttons: {
                Cancel: function() {
                    $( this ).dialog( "close" );
                },
                "Change": function() {
                    if (validateChangeOwner()){
                        var formData = new FormData($( "#form_start" )[0]);
                        change_owner_record(recordID);
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
 * AJAX call, change record owner
 * @param recordID
 */
change_owner_record = function(recordID){
    var userId = $( "#id_users" ).val().trim();
    $.ajax({
        url : "/dashboard/change-owner-record",
        type : "POST",
        dataType: "json",
        data : {
            recordID: recordID,
            userID: userId,
        },
		success: function(data){
			window.location = "/dashboard/resources"
	    },
        error:function(data){
            $("#form_start_errors").html(data.responseText);
            $("#banner_errors").show(500)
        }
    });
}

/**
 * Delete a form
 * @param formID
 */
deleteDraft = function(formID){
	$(function() {
        $( "#dialog-delete-draft" ).dialog({
            modal: true,
            buttons: {
                Cancel: function() {
                    $( this ).dialog( "close" );
                },
            	Delete: function() {
            	    $( "#banner_wait").show();
                    delete_draft(formID);
                },
            }
        });
    });
}


/**
 * AJAX call, delete a form
 * @param formID
 */
delete_draft = function(formID){
	$.ajax({
        url : "/curate/delete-form?id=" + formID,
        type : "GET",
        dataType: "json",
        data : {
        	formID: formID,
        },
		success: function(data){
			window.location = "/dashboard/resources"
	    },
        error:function(data){
        	window.location = "/dashboard/resources"
        }
    });
}

/**
 * Publish a draft
 * @param draft_id
 */
updatePublishDraft = function(draft_id){
	$(function() {
        $( "#dialog-publish-draft" ).dialog({
            modal: true,
            buttons: {
            	Cancel: function() {
                    $( this ).dialog( "close" );
                },
            	Publish: function() {
            	$( "#banner_wait_publish").show();
                    update_publish_draft(draft_id);
                },
            }
        });
    });
}

/**
 * AJAX call, update the publish document and date of a XMLdata
 * @param draft_id
 */
update_publish_draft = function(draft_id){
	$.ajax({
        url : "/dashboard/update_publish_draft",
        type : "GET",
        dataType: "json",
        data : {
        	draft_id: draft_id,
        },
		success: function(data){
		    location.reload();
	    }
    });
}

/**
 * AJAX call, change the status of a XMLdata
 * @param result_id
 */
change_status = function(result_id, is_published){
    var e = document.getElementById("status"+result_id);
    var value = e.options[e.selectedIndex].value;
	$.ajax({
        url : "/dashboard/change_status",
        type : "GET",
        dataType: "json",
        data : {
        	status: value,
        	result_id: result_id,
        	is_published: is_published,
        },
		success: function(data){
		    location.reload();
	    }
    });
}