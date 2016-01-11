$('body').on('click', '.mod_checkboxes input:checkbox', function(event) {
	$checkboxes = $(this).closest('.mod_checkboxes');
	console.log($checkboxes);
	var values = [];
	$checkboxes.find("input:checked").each(function() {
		  values.push($(this).val());
	});

	
	// Collect data
    var data = {
        'data[]': values
    }

    var module = $checkboxes.parent().parent();
    saveModuleData(module, data);
});