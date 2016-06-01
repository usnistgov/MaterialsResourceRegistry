var targetNodes         = $("#xsdForm"); // 
var MutationObserver    = window.MutationObserver || window.WebKitMutationObserver;
var autoKeyObserver     = new MutationObserver (autoKeyHandler);
var obsConfig           = {childList: true, subtree:true};

// init number of keys to 0
var nbAutoKey = 0 

// Add a target node to the observer. Can only add one node at a time.
// Every time the form is updated, keyrefs will be updated 
targetNodes.each ( function () {
	autoKeyObserver.observe (this, obsConfig);
} );

function autoKeyHandler (mutationRecords) {
	current_nbAutoKey = $(".mod_auto_key").length;
	console.log('previous: ' + nbAutoKey);
	console.log('current: ' + current_nbAutoKey);
	// number of keys has changed
	if (current_nbAutoKey != nbAutoKey){
        console.log('Number of Keys has changed.')
        nbAutoKey = current_nbAutoKey;
        $.ajax({
            url : "/modules/curator/get-updated-keys",
            type : "GET",
            dataType: "json",
            success: function(data){
                console.log(data);
                var i;
                for (i = 0; i < data.length; ++i) {
                    var module_id = data[i];
                    console.log(module_id);
                    $.ajax({
                        url : "/modules/curator/auto-keyref?module_id=" + data[i],
                        type : "GET",
                        async : false,
                        success: function(response){
                            console.log("Replace refs " + module_id);
                            $("#" + module_id ).replaceWith(response);
                        },
                        error: function(){
                            console.log("Error");
                        }
                    });
                }
            }
        });
	} 
}