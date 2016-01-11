/**
 * 
 * File Name: user_account_req.js
 * Author: Sharief Youssef
 * 		   sharief.youssef@nist.gov
 *
 *        Guillaume SOUSA AMARAL
 *        guillaume.sousa@nist.gov
 * 
 * Sponsor: National Institute of Standards and Technology (NIST)
 * 
 */

/**
 * Checks that the password is correct
 * @param password
 * @returns {Boolean}
 */
checkPassword = function(password){
	//if length is 8 characters or more, increase strength value
	if (password.length < 8){
		return false;
	}
//	//lower and uppercase characters
//	if (!password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)){
//		return false;
//	}
	
	//numbers and characters
	if (!password.match(/([a-zA-Z])/) || !password.match(/([0-9])/)){
		return false;
	} 
}

/**
 * Checks that the two passwords are correct
 */
checkPasswords = function(pass1, pass2){
	errors = ""
		
	if (pass1 != pass2){
		errors += "Passwords should be identical.";
	}else{
		if(checkPassword(pass1) == false){
			errors += "Password should respect the following requirements:<br/>";
			errors += "- Minimum length: 8 characters.<br/>";
			errors += "- At least 1 alphanumeric character.<br/>";
			errors += "- At least 1 non alphanumeric character.<br/>";				
		}
	}
	
	return errors;
}

/**
 * Checks that the current request is valid
 */
validateRequest = function(){
	pass1 = $("#id_password1").val();
	pass2 = $("#id_password2").val();
	
	errors = checkPasswords(pass1,pass2);
	
	if (errors != ""){
		$("#request_error").html(errors);
		return (false);
	}
	else{
		$("#request_error").html("");
		return (true);
	}
}

/**
 * Checks that the new password is valid
 */
validatePassword = function()
{
	pass1 = $("#id_new1").val();
	pass2 = $("#id_new2").val();
	
	errors = checkPasswords(pass1,pass2);
	
	if (errors != ""){
		$("#password_error").html(errors);
		return (false);
	}
	else{
		$("#password_error").html("");
		return (true);
	}
}

/**
 * Return to profile
 */
returnProfile = function()
{
	console.log('BEGIN [returnProfile]');

	window.location = '/my-profile'

	console.log('END [returnProfile]');
}