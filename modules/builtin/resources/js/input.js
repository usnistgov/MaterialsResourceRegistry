$('body').on('blur', '.mod_input input[type="text"]', function(event) {
    // Collect data
    var data = {
        'data': $(this).val()
    }

    var module = $(this).parent().parent().parent()
    saveModuleData(module, data);
});