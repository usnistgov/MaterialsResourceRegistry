configureAutocomplete({
    source: function(request, response) {
        var term = request.term;

        $.ajax({
            url: '/modules/examples/autocomplete',
            method: 'POST',
            dataType: 'json',
            data: {
                'list': term
            },
            success: function(data) {
                var $data = $(data.html);

                var textData = $data.find('.moduleDisplay').text();
                var re = new RegExp("'", 'g');
                textData = textData.replace(re, '\"');

                var jsonData = JSON.parse(textData);
                response(jsonData);
            }
        });
    },
    minLength: 0
});

$('body').on('blur', '.mod_autocomplete input[type="text"]', function(event) {
    var $this = $(this);
    saveModuleData($this.parents('.module'), {'data': $this.val()});
});