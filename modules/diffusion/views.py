from models import PeriodicTableModule, PeriodicTableMultipleModule, ExcelUploaderModule


def periodic_table_view(request):
    return PeriodicTableModule().render(request)


def periodic_table_multiple_view(request):
    return PeriodicTableMultipleModule().render(request)


def upload_excel_view(request):
    return ExcelUploaderModule().render(request)
