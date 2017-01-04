# setup file

from distutils.core import setup
import py2exe

data_files = [
    ("", [
        "C:\\Staff\\Python27\\python27.dll",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\MessageBox.ui",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\MainWindow.ui",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\TableWindow.ui"
    ]),
    ("icons", [
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\icons\\GearICO.ico",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\icons\\gear.png",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\icons\\tick.png",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\icons\\warning.png",
    ]),
    ("tables", [
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\tables\\Kc.png",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\tables\\Yf.png",
    ]),
    ("sources", [
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\sources\\DisliKutusu_simple.py",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\sources\\evolvent.py",
        "C:\\Users\\MW\\Desktop\\DisliKutusu\\DisliKutusu.pyw",
    ])
]


setup(
    packages = [],
    package_data = {},
    scripts = [],
    data_files = data_files,
    windows=[{
        "script": "DisliKutusu.pyw",
        "icon_resources" : [ (1, "icons/GearICO.ico") ],
        "name": "Disli Kutusu".decode("u8"),
        "description": "Disli Kutusu Boyutlandirma".decode("u8"),
        "version": "1.0.0",
        "author": "",
        "copyright": "243196 + 243268",
        "company_name": "KTU",
        "dest_base": "DisliKutusu_app",
    }],
    options={
        "py2exe": {
            "skip_archive": True,
            "includes": ["sip"],
            "optimize": 1,
            "bundle_files": 3,
            "compressed": False,
        }
    }
)

