(function() {
    "use strict";
   
    // Save the form in the database
    var sendSaveRequest = function() {
        console.log('Saving form...');

        $.ajax({
            'url': '/curate/save_form',
            'type': 'POST',
            'dataType': 'json',
            success: function() {
                $( "#dialog-saved-message" ).dialog({
                    modal: true,
                    buttons: {
                        Ok: function() {
                            $( this ).dialog( "close" );
                        }
                    }
                });
            },
            error: function() {
            
            }
        });
    };

    // Display the saving confirmation popup
    var saveForm = function(event)
    {
        event.preventDefault();

        $(function() {
            $( "#dialog-save-form-message" ).dialog({
                modal: true,
                buttons: {
                    Save: function() {
                        sendSaveRequest();
                        $( this ).dialog( "close" );
                    },
                    Cancel: function() {
                        $( this ).dialog( "close" );
                    }
                }
            });
        });
    };

    // Handling toolbars events
    $(document).on('click', '.save-form', saveForm);
})();
