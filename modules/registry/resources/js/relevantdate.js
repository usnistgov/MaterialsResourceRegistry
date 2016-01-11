$('body').on('blur', '.relevant-date-form input', function(event) {
	$form = $(this).closest('.relevant-date-form');
	
	// Collect data
    var data = new FormData($form[0]);
    var module = $form.parent().parent();
    console.log(module);
    saveModuleData(module, data);
});