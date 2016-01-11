var blobHosterPopupOptions = {
    title: "Upload File",
}

saveBlobHosterData = function() {
    return new FormData(openPopUp.find('.blobhoster-form')[0]);
}

configurePopUp('/curator/blob-hoster', blobHosterPopupOptions, saveBlobHosterData);