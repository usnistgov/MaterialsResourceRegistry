editForm = function(){
	console.log('editForm');
	if (document.referrer.indexOf('&useForm=true') != -1){
		window.location = document.referrer;
	}else{
		window.location = document.referrer + '&useForm=true';
	}
}