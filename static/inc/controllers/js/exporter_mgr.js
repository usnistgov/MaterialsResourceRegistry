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
    selected_option = $( "#dialog-exporters" ).find("input:checkbox[name='XSLTExporter']:checked").val()
    if (selected_option == undefined)
    {
        $("#xslts").hide();
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
    var elems = $("input[name*=Exporter]")
    var listIdOn = [];
    for(var i = 0; i < elems.length; i++) {
    	if(elems[i].checked == true)
    	{
    		listIdOn.push(elems[i].getAttribute("id"));
    	}
    }

    var elemsXslt = $("input:visible[name=xslt]")
    var listIdOnXslt = [];
    for(var i = 0; i < elemsXslt.length; i++) {
    	if(elemsXslt[i].checked == true)
    	{
    		listIdOnXslt.push(elemsXslt[i].getAttribute("id"));
    	}
    }

    $.ajax({
        url : "/admin/save_exporters",
        type : "POST",
        dataType: "json",
        data : {
            listIdOn : listIdOn,
            listIdOnXslt : listIdOnXslt,
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
    selected_option = $( "#dialog-exporters" ).find("input:checkbox[name='XSLTExporter']:checked").val()
    if (selected_option == undefined)
    {
        $('#xslts input:not([disabled])').removeAttr('checked');
        // Refresh the jQuery UI buttonset.
        ButtonSetInit();
        $("#xslts").hide(500);
    }
    else
    {
        $("#xslts").show(500);
    }
}