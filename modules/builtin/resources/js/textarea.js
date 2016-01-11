$('body').on('blur', '.mod_textarea textarea', function(event) {
    // Collect data
    var data = {
        'data': $(this).val()
    }

    var module = $(this).parent().parent().parent();
    saveModuleData(module, data);
});