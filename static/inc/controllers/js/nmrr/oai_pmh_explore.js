dialog_detail_oai_pmh = function(id){
	$.ajax({
        url : "/oai_pmh/explore/detail_result_keyword?id=" + id,
        type : "GET",
        success: function(data){
        	console.log(data);
        	$("#result_detail").html(data);
        	
        	$(function() {
                $( "#dialog-detail-result" ).dialog({
                    modal: true,
                    height: 430,
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

getRegistries = function(numInstance){
    var values = [];
    $('#id_my_registries input:checked').each(function() {
        values.push(this.value);
    });

    return values;
}