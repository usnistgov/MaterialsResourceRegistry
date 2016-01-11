/**
 * 
 * File Name: explore.js
 * Author: Sharief Youssef
 * 		   sharief.youssef@nist.gov
 *
 *         Guillaume SOUSA AMARAL
 *         guillaume.sousa@nist.gov
 *
 *         Pierre Francois RIGODIAT
 *         pierre-francois.rigodiat@nist.gov
 * 
 * Sponsor: National Institute of Standards and Technology (NIST)
 * 
 */


Init = function (){
    selected_option = $( "#dialog-exporters" ).find("input:checkbox[name='XSLTShort']:checked").val()
    if (selected_option == undefined)
    {
        $("#xslts_short").hide();
    }
    selected_option = $( "#dialog-exporters" ).find("input:checkbox[name='XSLTDetailed']:checked").val()
    if (selected_option == undefined)
    {
        $("#xslts_detailed").hide();
    }
    ButtonSetInit();
}


ButtonSetInit = function(){
    var buttonsetElts = $("td[id^=ButtonSet]")
    $.each(buttonsetElts, function(index, props) {
         $("#"+props.id).buttonset();
    });

}

saveTemplate = function(){
    var idXsltShort = $("input:visible[name=short_xslt]:checked").attr("xsltId")
    var idXsltDetailed = $("input:visible[name=detailed_xslt]:checked").attr("xsltId")

    $.ajax({
        url : "/admin/save_result_xslt",
        type : "POST",
        dataType: "json",
        data : {
            idXsltShort : idXsltShort,
            idXsltDetailed : idXsltDetailed,
        },
        success: function(data){
        	saveTemplateCallback();
        }
    });
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

deselectXSLT = function (){
    selected_option = $( "#dialog-exporters" ).find("input:checkbox[name='XSLTShort']:checked").val()
    if (selected_option == undefined)
    {
        $('#xslts_short input:not([disabled])').removeAttr('checked');
        // Refresh the jQuery UI buttonset.
        ButtonSetInit();
        $("#xslts_short").hide(500);
    }
    else
    {
        $("#xslts_short").show(500);
    }

    selected_option = $( "#dialog-exporters" ).find("input:checkbox[name='XSLTDetailed']:checked").val()
    if (selected_option == undefined)
    {
        $('#xslts_detailed input:not([disabled])').removeAttr('checked');
        // Refresh the jQuery UI buttonset.
        ButtonSetInit();
        $("#xslts_detailed").hide(500);
    }
    else
    {
        $("#xslts_detailed").show(500);
    }
}
