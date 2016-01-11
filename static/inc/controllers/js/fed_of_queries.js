/**
 * 
 * File Name: fed_of_queries.js
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
 * load controllers for the federation of queries
 */
loadFedOfQueriesHandler = function()
{
	console.log('BEGIN [loadFedOfQueriesHandler]');
	$('.edit.instance').on('click',editInstance);
    $('.delete.instance').on('click', deleteInstance);
	console.log('END [loadFedOfQueriesHandler]');
}


/**
 * Check that the address is a correct IP address
 * @param address
 * @returns {Boolean}
 */
function validateAddress(address)   
{  
	if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(address))  
	{  
		return (true)  ;
	}  
	return (false)  ;
}


/**
 * Check that the port is a correct port number
 * @param port
 * @returns {Boolean}
 */
function validatePort(port)   
{  
	if (/^[0-9]{1,5}$/.test(port))  
	{  
		return (true)  ;
	}  
	return (false)  ;
} 


/**
 * Check that fields are correct
 * @param address
 * @param port
 * @returns {String}
 */
function checkFields(address, port){
	errors = ""
	
	if(validateAddress(address) == false){
		errors += "The address is not valid.<br/>";
	}
	if(validatePort(port) == false){
		errors += "The port number is not valid.<br/>";
	}
	
	return errors;
}


/**
 * Check that instance information are valid
 * @returns {Boolean}
 */
function validateInstance(){
	address = $("#id_ip_address").val();
	port = $("#id_port").val();
	
	errors = checkFields(address, port);
	
	if (errors != ""){
		$("#instance_error").html(errors);
		return (false);
	}
	else{
		$("#instance_error").html("");
		return (true);
	}
}


/**
 * Edit repository information. Get the information from the server.
 */
editInstance = function()
{    
    var instanceid = $(this).attr("instanceid");
    var name = $(this).parent().siblings(':first').text();
    
    $("#edit_instance_error").html("");
    $("#edit-name").val(name);
    
    $(function() {
        $( "#dialog-edit-instance" ).dialog({
            modal: true,
            buttons: {
            	Edit: function() {	
            		name = $("#edit-name").val();
            		edit_instance(instanceid, name);
            	},
            	Cancel: function() {	
            		$( this ).dialog( "close" );
            	}
            }      
        });
	});
}


/**
 * AJAX call, edit an instance
 * @param instanceid id of the selected instance
 * @param name new name of the instance
 */
edit_instance = function(instanceid, name){
    $.ajax({
        url : "/admin/edit_instance",
        type : "POST",
        dataType: "json",
        data : {
        	instanceid : instanceid,
        	name: name
        },
        success: function(data){
        	if ('errors' in data){
        		$("#edit_instance_error").html(data.errors);
        	}else{
        		$("#dialog-edit-instance").dialog("close");
                $('#model_selection').load(document.URL +  ' #model_selection', function() {
                      loadFedOfQueriesHandler();
                });
        	}
        }
    });
}


/**
 * Delete a repository.
 */
deleteInstance = function()
{
	var instanceid = $(this).attr("instanceid");
	$(function() {
        $( "#dialog-deleteinstance-message" ).dialog({
            modal: true,
            width: 520,
            buttons: {
            	Delete: function() {	
            		delete_instance(instanceid);
            	},
            	Cancel: function() {	
            		$( this ).dialog( "close" );
            	}
            }      
        });
	});
}


/**
 * AJAX call, deletes an instance of a repository
 * @param instanceid id of the selected instance
 */
delete_instance = function(instanceid){
    $.ajax({
        url : "/admin/delete_instance",
        type : "POST",
        dataType: "json",
        data : {
        	instanceid : instanceid,
        },
        success: function(data){
        	$("#dialog-deleteinstance-message").dialog("close");
            $('#model_selection').load(document.URL +  ' #model_selection', function() {
                  loadFedOfQueriesHandler();
            });
        }
    });
}

