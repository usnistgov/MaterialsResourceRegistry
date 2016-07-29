(function() {
    "use strict";

    // Save the value of one (default) element in the database
    var saveElement = function(event) {
        event.preventDefault();

        var $input = $(this);
        var inputId = $input.attr('id');

        console.log('Saving element ' + inputId + '...');

        $.ajax({
            'url': '/curate/save_element',
            'type': 'POST',
            'dataType': 'json',
            'data': {
                'id': inputId,
                'value': $input.val()
            },
            success: function() {
                console.log('Element ' + inputId + ' saved');
            },
            error: function() {
                console.error('An error occured when saving element ' + inputId);
            }
        });
    };

    // Save events
    $(document).on('blur', 'input.default', saveElement);
    $(document).on('change', 'select.restriction', saveElement); 
})();
