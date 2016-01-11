$(document).ready(function(){
	$('ul.dropdown').superfish({
		animation: {height: 'show'},
		onBeforeShow: function() {
		    var $input = $(this).siblings('a:first');

            if($input.html()) {
                inputHTML = $input.html().replace('right', 'down');
		        $input.html(inputHTML);
            }
		},
		onHide: function() {
            var $input = $(this).siblings('a:first');

		    inputHTML = $input.html().replace('down', 'right');
		    $input.html(inputHTML);
		}
	});  

});