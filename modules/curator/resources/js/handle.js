var HandlePopupOptions = {
    title: "Get a unique handle",
}

saveHandleData = function() {
	// get the current handle from the form if present
	currentHandle = openModule.find(".moduleResult").text();
	
    return {'data': currentHandle};
}

configurePopUp('/curator/handle', HandlePopupOptions, saveHandleData);