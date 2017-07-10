var custom_view_done;
var timeout;
var first_occurrence = true;

initSearch = function(listRefinements, keyword, resource, data_provider) {
    select_hidden_schemas(resource)
	initResources();
	loadRefinements(resource, listRefinements, keyword, data_provider);
}

selectType = function(radio, td_icon) {
    if (!$(td_icon).hasClass('disabled_refinements')) {
        var tree = getTypeTree();
        var root =  tree.fancytree('getTree');
        if (radio == "all"){
            selectAllCheckboxes(tree);
        }
        else if (root.length !== 0) {
            if(areAllSelected(tree)){
                root.visit(function(node){
                    node.setSelected(false);
                });
            }
            var node = root.getNodeByKey(radio);
            if (node != null) {
                node.setSelected(!node.isSelected());
            }
        }
    }
}

selectAllCheckboxes = function(root) {
    var selected = areAllSelected(tree);
    var root =  tree.fancytree('getTree');
    if (root.length !== 0) {
        root.visit(function(node){
            node.setSelected(!selected);
        });
    }
}

update_url = function() {
    if ( first_occurrence) {
        return ;
    }
    var refinements = [];
    $('*[id^="tree_"]').each(function() {
        getSelectedRefinements($(this), refinements);
    });

    var data_providers = [];
    $("#id_my_registries").find('input:checked').each(function(){
        var label = $("label[for='"+$(this).attr('checked_id')+"']");
        data_providers.push(label.text());
    });

	var keyword = $("#id_search_entry").val();
	$.ajax({
        url : "/explore/update_url",
        type : "GET",
        dataType: "json",
        data : {
            keyword: keyword,
            refinements: refinements,
            oai: data_providers,
        },
        success: function(data) {
            if (data.url.length == 0)
                data.url = History.getBaseUrl();

            History.pushState("", "", data.url);
        }
    });
}

/**
 * Set keywords
 */
set_keyword = function(keyword) {
    var list_keyword = keyword.split('&amp;');
    for (var i=0 ; i<list_keyword.length ; i++) {
        $("#id_search_entry").tagit("createTag", list_keyword[i]);
    }
}

/**
 * Set data providers
 */
set_data_provider = function(data_providers) {
    var list_oai = data_providers.split('&amp;');
    $("#id_my_registries").find('input').each(function(){
        var label = $("label[for='"+$(this).attr('checked_id')+"']");
        for (var i = 0 ; i < list_oai.length ; i++) {
            if (label.text() == list_oai[i]) {
                $(this).prop( "checked", true );
            }
        }
    });
}

/**
 * Load refinement queries
 */
selectRefinementQueries = function(listRefinement) {
	var list_refinements = listRefinement.split('&amp;');

    $('*[id^="tree_"]').each(function() {
        var root = $(this).fancytree('getTree');
        for (var i = 0; i < list_refinements.length; i++) {
            var node = root.getNodeByKey(list_refinements[i]);
            if (node != null) {
                node.setSelected(true);
            }
        }
    });
}

select_hidden_schemas = function (selected_val) {
// update the value of the search form
    if (selected_val == 'all') {
        // check all options
        $("#id_my_schemas").find("input").each(function () {
            $(this).prop("checked", true);
        });
    } else {
        // uncheck all options except the selected one
        $("#id_my_schemas").find("input").each(function () {
            if ($(this).val() == selected_val) {
                $(this).prop("checked", true);
            } else {
                $(this).removeAttr("checked");
            }
        });
    }
}

initResources = function(){
	// get radio to refine resource type
	var radio_btns = $("#refine_resource_type").children("input:radio");
	for(var i = 0; i < radio_btns.length; i++) {
		// when value change
		radio_btns[i].onclick = function() {
			// get the value
	        selected_val = $(this).val();
			// update selected icon
	        if (selected_val == 'repository'
	        	|| selected_val == 'projectarchive'
	        		|| selected_val == 'database'){
	        	$("#icons_table").find("td").each(function(){
		        	$(this).removeClass("selected_resource");
		        	if ($(this).attr("value") == 'datacollection') {
                        $(this).addClass("selected_resource");
                    }
	        	});
	        }else {
                $("#icons_table").find("td").each(function () {
                    $(this).removeClass("selected_resource");
                    if ($(this).attr("value") == selected_val) {
                        $(this).addClass("selected_resource");
                    }
                });
            }

			// update refinements options based on the selected schema
			loadRefinements(selected_val, '', '');

			// update filters: if custom, switch to default simple
			if ($("#results_view").val() == "custom"){
				$("#results_view").val("simple");
			}
			filter_result_display($("#results_view").val());
			custom_view_done = false;
            select_hidden_schemas(selected_val);
	    };
	}
}

initFilters = function(){
	// Set filter to simple by default
	$("#results_view").val("simple");
	
	// update view on filter change
	$("#results_view").on('change',function(){
		filter_result_display($("#results_view").val());
	});
}


filter_result_display = function(filter){
	$("#config_custom").css('display','none');
	
	if (filter == 'simple'){
		$(".nmrr_line").hide();
		$(".nmrr_line.line_publisher").show();
		$(".nmrr_line.line_creator").show();
		$(".nmrr_line.line_subject").show();
	}else if (filter == 'detailed'){
		$(".nmrr_line").show();
	}else if (filter == 'custom'){
		$("#config_custom").css('display','');
		if (custom_view_done == true){
	    	$(".nmrr_line").hide();
			$("#custom_view").children("input:checked").each(function(){
				$(".nmrr_line." + $(this).val()).show();
			});
		}
		else{
			configure_custom_view();
		}
	}
}


configure_custom_view = function(){
	if (custom_view_done == false){
		load_custom_view($('input[name=resource_type]:checked').val());
		custom_view_dialog();
	}else{
		custom_view_dialog();
	}
}


custom_view_dialog = function(){	
    $( "#dialog-custom-view" ).dialog({
        modal: true,
        height: 500,
        width: 400,
        buttons: {
            Cancel: function() {
            	$( this ).dialog( "close" );
            },
            Apply: function() {
            	$( this ).dialog( "close" );
            	$(".nmrr_line").hide();
    			$("#custom_view").children("input:checked").each(function(){
    				$(".nmrr_line." + $(this).val()).show();
    			});
            }
        },
        close: function(){
        	custom_view_done = true;
        }
    });
}


/**
 * Load custom view
 */
load_custom_view = function(schema){
	$.ajax({
        url : "/explore/custom-view?schema=" + schema,
        type : "GET",
        dataType: "json",
        success: function(data){
        	if('custom_fields' in data){
        		$("#custom_view").html(data.custom_fields);
        	}
    	}
    });
}



/**
 * AJAX call, gets query results
 * @param numInstance
 */
get_results_keyword_refined = function(numInstance){
	// clear the timeout
	clearTimeout(timeout);
	// send request if no parameter changed during the timeout
    timeout = setTimeout(function() {
        if (!first_occurrence) {
            update_url();
        }
    	$("#results").html('Please wait...');
        var keyword = $("#id_search_entry").val();
        var schemas_ = getSchemas();
        var refinements_ = loadRefinementQueries();
        var registries_ = getRegistries();
        updateRefinementsOccurrences(keyword, schemas_, refinements_, registries_);
        // Do not search if no type refinement are selected
        if(asSelectedElement(getTypeTree()))
        {
            $.ajax({
                url : "/explore/get_results_by_instance_keyword",
                type : "POST",
                dataType: "json",
                data : {
                    keyword: keyword,
                    schemas: schemas_,
                    refinements: refinements_,
                    onlySuggestions: false,
                    registries: registries_,
                    csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                },
                beforeSend: function( xhr ) {
                    $("#loading").addClass("isloading");
                },
                success: function(data){
                    if (data.resultString.length == 0){
                        // get no results
                        $("#results").html("No results found");
                        // get no results
                        $("#results_infos").html("0 result");
                    }
                    else{
                        // get result count
                        if(data.count > 1)
                            $("#results_infos").html(data.count + " results");
                        else
                            $("#results_infos").html(data.count + " result");
                        // get results
                        $("#results").html(data.resultString);
                        // filter the view
                        filter_result_display($("#results_view").val());
                        $(".description").shorten({showChars: 350,
                            ellipsesText: "",
                            moreText: "... show more",
                            lessText: " show less",
                        });
                    }
                },
                complete: function(){
                    $("#loading").removeClass("isloading");
                    checkEmptyAccordion();
                }
            });
        }
        else {
            // get no results
            $("#results").html("No results found");
            // get no results
            $("#results_infos").html("0 results");
        }
    }, 1000);
}

// clear all refinements
clearRefinements = function(){
	$("#refine_resource").find('input:checked').prop('checked',false);
	get_results_keyword_refined();
}

updateRefinementsOccurrences = function(keyword, schemas_, refinements_, registries_){
	$.ajax({
        url : "/explore/get_results_occurrences",
        type : "POST",
        dataType: "json",
        data : {
            keyword: keyword,
            schemas: schemas_,
            refinements: refinements_,
            allRefinements: getAllRefinements(),
            onlySuggestions: false,
            registries: registries_,
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
        },
        beforeSend: function( xhr ) {
            $(".occurrences").each(function(){
                $(this).html("-");
                $(this).closest('span').fadeTo(100, 0.2);
            });
            // Disable checkboxes
            $('*[id^="tree_"]').css("pointer-events", "none");
            // Disable clear
            $('.clearTree').addClass('disabled_refinements');
            // Disable icons
            $('#icons_table td').addClass('disabled_refinements');
            // Disable tags
            $('#myFilters li').addClass('disabled_refinements');
        },
        success: function(data){
            $.map(data.items, function (item) {
                var text = $("#"+item.text_id)
                text.html(item.nb_occurrences);
                if(item.nb_occurrences == 0)
                    text.closest('span').fadeTo(100, 0.2);
                else
                    text.closest('span').fadeTo(100, 1);
            });
        },
        complete: function(){
            // Enable checkboxes
            $('*[id^="tree_"]').css("pointer-events", "auto");
            // Enable clear
            $('.clearTree').removeClass('disabled_refinements');
            // Enable icons
            $('#icons_table td').removeClass('disabled_refinements')
            // Enable tags
            $('#myFilters li').removeClass('disabled_refinements');
        }
    });
}

/**
 * Load refinement queries
 */
loadRefinementQueries = function(){
	var dict = [];
    $('*[id^="tree_"]').each(function(){
        var refinements = [];
        getSelectedRefinements($(this), refinements);
        if(!$.isEmptyObject(refinements))
        {
            dict.push({
                key:   this.id,
                value: refinements
            });
        }
    });

	return JSON.stringify(dict);
}


getSelectedRefinements = function (tree, refinements){
    var nodes = tree.fancytree('getRootNode').tree.getSelectedNodes();
    $(nodes).each(function() {
        refinements.push($(this)[0].key);
    });
}

getAllRefinements = function(){
    var dict = [];

    $('*[id^="tree_"]').each(function(){
        var refinements = [];
        var nodes = $(this).fancytree('getRootNode').getChildren();
        getRefinementsChildren(nodes, refinements);
        dict.push({
            key:   this.id,
            value: refinements
        });
    });

	return JSON.stringify(dict);
}


getRefinementsChildren = function(children, refinements)
{
   if(children === undefined)
        return;

    $(children).each(function() {
        refinements.push($(this)[0].key);
        var nodes = $(this)[0].getChildren();
        getRefinementsChildren(nodes, refinements);
    });
}


loadRefinements = function(schema, listRefinements, keyword, data_provider){
	$("#refine_resource").html('');
	$.ajax({
        url : "/explore/load_refinements",
        type : "GET",
        dataType: "json",
        data : {
        	schema:schema,
        },
        success: function(data){
            $("#refine_resource").html(data.template);
            $.map(data.items, function (item) {
                initFancyTree(item.div_id, item.json_data);
            });
            if (first_occurrence) {
                selectRefinementQueries(listRefinements);
                set_keyword(keyword);
                set_data_provider(data_provider);
                tree = getTypeTree();
                if(!asSelectedElement(tree)) {
                    root = tree.fancytree('getTree');
                    selectAllCheckboxes(root);
                }
                $("a[href='#"+tree.parent().parent().prop('id')+"']").click();
            }
            initFilters();
	        custom_view_done = false;
	        get_results_keyword_refined();
	        first_occurrence = false;
        }
    });
}

initFancyTree = function(div_id, json_data) {

    $("#tree_"+div_id).fancytree({
        extensions: ["glyph", "wide", "customTag"],
        checkbox: true,
        icon: false,
        glyph: glyph_opts,
        wide: {
            iconWidth: "1em",
            iconSpacing: "0.5em",
            levelOfs: "1.5em"
        },
        customTag : {
            tag: "div"
        },
        _classNames: {
            active: "no-css",
            focused: "no-css"
        },
        selectMode: 3,
        source: JSON.parse(json_data),
        toggleEffect: { effect: "drop", options: {direction: "left"}, duration: 400 },
        init: function(event, data) {
            // $("#tree_"+div_id+" ul").addClass("fancytree-colorize-selected");
            // Render all nodes even if collapsed
            $(this).fancytree("getRootNode").render(force=true, deep=true);
        },
        select: function(event, data){
            if (! first_occurrence) {
                get_results_keyword_refined();
            }
            selectIcons();
            manageFilters($(this));
        }
    });
}

glyph_opts = {
    map: {
      doc: "glyphicon glyphicon-file",
      docOpen: "glyphicon glyphicon-file",
      checkbox: "glyphicon glyphicon-unchecked",
      checkboxSelected: "glyphicon glyphicon-check",
      checkboxUnknown: "glyphicon glyphicon-share",
      dragHelper: "glyphicon glyphicon-play",
      dropMarker: "glyphicon glyphicon-arrow-right",
      error: "glyphicon glyphicon-warning-sign",
      expanderClosed: "glyphicon glyphicon-menu-right",
      expanderLazy: "glyphicon glyphicon-menu-right",
      expanderOpen: "glyphicon glyphicon-menu-down",
      folder: "glyphicon glyphicon-folder-close",
      folderOpen: "glyphicon glyphicon-folder-open",
      loading: "glyphicon glyphicon-refresh glyphicon-spin"
    }
};

selectIcons = function () {
    icon = [];
    tree = getTypeTree();

    if(areAllSelected(tree)){
        icon.push("all");
    }
    else
    {
        var nodes = tree.fancytree('getRootNode').tree.getSelectedNodes(stopOnParents=true);
        $(nodes).each(function() {
            icon.push($(this)[0].key);
        });
    }

    $("#icons_table").find("td").each(function(){
        var i = 0;
        $(this).removeClass("selected_resource");
        var res = "^" + $(this).attr("value");
        for (; i < icon.length; i++) {
            if (icon[i].match(res)) {
                $(this).addClass("selected_resource");
            }
        }
    });
}

areAllSelected = function(tree) {
    var allCount = tree.fancytree('getRootNode').tree.count()
    var selectedNodes = tree.fancytree('getRootNode').tree.getSelectedNodes();

    return selectedNodes.length == allCount;
}

areAllParentSelected = function(tree) {
    var nodes = tree.fancytree('getRootNode').tree.getSelectedNodes(stopOnParents=true);
    var children = tree.fancytree('getRootNode').getChildren();

    return nodes.length == children.length;
}

areAllUnselected = function(tree) {
    var nodes = tree.fancytree('getRootNode').tree.getSelectedNodes();
    return nodes.length == 0;
}

areAllParentUnselected = function(tree) {
    var nodes = tree.fancytree('getRootNode').tree.getSelectedNodes(stopOnParents=true);
    return nodes.length == 0;
}

asSelectedElement = function(tree) {
    var nodes = tree.fancytree('getRootNode').tree.getSelectedNodes(stopOnParents=true);
    return nodes.length > 0;
}

getTypeTree = function () {
    return $('*[id^="tree_"]').first();
}

checkEmptyAccordion = function () {
    $('div .collapseXSLT').each(function() {
        if( $(this).is(':empty') ) {
            var link = $("[aria-controls='" + $(this).prop("id") + "']")
            link.hide();
        }
    });
}

manageFilters = function (tree) {
    if(areAllUnselected(tree))
        $("#myFilters").tagit("removeTagByLabel", tree.attr("name"));
    else if ($("#myFilters").tagit("isNew", tree.attr("name")))
    {
        $("#myFilters").tagit("createTag", tree.attr("name"), undefined, undefined, custom_id=tree.attr("id"));
        showFilters();
    }
}

initTagFilters = function () {
    $("#myFilters").tagit({
        readOnly: false,
        singleFieldNode: false,
        beforeTagRemoved: function(event, ui) {
            if(!ui.tag.hasClass('disabled_refinements'))
                clearTree("#"+ ui.tag.attr("custom_id"), ui.tag);
            else
                return false;
        },
        afterTagRemoved: function(event, ui) {
            if(!$("#myFilters").tagit("hasTag"))
                hideFilters();
        },
    }).ready(function() {
        $(this).find('#myFilters .tagit-new').css('display', 'none');
        hideFilters();
    });
}

showFilters = function () {
    $("#filters_refinements").show();
}

hideFilters = function () {
    $("#filters_refinements").hide();
}

clearTree = function(div_tree, link) {
    if (!$(link).hasClass('disabled_refinements')) {
        var root =  $(div_tree).fancytree('getTree');
        if (root.length !== 0) {
            root.visit(function(node){
                node.setSelected(false);
            });
        }
    }
}

clearAllTrees = function() {
    $(".clearTree").click();
}