# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe
import sys
sys.argv.append('py2exe')
setup(
    version = '0.1.0',
    #description = '融合会议业务数据分析工具',
    #name = '融合会议业务数据分析工具',          
    windows=[{'script':'mainWnd.py','icon_resources':[(0,'res.dll')]}],
    options={'py2exe':{
                   'optimize': 2,
                   'compressed': 1,
                   'includes':['CryptTool', 'Crypto.Hash.HMAC','Crypto.Hash.MD2','Crypto.Hash.MD4','Crypto.Hash.MD5','Crypto.Hash.RIPEMD','Crypto.Hash.SHA','Crypto.Hash.SHA224','Crypto.Hash.SHA256','Crypto.Hash.SHA384','Crypto.Hash.SHA512'],
                   'dll_excludes':['w9xpopen.exe', 'MSVCP90.dll'],
                   'bundle_files': 3
                   }
            },
    data_files = ['res.dll',('imageformats',['imageformats/qico4.dll'])], requires=['Crypto']
)
