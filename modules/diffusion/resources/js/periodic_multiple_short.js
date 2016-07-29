var periodicTableMultiplePopupOptions = {
    width: 700,
    title: "Periodic Table",
    create: function(event, ui) {
        // Initialization
        $(this).find('.sample-row').hide();
        $(this).find('.saved-data').hide();

        var elements = $(this).find('.element-list tbody tr:not(.empty)');
        var savedElementCount = 0;

        $.each(elements, function(index, element) {
            var $element = $(element);

            if($element.hasClass('saved')) {
                savedElementCount += 1;

                if($element.is(':hidden')) {
                    $element.show();
                }

                var qty = $element.find('.qty .saved-data').text();
                $element.find('.qty input').val(qty);

                var pur = $element.find('.pur .saved-data').text();
                $element.find('.pur input').val(pur);

            } else {
                $element.remove();
            }
        });

        console.log('saved:' + savedElementCount);
        if(savedElementCount === 0) {
            $(this).find('.element-list .empty').show();
        }
    },
}

$(document).on('click', '.periodic-table-multiple td.p-elem', function(event) {
    var chosenTable = openPopUp.find('.element-list');
    var elementName = $(this).text();

    var newRow = chosenTable.find('tr.sample-row').clone();
    newRow.show();
    newRow.removeClass('sample-row');
    newRow.find('td:first').text(elementName);

    chosenTable.find('.empty').hide();
    chosenTable.find('tbody').append(newRow);
});

$(document).on('click', '.element-list .remove-element', function(event) {
    var chosenTable = openPopUp.find('.element-list');
    var currentRow = $(this).parent().parent();

    if(currentRow.hasClass('saved')) {
        currentRow.hide();
        currentRow.addClass('hidden');
    } else {
        currentRow.remove();
    }

    console.log(chosenTable.find('tbody').children(':visible'));
    if(chosenTable.find('tbody').children(':visible').length === 0) {
        chosenTable.find('.empty').show();
    }
});

savePeriodicTableMultipleData = function() {
    var hiddenSavedElements = openPopUp.find('.saved:hidden');
    $.each(hiddenSavedElements, function(index, hiddenElement) {
        $(hiddenElement).remove();
    });

    var elementList = openPopUp.find('.element-list tbody');
    var data = [];

    $.each(elementList.find('tr'), function(index, element) {
        var $element = $(element);
        var elementData = {};

        if(!$element.hasClass('empty')) {
            $element.addClass('saved');

            elementData.name = $element.find('.name').text();
            elementData.qty = $element.find('.qty input').val();
            $element.find('.qty .saved-data').text(elementData.qty);

            elementData.pur = $element.find('.pur input').val();
            $element.find('.pur .saved-data').text(elementData.pur);

            data.push(elementData);
        }
    });

    return {'elementList': JSON.stringify(data)};
}

configurePopUp('/diffusion/periodic-table-multiple', periodicTableMultiplePopupOptions, savePeriodicTableMultipleData);