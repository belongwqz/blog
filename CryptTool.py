# -*- coding:utf-8 -*
__author__ = 'w00177728'
from Crypto.Cipher import AES, ARC2, ARC4, Blowfish, CAST, DES, DES3, PKCS1_OAEP, PKCS1_v1_5, XOR
from Crypto.PublicKey import RSA
import base64
import importlib
import traceback
import zlib
import io
import os
#import hashlib


class SumCrypt(object):
    ALG_LST = {
        'HMAC': importlib.import_module('Crypto.Hash.HMAC'),
        'MD2': importlib.import_module('Crypto.Hash.MD2'),
        'MD4': importlib.import_module('Crypto.Hash.MD4'),
        'MD5': importlib.import_module('Crypto.Hash.MD5'),
        'RIPEMD': importlib.import_module('Crypto.Hash.RIPEMD'),
        'SHA': importlib.import_module('Crypto.Hash.SHA'),
        'SHA224': importlib.import_module('Crypto.Hash.SHA224'),
        'SHA256': importlib.import_module('Crypto.Hash.SHA256'),
        'SHA384': importlib.import_module('Crypto.Hash.SHA384'),
        'SHA512': importlib.import_module('Crypto.Hash.SHA512')
    }

    def __proxySum(self, module, func, param):
        return getattr(module, func)(param).hexdigest().upper()

    def __init__(self, algType):
        self.alg = algType

    def __loopCheck(self, fileName, func, back=False, chunk_size=1024):
        backInfo = None
        with io.FileIO(fileName, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if len(chunk) == 0:
                    break
                if not back:
                    func(chunk)
                else:
                    if not backInfo:
                        backInfo = func(chunk)
                    else:
                        backInfo = func(chunk, backInfo)
        return backInfo

    def File(self, fileName):
        if not os.path.isfile(fileName):
            return u'文件不存在！'
        if self.alg == 'CRC32':
            return '%x' % (self.__loopCheck(fileName.encode("gb2312"), zlib.crc32, True) & 0xffffffff)
        else:
            ins = getattr(SumCrypt.ALG_LST[self.alg], 'new')()
            self.__loopCheck(fileName.encode("gb2312"), ins.update)
            return ins.hexdigest().upper()

    def String(self, cont):
        if self.alg == 'CRC32':
            return '%x' % zlib.crc32(cont.encode("gb2312"))
        else:
            return self.__proxySum(SumCrypt.ALG_LST[self.alg], 'new', cont.encode("gb2312"))


class CipherCrypt(object):
    def __init__(self, cType, key, cont):
        self.cType = cType.encode('gb2312')
        self.key = key.encode('gb2312')
        self.cont = cont.encode('gb2312')
        self.pad = lambda s, bs: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        self.unpad = lambda s: s[0:-ord(s[-1])]

    def Encrypt(self):
        result = None
        try:
            if self.cType == 'AES':
                result = AES.new(self.key, AES.MODE_ECB).encrypt(
                    self.pad(self.cont, AES.block_size)).encode('hex').upper()
            elif self.cType == 'ARC2':
                result = ARC2.new(self.key, ARC2.MODE_ECB).encrypt(
                    self.pad(self.cont, ARC2.block_size)).encode('hex').upper()
            elif self.cType == 'ARC4':
                result = ARC4.new(self.key).encrypt(self.cont).encode('hex').upper()
            elif self.cType == 'Blowfish':
                result = Blowfish.new(self.key, Blowfish.MODE_ECB).encrypt(
                    self.pad(self.cont, Blowfish.block_size)).encode('hex').upper()
            elif self.cType == 'CAST':
                result = CAST.new(self.key, CAST.MODE_ECB).encrypt(
                    self.pad(self.cont, CAST.block_size)).encode('hex').upper()
            elif self.cType == 'DES':
                result = DES.new(self.key, DES.MODE_ECB).encrypt(
                    self.pad(self.cont, DES.block_size)).encode('hex').upper()
            elif self.cType == 'DES3':
                result = DES3.new(self.key, DES3.MODE_ECB).encrypt(
                    self.pad(self.cont, DES3.block_size)).encode('hex').upper()
            elif self.cType == 'PKCS1_OAEP':
                result = PKCS1_OAEP.new(RSA.importKey(open(self.key).read())).encrypt(self.cont).encode('hex').upper()
            elif self.cType == 'PKCS1_v1_5':
                result = PKCS1_v1_5.new(RSA.importKey(open(self.key).read())).encrypt(self.cont).encode('hex').upper()
            elif self.cType == 'XOR':
                result = XOR.new(self.key).encrypt(self.cont).encode('hex').upper()
            elif self.cType == 'BASE64':
                result = base64.b64encode(self.cont)
            elif self.cType == 'BASE32':
                result = base64.b32encode(self.cont)
            elif self.cType == 'BASE16':
                result = base64.b16encode(self.cont)
            else:
                result = u'当前算法尚未实现'
        except:
            print traceback.format_exc()
        return result

    def Decrypt(self):
        result = None
        try:
            if self.cType == 'AES':
                result = self.unpad(AES.new(self.key, AES.MODE_ECB).decrypt(
                    self.cont.decode('hex'))).decode('gb2312')
            elif self.cType == 'ARC2':
                result = self.unpad(ARC2.new(self.key, ARC2.MODE_ECB).decrypt(
                    self.cont.decode('hex'))).decode('gb2312')
            elif self.cType == 'ARC4':
                result = ARC4.new(self.key).decrypt(self.cont.decode('hex')).decode('gb2312')
            elif self.cType == 'Blowfish':
                result = self.unpad(Blowfish.new(self.key, Blowfish.MODE_ECB).decrypt(
                    self.cont.decode('hex'))).decode('gb2312')
            elif self.cType == 'CAST':
                result = self.unpad(CAST.new(self.key, CAST.MODE_ECB).decrypt(
                    self.cont.decode('hex'))).decode('gb2312')
            elif self.cType == 'DES':
                result = self.unpad(DES.new(self.key, DES.MODE_ECB).decrypt(
                    self.cont.decode('hex'))).decode('gb2312')
            elif self.cType == 'DES3':
                result = self.unpad(DES3.new(self.key, DES3.MODE_ECB).decrypt(
                    self.cont.decode('hex'))).decode('gb2312')
            elif self.cType == 'PKCS1_OAEP':
                result = PKCS1_OAEP.new(self.key).decrypt(self.cont.decode('hex')).decode('gb2312')
            elif self.cType == 'PKCS1_v1_5':
                result = PKCS1_v1_5.new(self.key).decrypt(self.cont.decode('hex')).decode('gb2312')
            elif self.cType == 'XOR':
                result = XOR.new(self.key).decrypt(self.cont.decode('hex')).decode('gb2312')
            elif self.cType == 'BASE64':
                result = base64.b64decode(self.cont).strip()
            elif self.cType == 'BASE32':
                result = base64.b32decode(self.cont).strip()
            elif self.cType == 'BASE16':
                result = base64.b16decode(self.cont).strip()
            else:
                result = u'当前算法尚未'
        except:
            print traceback.format_exc()
            return result
        return result
