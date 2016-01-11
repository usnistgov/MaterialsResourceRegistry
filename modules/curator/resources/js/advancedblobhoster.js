var advancedBlobHosterPopupOptions = {
    title: "Select a file",
}

saveAdvancedBlobHosterData = function() {
    return new FormData(openPopUp.find('.advanced-blobhoster-form')[0]);
}

configurePopUp('/curator/advanced-blob-hoster', advancedBlobHosterPopupOptions, saveAdvancedBlobHosterData);