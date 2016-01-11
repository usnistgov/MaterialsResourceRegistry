var periodicTablePopupOptions = {
    width: 700,
    title: "Select Element",
    create: function(event, ui) {
        var pTable = $(this).find('.periodic-table');

        // Initialization
        var popUpState = openPopUp.find('.periodic-table-keep-state');

        if(popUpState.text() !== 'true') {
            $.each(pTable.find('.selected'), function(index, element) {
                $(element).removeClass('selected');
            });

            $.each(pTable.find('.orig-selected'), function(index, element) {
                $(element).addClass('selected');
            });
        }

        popUpState.text("false");
    },
}

// Selection highlight
$(document).on('click', '.periodic-table-simple td.p-elem', function(event) {
    var pTable = openPopUp.find('.periodic-table');
    $.each(pTable.find('.selected'), function(index, element) {
        $(element).removeClass('selected');
    });

    $(this).addClass('selected');
});

savePeriodicTableData = function() {
    var selectedElement = openPopUp.find('.periodic-table .selected');

    openPopUp.find('.periodic-table-keep-state').text("true");

    $.each(openPopUp.find('.periodic-table').find('.orig-selected'), function(index, element) {
        $(element).removeClass('orig-selected');
    });
    selectedElement.addClass('orig-selected');

    return {'selectedElement': selectedElement.text()};
}

configurePopUp('/diffusion/periodic-table', periodicTablePopupOptions, savePeriodicTableData);