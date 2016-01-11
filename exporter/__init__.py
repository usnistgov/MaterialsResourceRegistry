import importlib

default_app_config = 'exporter.apps.ExporterConfig'

def get_exporter(Exporter):
    """
    :param Exporter location:
    :return:
    """
    pkglist = Exporter.split('.')

    pkgs = '.'.join(pkglist[:-1])
    func = pkglist[-1:][0]

    imported_pkgs = importlib.import_module(pkgs)
    a = getattr(imported_pkgs, func)
    instance = a()

    return instance