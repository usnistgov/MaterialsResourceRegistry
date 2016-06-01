updateForm = function(event) {
    event.preventDefault();

    var $changedModule = $(this);

    $('input').each(function(index, item) {
        var $input = $(item);

        $.ajax({
            'url': '/curate/element_value',
            'type': 'POST',
            'dataType': 'json',
            'data': {
                'id': $input.attr('id')
            },
            'success': function(data) {
                $input.val(data.value);
            },
            'error': function(data) {

            }
        });

    });

    $('select[id]').each(function(index, item) {
        var $select = $(item);

        $.ajax({
            'url': '/curate/element_value',
            'type': 'POST',
            'dataType': 'json',
            'data': {
                'id': $select.attr('id')
            },
            'success': function(data) {
                $select.val(data.value);
            },
            'error': function(data) {

            }
        });
    });

    $('.module').each(function(index, item) {
        var $module = $(item);

        if ( $changedModule.attr('id') == $module.attr('id') ) {
            return;
        }

        $.ajax({
            'url': '/curate/element_value',
            'type': 'POST',
            'dataType': 'json',
            'data': {
                'id': $module.attr('id')
            },
            'success': function(data) {
                saveModuleData($module, data.value);
            },
            'error': function(data) {

            }
        });
    });
};

$(document).on('change', '.mod_options', updateForm)