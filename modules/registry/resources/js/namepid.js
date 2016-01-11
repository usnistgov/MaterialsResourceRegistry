$('body').on('blur', '.name-pid-form input', function(event) {
	$form = $(this).closest('.name-pid-form');
	console.log($form);
	
	// Collect data
    var data = new FormData($form[0]);
    var module = $form.parent().parent();
    console.log(module);
    saveModuleData(module, data);
});