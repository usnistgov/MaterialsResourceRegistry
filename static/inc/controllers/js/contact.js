/**
 * 
 * File Name: contact.js
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
 * Load controllers for contact messages
 */
loadContactMessagesHandler = function(){
    console.log('BEGIN [loadContactMessagesHandler]');
    $('.remove.message').on('click', removeMessage);
    console.log('END [loadContactMessagesHandler]');
}


/**
 * Delete a message from the list
 */
removeMessage = function(){
	var messageid = $(this).attr("messageid");
	$(function() {
	    $( "#dialog-confirm-delete" ).dialog({
	      modal: true,
	      buttons: {
	        Yes: function() {
	          $( this ).dialog( "close" );
	          remove_message(messageid);
	        },
	        No:function() {
	         $( this ).dialog( "close" );
		    }
	      }
	    });
	  });	
}


/**
 * AJAX call, removes a message
 * @param messageid id of the message
 */
remove_message = function(messageid){
    $.ajax({
        url : "/admin/remove_message",
        type : "POST",
        data:{
        	messageid: messageid
        },
        dataType: "json",
        success: function(data){
        	$('#model_selection').load(document.URL +  ' #model_selection', function() {
                loadContactMessagesHandler();
            });
        }
    });
}