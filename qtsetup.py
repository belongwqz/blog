# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe
import sys
try:
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]:
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    pass
sys.argv.append("py2exe")
setup(
    version = "0.1.0",
    #description = "融合会议业务数据分析工具",
    #name = "融合会议业务数据分析工具",          
    windows=[{"script":"ReportWnd.py",'icon_resources':[(0,"res.dll")]}],
    options={"py2exe":{
                   "optimize": 2,
                   "compressed": 1,
                   "includes":["sip","resource","tool"],
                   "dll_excludes":["w9xpopen.exe"]
                   }
            },
    data_files = ['res.dll',('imageformats',['imageformats/qico4.dll'])]
)
