var xsd_xpath = null;
var loadAutocomplete = function() {
    configureAutocomplete({
        source: function(request, response) {
            var term = request.term;

            $.ajax({
                url: '/modules/curator/enum-autocomplete',
                method: 'POST',
                dataType: 'json',
                data: {
                    'xsd_xpath': (xsd_xpath===null)?'':xsd_xpath,
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
        minLength: 1,
        select: function(event, ui) {
            var selectedValue = ui.item.value;

            $(':focus').val(selectedValue);
            $(':focus').trigger('blur');
        }
    });
};

$(document).on('focus', '.mod_autocomplete input[type="text"]', function(event) {
    loadAutocomplete();

    var $modDisplay = $(this).parents('.module').find('.moduleDisplay');
    xsd_xpath = $modDisplay.find('span').text();
});

$(document).on('blur', '.mod_autocomplete input[type="text"]', function(event) {
    var $this = $(this);
    saveModuleData($this.parents('.module'), {'data': $this.val(), 'xsd_xpath': xsd_xpath});
});