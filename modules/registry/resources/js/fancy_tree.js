var save_selected_checkboxes = function(event, data){
	$mod_fancy_tree = $(event.target);
	var values = [];

    var nodes = $mod_fancy_tree.fancytree('getRootNode').tree.getSelectedNodes();
    $(nodes).each(function() {
        console.log($(this)[0].key);
        values.push($(this)[0].key);
    });

	// Collect data
    var data = {
        'data[]': values
    }

    var module = $mod_fancy_tree.parent().parent().parent();
    saveModuleData(module, data);
};
