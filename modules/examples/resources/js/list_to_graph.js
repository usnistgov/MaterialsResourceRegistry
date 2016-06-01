$('body').on('blur', '.mod_async_input.list_to_graph input[type="text"]', function(event) {
	async_input($(this), listToGraph);
});

listToGraph = function(input){
	var modResult = $(input).parents('.module').find('.moduleResult').text();
	var arr = modResult.split(' ');
	var x = d3.scale.linear()
		.domain([0, d3.max(arr)])
		.range([0, 420]);

	d3.select(".chart")
	  .selectAll("div")
	    .data(arr)
	  .enter().append("div")
	    .style("width", function(d) { return x(d) + "px"; })
	    .text(function(d) { return d; });
}