var excelUploaderPopupOptions = {
    title: "Upload Excel File",
}

saveExcelUploaderData = function() {
    return new FormData(openPopUp.find('.excel-uploader-form')[0]);
}

configurePopUp('/diffusion/upload-excel', excelUploaderPopupOptions, saveExcelUploaderData);