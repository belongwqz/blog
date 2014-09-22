# -*- coding:utf-8 -*-
#
#作者：w00177728
#时间：2013/3/5
#说明：升级工具类封装，包含了升级常用的操作类，以及文本格式化处理、xml处理等功能
#
from __future__ import generators
import ConfigParser
import os
import sys
import re
import logging
import time
import shutil
import codecs
import random
import string
from xml.dom import minidom
from pyexpat import ExpatError
from warnings import warn as _warn

ErrorSizeChanged = "UnSortedDict changed size during iteration!"
WarnNoOrderArg  = "UnSortedDict created/updated from unordered mapping object"
WarnNoOrderKW   = "UnSortedDict created/updated with (unordered!) keyword arguments"

def CopyBaseClassDocs(className, bases, dictVal, metaClass=type):
    for (name, member) in dictVal.iteritems():
        if getattr(member, "__doc__", None):
            continue
        for base in bases:
            baseMember = getattr(base, name, None)
            if not baseMember:
                continue
            baseMemberDoc = getattr(baseMember, "__doc__", None)
            if baseMemberDoc:
                member.__doc__ = baseMemberDoc
    return metaClass(className, bases, dictVal)

#封装一个不排序（稳定）的字典容器
class UnSortedDict(dict):
    __metaClass__ = CopyBaseClassDocs # 将基类的描述拷贝过来

    # Python 2.2 不处理 __* inside __slots__
    __slots__ = ("_UnSortedDict__ksl",) # key sequence list aka __ksl

    # @staticmethod
    def is_ordered(dictInstance):
        """Returns true if argument is known to be ordered."""
        if isinstance(dictInstance, UnSortedDict):
            return True
        try:
            if len(dictInstance) <= 1:
                return True
        except:
            pass
        return False
    is_ordered = staticmethod(is_ordered)

    def __init__(self, *arg, **kw):
        if arg:
            if len(arg) > 1:
                raise TypeError("at most one argument permitted")
            arg = arg[0]
            if hasattr(arg, "keys"):
                if not self.is_ordered(arg):
                    _warn(WarnNoOrderArg, RuntimeWarning, stacklevel=2)
                super(UnSortedDict, self).__init__(arg, **kw)
                self.__ksl = arg.keys()
            else:
                super(UnSortedDict, self).__init__(**kw)
                self.__ksl = []
                for pair in arg:
                    if len(pair) != 2:
                        raise ValueError("not a 2-tuple", pair)
                    self.__setitem__(pair[0], pair[1])
                if kw:
                    ksl = self.__ksl
                    for k in super(UnSortedDict, self).iterkeys():
                        if k not in ksl:
                            ksl.append(k)
                    self.__ksl = ksl
        else:
            super(UnSortedDict, self).__init__(**kw)
            self.__ksl = super(UnSortedDict, self).keys()
        if len(kw) > 1:
            _warn(WarnNoOrderKW, RuntimeWarning, stacklevel=2)

    def update(self, *arg, **kw):
        if arg:
            if len(arg) > 1:
                raise TypeError("at most one non-keyword argument permitted")
            arg = arg[0]
            if hasattr(arg, "keys"):
                if not self.is_ordered(arg):
                    _warn(WarnNoOrderArg, RuntimeWarning, stacklevel=2)
                super(UnSortedDict, self).update(arg)
                ksl = self.__ksl
                for k in arg.keys():
                    if k not in ksl:
                        ksl.append(k)
                self.__ksl = ksl
            else:
                 for pair in arg:
                    if len(pair) != 2:
                        raise ValueError("not a 2-tuple", pair)
                    self.__setitem__(pair[0], pair[1])
        if kw:
            if len(kw) > 1:
                _warn(WarnNoOrderKW, RuntimeWarning, stacklevel=2)
            super(UnSortedDict, self).update(kw)
            ksl = self.__ksl
            for k in kw.iterkeys():
                if k not in ksl:
                    ksl.append(k)
            self.__ksl = ksl

    def __str__(self):
        def _repr(x):
            if x is self:
                return "UnSortedDict({...})"
            return repr(x)
        return ( "UnSortedDict({" + ", ".join([
                 "%r: %s" % (k, _repr(v)) for k, v in self.iteritems()])
                 + "})" )

    def __repr__(self):
        def _repr(x):
            if x is self:
                return "UnSortedDict({...})"
            return repr(x)
        return ( "UnSortedDict([" + ", ".join([
                 "(%r, %s)" % (k, _repr(v)) for k, v in self.iteritems()])
                 + "])" )

    def __setitem__(self, key, value):
        super(UnSortedDict, self).__setitem__(key, value)
        if key not in self.__ksl:
            self.__ksl.append(key)

    def __delitem__(self, key):
        if key in self.__ksl:
            self.__ksl.remove(key)
        super(UnSortedDict, self).__delitem__(key)

    def __iter__(self):
        length = len(self)
        for key in self.__ksl[:]:
            yield key
        if length != len(self):
            raise RuntimeError(ErrorSizeChanged)

    def keys(self):
        return self.__ksl[:]

    def iterkeys(self):
        return self.__iter__()

    def values(self):
        return [ self[k] for k in self.__ksl ]

    def itervalues(self):
        length = len(self)
        for key in self.__ksl[:]:
            yield self[key]
        if length != len(self):
            raise RuntimeError(ErrorSizeChanged)

    def items(self):
        return [ (k, self[k]) for k in self.__ksl ]

    def iteritems(self):
        length = len(self)
        for key in self.__ksl[:]:
            yield ( key, self[key] )
        if length != len(self):
            raise RuntimeError(ErrorSizeChanged)

    def clear(self):
        super(UnSortedDict, self).clear()
        self.__ksl = []

    def copy(self):
        return UnSortedDict(self)

    def pop(self, k, *default):
        if k in self.__ksl:
            self.__ksl.remove(k)
        return super(UnSortedDict, self).pop(k, *default)

    def popitem(self):
        item = super(UnSortedDict, self).popitem()
        try:
            self.__ksl.remove(item[0])
        except:
            raise ValueError("cannot remove", item, self.__ksl, self)
        return item

UnSortedDict.__metaClass__ = staticmethod(CopyBaseClassDocs)

#重写ConfigParser类，如果不重写，则所有option的关键字自动变为小写
class ConfigParserNew(ConfigParser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

#文件校验类
class FileModifyChecker(object):
    def __init__(self, fileName):
        self.fileName = fileName
        self.hashValue = self.__getHash()

    def __getHash(self):
        if not os.path.isfile(self.fileName):
            return []
        else:
            return [os.path.getatime(self.fileName), os.path.getctime(self.fileName), os.path.getmtime(self.fileName)]

    #文件已经修改过则返回True
    def isModified(self):
        currentHash = self.__getHash()
        if currentHash == self.hashValue:
            return False
        else:
            self.hashValue = currentHash
            return True

#ini文件操作封装类
class IniFile(object):
    def __init__(self, fileName):
        """
        1、如果文件不存在则不用管，在SetValue时会自动创建，否则读取其内容，避免覆盖
        2、为了简单保证并发操作安全，使用hash码进行校验，这样可以保证内存值和文件的同步，但是不保证多线程安全
        """
        self.fileName = fileName
        if self.fileName is None:
            assert False, 'file name is None!'
        #if not os.path.isfile(self.fileName):
        #    assert False, 'file [%s] not exist!' % self.fileName
        self.cfg = ConfigParserNew()
        self.checker = FileModifyChecker(self.fileName)
        self.cfg.read(self.fileName)

    def __checkModify(self):
        #如果校验失败，说明文件有修改，则重新加载
        if self.checker.isModified():
            self.cfg.read(self.fileName)

    #回写类的操作需要在结尾调用
    def __write(self):
        self.cfg.write(open(self.fileName, 'w'))

    #获取值
    def GetValue(self, section, key, defVal=''):
        self.__checkModify()
        try:
            value = self.cfg.get(section, key)
        except:
            value = defVal
        return value

    #增加或者修改值
    def SetValue(self, section, key, value):
        self.__checkModify()
        if not self.HasSection(section):
            self.cfg.add_section(section)
        self.cfg.set(section, key, value)
        self.__write()
        return

    #删除一个选项
    def RemoveOption(self, section, key):
        self.__checkModify()
        result = False
        if self.HasOption(section, key):
            self.cfg.remove_option(section, key)
            self.__write()
            result = True
        return result

    #删除一个大项
    def RemoveSection(self, section):
        self.__checkModify()
        result = False
        if self.HasSection(section):
            self.cfg.remove_section(section)
            self.__write()
            result = True
        return result

    #判断是否有某小项
    def HasOption(self, section, key):
        self.__checkModify()
        return self.cfg.has_option(section, key)

    #判断是否有某类大项
    def HasSection(self, section):
        self.__checkModify()
        return self.cfg.has_section(section)

    #获取所有选项的大项
    def GetAllSections(self):
        self.__checkModify()
        return self.cfg.sections()

    #获取某大项的所小项
    def GetAllOptions(self, section):
        self.__checkModify()
        result = []
        if self.cfg.has_section(section):
            result = self.cfg.options(section)
        return result

    #获取某大项的所有小项和对应的值
    def GetAllItems(self, section):
        self.__checkModify()
        result = []
        if self.cfg.has_section(section):
            result = self.cfg.items(section)
        return result

#文本文件常用操作封装类
class TextFile(object):
    MODE_STRING = 1
    MODE_PROPERTY = 2

    def __init__(self, mode=MODE_PROPERTY, ignoreBlankLine=False, trimRight = False, encoding=None):
        self.isLoaded = False
        self.fileHandle = None
        self.strIgnore = [';', '#']
        self.strCont = []
        self.propCont = UnSortedDict()
        self.mode = mode
        self.ignoreBlankLine = ignoreBlankLine
        self.trimRight = trimRight
        self.encoding = encoding
        self.noneKey = 'nullKey'

    #判断是否要跳过某行
    def __ignore(self, line):
        if line is None:
            return True
        tmp = line.lstrip()
        #空行跳过
        if tmp == '':
            return self.ignoreBlankLine

        #遇到注释符也跳过
        for char in self.strIgnore:
            if tmp.startswith(char):
                return True

        return False

    #格式化行
    def __format(self, cont):
        if cont is None:
            return cont

        if cont.endswith('\n'):
            newCont = cont[:-1]
        else:
            newCont = cont

        if self.trimRight:
            return newCont.rstrip()
        else:
            return newCont

    #用生成的随机值作为关键字来保存注释和空行信息
    def __randomKey(self):
        #return '%s_%.8f' % (self.noneKey, random.random())
        return '%s_%s' % (self.noneKey, ''.join(random.sample(string.ascii_letters+string.digits, 6)))

    def __appendProperty(self, line):
        newLine = self.__format(line)
        splitPos = newLine.find('=')
        if splitPos > 0 and line.strip() != '':
            proName = newLine[:splitPos].lstrip()
            proValue = newLine[splitPos + 1:].lstrip()
            proName = proName.rstrip()
            if self.trimRight:
                proValue = proValue.rstrip()
            self.propCont[proName] = proValue
        else:
            self.propCont[self.__randomKey()] = self.__format(line)

    #读取文件到内存
    def __read(self):
        self.strCont = []
        self.propCont.clear()
        for line in self.fileHandle.readlines():
            if not self.__ignore(line):
                if self.mode == TextFile.MODE_STRING:
                    self.strCont.append(self.__format(line))
                elif self.mode == TextFile.MODE_PROPERTY:
                    self.__appendProperty(line)
                else:
                    assert False, 'mode is not right.'

    #加载文件到内存
    def loadFile(self, fileName):
        if not self.isLoaded:
            if os.path.isfile(fileName):
                self.fileName = fileName
                if self.encoding is not None:
                    self.fileHandle = codecs.open(self.fileName, 'r', self.encoding)
                else:
                    self.fileHandle = codecs.open(self.fileName, 'r')
                self.__read()
                self.isLoaded = True
        return self.isLoaded

    #文本过滤
    #keyWord:关键字，支持字符串和容器等
    #bKeep：为True表示符合条件的才保留，为False表示符合条件的删除掉，默认为False
    def filterText(self, keyWord, bKeep=False):
        if (not self.isLoaded) or keyWord is None or self.mode != TextFile.MODE_STRING:
            return
        keyType = type(keyWord).__name__
        if keyType == 'str':
            if keyWord.strip() != '':
                if bKeep:
                    self.setContent([x for x in self.getContent() if x is not None and x.find(keyWord) != -1])
                else:
                    self.setContent([x for x in self.getContent() if x is not None and x.find(keyWord) == -1])
        elif keyType in ['int', 'float']:
            self.filterText(str(keyWord), bKeep)
        elif keyType in ['list', 'set', 'tuple']:
            for word in keyWord:
                self.filterText(word, bKeep)
        elif keyType == 'dict':
            for key in keyWord:
                self.filterText(keyWord.get(key), bKeep)
        elif keyType == 'NoneType':
            pass
        return

    #释放句柄
    def release(self):
        if self.fileHandle is not None:
            self.fileHandle.close()
            self.fileHandle = None

    #保存文件
    def saveFile(self, fileName='', addBlank = True):
        result = False
        if self.isLoaded:
            if fileName != '':
                self.fileName = fileName
            self.release()
            if self.encoding is not None:
                self.fileHandle = codecs.open(self.fileName, 'w', self.encoding)
            else:
                self.fileHandle = codecs.open(self.fileName, 'w')
            if self.mode == TextFile.MODE_STRING:
                for line in self.strCont:
                    self.fileHandle.write(line + '\n')
                result = True
            elif self.mode == TextFile.MODE_PROPERTY:
                for pro, val in self.propCont.items():
                    if pro is None or val is None:
                        continue
                    if pro.startswith(self.noneKey):
                        self.fileHandle.write(val + '\n')
                    else:
                        if addBlank:
                            self.fileHandle.write(pro + ' = ' + val + '\n')
                        else:
                            self.fileHandle.write(pro + '=' + val + '\n')
                result = True
            else:
                pass
            self.release()
            self.isLoaded = False
        return result

    #获取内容
    def getContent(self):
        if not self.isLoaded:
            return None
        if self.mode == TextFile.MODE_STRING:
            return self.strCont
        elif self.mode == TextFile.MODE_PROPERTY:
            return self.propCont
        else:
            return None

    #设置内容
    def setContent(self, cont):
        if not self.isLoaded:
            return False
        result = False
        if cont is not None:
            if self.mode == TextFile.MODE_STRING:
                self.strCont = cont
                result = True
            elif self.mode == TextFile.MODE_PROPERTY:
                self.propCont = cont
                result = True
            else:
                pass
        return result

    #获取某个属性
    def getProperty(self, proName, defVal=''):
        if not self.isLoaded:
            return None
        tmp = proName.strip()
        if tmp != '':
            if self.mode == TextFile.MODE_PROPERTY:
                return self.propCont.get(proName, defVal)
            else:
                return None
        return None

    #修改某个属性
    def setProperty(self, proName, value):
        if not self.isLoaded:
            return False
        result = False
        pn = proName.strip()
        val = value.strip()
        if pn != '':
            if self.mode == TextFile.MODE_PROPERTY:
                self.propCont[pn] = val
                result = True
            else:
                pass
        return result

    #删除属性
    def removeProperty(self, proName):
        if not self.isLoaded:
            return False
        result = False
        tmp = proName.strip()
        if tmp != '':
            if self.mode == TextFile.MODE_PROPERTY:
                self.propCont.pop(tmp)
                result = True
            else:
                pass
        return result

    #添加注释标记
    def addIgnoreChar(self, ignoreChar):
        if not self.isLoaded:
            return False
        result = False
        if ignoreChar != '':
            self.strIgnore.append(ignoreChar)
            result = True
        return result

    #删除注释标记
    def removeIgnoreChar(self, ignoreChar=''):
        if ignoreChar == '':
            self.strIgnore = []
        else:
            self.strIgnore.remove(ignoreChar)

    #获取注释标记内容
    def getIgnoreChars(self):
        return self.strIgnore

class StringTool(object):
    def __init__(self, strCont):
        self.strCont = strCont

    def ToLower(self):
        if not self.strCont is None:
            return str.lower(self.strCont)
        else:
            return ''

    def ToUpper(self, ):
        if not self.strCont is None:
            return str.upper(self.strCont)
        else:
            return ''

    def TrimLeft(self):
        if not self.strCont is None:
            return str.lstrip(self.strCont)
        else:
            return ''

    def TrimRight(self):
        if not self.strCont is None:
            return str.rstrip(self.strCont)
        else:
            return ''

    def Trim(self):
        if not self.strCont is None:
            return str.strip(self.strCont)
        else:
            return ''

    def GetNumber(self):
        val = None
        try:
            val = int(self.strCont)
        except:
            try:
                val = float(self.strCont)
            except:
                pass
        return val

#升级常用操作封装类
class Utility(object):
    def __init__(self, parent, bConsole=False):
        self.parent = parent
        self.lc = bConsole
        self.ver_exp = r'^V\d{3}R\d{3}C\d{2}(SPC\d{3}T?)?$'
        self.key_exp = r'^\d{5}$'
        self.bak_exp = r'^\d{3}_Bak\w+.py$'
        self.rec_exp = r'^\d{3}_Re\w+.py$'
        self.trd_exp = r'^\d{3}_Trd\w+.py$'
        self.maxLogSize = 1024 * 1024 * 2  # 日志阈值为2M，大于这个值则另起一个日志
        self.__initOther()
        self.sLen = 3  # 脚本的用于排序的数字部分的长度
        self.cLen = len('V300R008C00SPC')  # C版本带SPC的字符串长度

    def __initOther(self):
        #单板上的路径固定死了，专用于升级
        self.op = None
        self.logfile = ''
        if self.IsLinux():
            self.op = IniFile(os.path.join(self.__ensureDir('/opt/MDXUpgrade/FrameWork/OM/Patch/Data/'), 'patchdata.ini'))
            if not self.op.HasSection('version_patch_table'):
                self.op.SetValue('version_patch_table', 'V300R008C00SPC100', 'V300R008C00SPC113')
                self.op.SetValue('version_patch_table', 'V300R008C01SPC100', 'V300R008C01SPC108')
            self.logfile = os.path.join(self.__ensureDir('/opt/MDXUpgrade/FrameWork/Log/'), 'upg.log')
            self.upgEnvFiles = ['/etc/upg.profile']
        elif self.IsWindows():
            self.op = IniFile(r'f:\upg.ini')
            self.logfile = 'f:\upg.log'
            self.upgEnvFiles = ['f:\upg.profile']
        else:
            raise AssertionError, 'platform not support!'

        self.Assert(self.op is not None, 'cant not get operator!')
        self.Assert(self.logfile != '', 'cant not get logfile!')
        self.__initlog()

    def __initlog(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt=' %m-%d %H:%M',
                            filename=self.logfile,
                            filemode='a')

        if self.lc:
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
        self.logger = logging.getLogger(os.path.basename(self.parent))
        self.__checkLogFile()
        self.LogInfo('>>' + self.__getCurrentTime() + '@[' + self.parent + ']<<')

    def __ensureDir(self, dirName):
        if not os.path.isdir(dirName):
            os.makedirs(dirName)
        return dirName

    def __getCurrentTime(self):
        return str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))

    def IsWindows(self):
        return self.MatchRule(r'^win\w*$', sys.platform) is not None

    def IsLinux(self):
        return self.MatchRule(r'^linux\w*$', sys.platform) is not None

    #根据环境变量和文件名组装全路径，允许文件名为空
    def GetFilePathByEnv(self, env, fileName):
        tmp = fileName
        envVal = StringTool(self.GetUpgEnv(env)).Trim()
        if envVal == '':
            return tmp
        if tmp.startswith(os.sep):
            tmp = tmp[1:]
        target = os.path.join(envVal, tmp)
        return target

    def __checkLogFile(self):
        if os.path.isfile(self.logfile):
            if os.path.getsize(self.logfile) > self.maxLogSize:
                shutil.copy(self.logfile, self.logfile + '_' + self.__getCurrentTime())
                f = open(self.logfile, 'w')
                f.close()

    def __checkParam(self, version, key):
        return self.CheckVersion(version) and self.CheckKey(key) is not None

    def MatchRule(self, rule, value):
        return re.match(rule, value)

    def CheckKey(self, key):
        return self.MatchRule(self.key_exp, key) is not None

    def CheckVersion(self, version):
        return self.MatchRule(self.ver_exp, version) is not None

    #判断是否是合法的补丁备份脚本
    def MatchBackupScript(self, scriptName):
        return self.MatchRule(self.bak_exp, os.path.basename(scriptName)) is not None

    #判断是否是合法的补丁数据还原脚本
    def MatchRecoverScript(self, scriptName):
        return self.MatchRule(self.rec_exp, os.path.basename(scriptName)) is not None

    #判断是否是合法的补丁第三方脚本
    def MatchThirdScript(self, scriptName):
        return self.MatchRule(self.trd_exp, os.path.basename(scriptName)) is not None

    #版本匹配，传入GA版本，匹配其补丁版本
    def MatchVersion(self, lowVer=''):
        bMatch = False
        lastVer = self.op.GetValue('version_patch_table', lowVer, 'null')
        if lastVer != 'null':
            bMatch = True
        else:
            lastVer = lowVer
        return bMatch, lastVer

    #添加备份数据
    def AddBackupInfo(self, version, key, value):
        result = False
        ver = StringTool(version).ToUpper()
        k = StringTool(key).ToUpper()
        if self.__checkParam(ver, k):
            self.op.SetValue(ver, k, value)
            result = True
        else:
            self.LogError('AddBackupInfo fail cause[invalid value],version = [' + version + '], key = [' + key + ']')
        return result

    #获取备份数据
    def GetBackupInfo(self, version, key):
        result = ''
        ver = StringTool(version).ToUpper()
        k = StringTool(key).ToUpper()
        if self.__checkParam(ver, k):
            result = self.op.GetValue(ver, k)
        else:
            self.LogError('GetBackupInfo fail cause[invalid value],version = [' + version + '], key = [' + key + ']')
        return result

    #删除备份数据
    def DelBackupInfo(self, version, key):
        result = False
        ver = StringTool(version).ToUpper()
        k = StringTool(key).ToUpper()
        if self.__checkParam(ver, k):
            result = self.op.RemoveOption(ver, k)
        else:
            self.LogError('DelBackupInfo fail cause[invalid value],version = [' + version + '], key = [' + key + ']')
        return result

    #打印info级别日志
    def LogInfo(self, content):
        if content is None:
            self.logger.info('None')
            return
        self.__checkLogFile()
        self.logger.info(content)

    #批量打印info级别日志
    def LogInfos(self, contents):
        if contents is None:
            self.LogInfo('None')
            return
        for content in contents:
            self.LogInfo(content)

    #打印error级别日志
    def LogError(self, content):
        if content is None:
            self.logger.error('None')
            return
        self.__checkLogFile()
        self.logger.error(content)

    #批量打印error级别日志
    def LogErrors(self, contents):
        if contents is None:
            self.LogError('None')
            return
        for content in contents:
            self.LogError(content)

    #执行命令并捕获标注输出和标准错误信息返回
    def __exec(self, executeCmd):
        result = []
        execInfo = []
        pipe_in, pipe_out_and_error = os.popen4(executeCmd)
        try:
            execInfo = pipe_out_and_error.readlines()
        except:
            self.LogError('exec [' + executeCmd + '] error!')
        pipe_in.close()
        pipe_out_and_error.close()
        for info in execInfo:
            tmp = StringTool(info).TrimRight()
            if tmp.endswith('\n'):
                tmp = tmp[:len(tmp) - 1]
            if tmp != '':
                result.append(tmp)
        return result

    #执行系统命令
    def ExecuteSystemCommand(self, cmd):
        return self.__exec(cmd)

    #调用python脚本
    def ExecutePythonScript(self, script):
        return self.__exec('python ' + script)

    #获取升级环境变量
    def GetUpgEnv(self, keyword):
        #将关键字转成字符串
        kw = str(keyword)
        if StringTool(kw).Trim() == '':
            return ''
            #先查询系统环境变量，如果查不到再使用文件查询
        sysEnvVal = str(os.environ.get(kw))
        if StringTool(sysEnvVal).Trim() != 'None':
            return sysEnvVal
        else:
            for fileName in self.upgEnvFiles:
                f = TextFile(TextFile.MODE_STRING)
                f.loadFile(fileName)
                for cont in f.getContent():
                    if cont.find(kw) != -1 and cont.find('=') > 0:
                        return StringTool(cont.split('=')[1]).Trim()
            return ''

    #断言，如果断言失败则程序退出
    def Assert(self, bTrue, info=''):
        if not bTrue and info != '':
            self.LogError(info)
        assert bTrue, info

    #判断文件是否存在
    def ExistFile(self, filePath):
        return os.path.isfile(filePath)

    #判断文件夹是否存在
    def ExistDir(self, dirPath):
        return os.path.isdir(dirPath)

    #遍历目录
    def WalkDir(self, dirName):
        fileList = []
        if os.path.isdir(dirName):
            for root,dirs,files in os.walk(dirName):
                for f in files:
                    fileList.append(os.path.join(root, f))
        return fileList

#xml文件操作封装类
class XmlTool(object):
    def __init__(self, fileName='', encode='utf-8'):
        self.xmlFile = fileName
        self.myEncode = encode
        if self.xmlFile != '':
            if not self.readXmlFile(self.xmlFile):
                assert False, "can't read this file[%s]!" % self.xmlFile
    
    def setEncoding(self, encode):
        self.myEncode = encode
    
    def newXml(self, fileName = ''):
        emptyXmlStr = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<root></root>"
        self.xmlFile = fileName
        return self.readXmlString(emptyXmlStr)

    #从字符串解析
    def readXmlString(self, data):
        self.dom = minidom.parseString(data)
        self.root = self.dom.firstChild
        return self.dom is not None

    #从文件构造
    def readXmlFile(self, fp):
        self.xmlFile = fp
        if not os.path.isfile(self.xmlFile):
            return False
        #由于minidom仅支持utf-8和utf-16，所以，需要对其他编码做一下处理
        try:
            self.dom = minidom.parse(self.xmlFile)
            self.root = self.dom.firstChild
        except ExpatError:
            xmlFile = codecs.open(fp)
            text = xmlFile.read()
            arrayInfo = text.split('?')
            if len(arrayInfo) > 2:
                encodeInfo = arrayInfo[1]
                text = text.replace(encodeInfo, 'xml version="1.0" encoding="utf-8"')
                xmlFile.close()
                try:
                    self.readXmlString(text)
                except ExpatError:
                    try:
                        text = unicode(text, encoding='GBK').encode('utf-8')
                    except UnicodeDecodeError:
                        #如果用unicode读取还出错，不再尝试，直接报错
                        assert False, "can't read this file[%s]!" % fp
                    self.readXmlString(text)
            else:
                #如果没有编码信息，不再尝试，直接报错
                assert False, "can't read this file[%s]!" % fp
        return self.dom is not None

    #写入到文件
    def writeXmlFile(self, fileName='', encodingNewLine=True):
        targetFile = fileName
        if targetFile == '':
            targetFile = self.xmlFile
        f = codecs.open(targetFile, 'w')
        writer = codecs.getwriter(self.myEncode)(f)
        self.dom.writexml(writer, encoding=self.myEncode)
        f.close()
        #默认会处理编码行与其他节点行之间不会换行的问题
        if encodingNewLine:
            #1、先按照文本读取一下内容
            fRead = codecs.open(targetFile, 'r', self.myEncode)
            text = fRead.read()
            fRead.close()
            #2、做换行处理
            text = text.replace("?><", "?>\n<")
            if self.dom.standalone is not None:
                if self.dom.standalone:
                    text = text.replace("?>\n<", " standalone=\"yes\"?>\n<")
                else:
                    text = text.replace("?>\n<", " standalone=\"no\"?>\n<")
            #3、重新写回去
            fWrite = codecs.open(targetFile, 'w', self.myEncode)
            fWrite.write(text)
            fWrite.close()

    #获取文本
    def getXmlText(self, formatFile=False):
        if formatFile:
            return self.dom.toprettyxml(encoding=self.myEncode)
        else:
            return self.dom.toxml(self.myEncode)

    #获取root节点，为xml.dom.Node
    def __getRootElement(self):
        return self.root

    #获取XmlNode类型的root节点
    def getRootNode(self):
        return XmlTool.XmlNode(self.__getRootElement())

    #数据越界的异常
    class ChildIndexOutOfBoundsException(Exception):
        pass

    #xml节点类
    class XmlNode:
        def __init__(self, elem):
            self.elem = elem

        #私有方法，获取一个文字节点
        def __getTextNode(self, text):
            tmpNode = minidom.Text()
            tmpNode.data = text
            tmpNode.ownerDocument = self.elem.ownerDocument
            return XmlTool.XmlNode(tmpNode)

        #私有方法，根据名字，获取一个新节点
        def __getElementNode(self, name):
            element = minidom.Element(name)
            element.ownerDocument = self.elem.ownerDocument
            return XmlTool.XmlNode(element)

        #获取节点名
        def getName(self):
            return self.elem.nodeName

        #获取节点值
        def getValue(self):
            if self.elem.childNodes.length == 0:
                return ""
            elif self.elem.childNodes.length == 1:
                return self.elem.firstChild.nodeValue
            else:
                return None

        #修改节点值
        def setValue(self, value):
            if self.elem.childNodes.length == 0:
                self.elem.appendChild(self.__getTextNode(value).elem)
                result = True
            elif self.elem.childNodes.length == 1:
                self.elem.firstChild.nodeValue = value
                result = True
            else:
                assert False, 'the node is not allow to set value!'
            return result

        #克隆节点
        def clone(self, deep=True):
            return XmlTool.XmlNode(self.elem.cloneNode(deep))

        #获取节点的字符串
        def getXmlText(self, formatFile=False):
            if formatFile:
                return self.elem.toprettyxml()
            else:
                return self.elem.toxml()

        #获取下一个兄弟节点
        def getNextSiblingNode(self):
            node = self.elem.nextSibling
            if node is not None:
                return XmlTool.XmlNode(node)
            else:
                return None

        #根据id获取子节点
        def getChildByIndex(self, index):
            children = self.elem.childNodes
            children_elem = []
            for child in children:
                if child.nodeType == minidom.Node.ELEMENT_NODE:
                    children_elem.append(child)
            if index > len(children_elem):
                raise XmlTool.ChildIndexOutOfBoundsException
            return XmlTool.XmlNode(children_elem[index])

        #根据名字获取子节点
        def getChildByName(self, name):
            children = self.elem.childNodes
            for child in children:
                if child.nodeType == minidom.Node.ELEMENT_NODE:
                    if child.nodeName == name:
                        return XmlTool.XmlNode(child)
            return None

        #获取所有的同名同级节点
        def getChildsByName(self, name):
            children = self.elem.childNodes
            children_elem = []
            for child in children:
                if child.nodeType == minidom.Node.ELEMENT_NODE:
                    if child.nodeName == name:
                        children_elem.append(XmlTool.XmlNode(child))
            return children_elem

        #私有方法，检查节点是否包含某属性，如果属性为空则直接返回成功
        def __checkNodeAttribute(self, node, attrName, attrValue):
            if attrName == '':
                return True
            if node is not None:
                attribute = node.getAttributeByName(attrName)
                if attribute is not None and attribute.getValue() == attrValue:
                    return True
            return False

        #根据属性值获取子节点,最多支持三个属性的查询
        def getChildByNameAndAttribute(self, name, attrName1, attrValue1, attrName2='',
                                       attrValue2='', attrName3='', attrValue3=''):
            if attrValue1 != '':
                nodes = self.getChildsByName(name)
                for node in nodes:
                    if self.__checkNodeAttribute(node, attrName1, attrValue1) and \
                            self.__checkNodeAttribute(node, attrName2, attrValue2) and \
                            self.__checkNodeAttribute(node, attrName3, attrValue3):
                        return node
            return None

        #根据名字追加子节点
        def appendChildByName(self, name, beforeFormat='', afterFormat=''):
            node = self.__getElementNode(name)
            self.appendChildByNode(node, beforeFormat, afterFormat)
            return node

        #追加一个XmlNode类型的子节点
        def appendChildByNode(self, node, beforeFormat='', afterFormat=''):
            if beforeFormat != '':
                self.elem.appendChild(self.__getTextNode(beforeFormat).elem)
            result = self.elem.appendChild(node.elem)
            if afterFormat != '':
                self.elem.appendChild(self.__getTextNode(afterFormat).elem)
            return XmlTool.XmlNode(result)

        #根据节点名在特定节点前插入一个新的子节点
        def insertChildBeforeByName(self, name, refNode, beforeFormat='', afterFormat=''):
            return self.insertChildBeforeByNode(self.__getElementNode(name), refNode, beforeFormat, afterFormat)

        #在特定节点前插入一个新的XmlNode类型子节点
        def insertChildBeforeByNode(self, newNode, refNode, beforeFormat='', afterFormat=''):
            if beforeFormat != '':
                self.elem.insertBefore(self.__getTextNode(beforeFormat).elem, refNode.elem)
            result = self.elem.insertBefore(newNode.elem, refNode.elem)
            if afterFormat != '':
                self.elem.insertBefore(self.__getTextNode(afterFormat).elem, refNode.elem)
            return XmlTool.XmlNode(result)

        #根据名字删除子节点
        def removeChildByName(self, name):
            result = False
            node = self.getChildByName(name)
            if node is not None:
                self.elem.removeChild(node.elem)
                result = True
            return result

        #根据名字以及属性删除子节点，最多支持三个属性的匹配
        def removeChildByNameAndAttribute(self, name, attrName1, attrValue1, attrName2='',
                                          attrValue2='', attrName3='', attrValue3=''):
            result = False
            try:
                if attrValue1 != '':
                    node = self.getChildByNameAndAttribute(name, attrName1, attrValue1,
                                                           attrName2, attrValue2, attrName3, attrValue3)
                    if node is not None:
                        self.elem.removeChild(node.elem)
                        result = True
            except:
                pass
            return result

        #删除某节点
        def removeChildByNode(self, node):
            bakNode = None
            try:
                bakNode = self.elem.removeChild(node.elem)
            except:
                pass
            return bakNode is not None

        #根据id删除子节点
        def removeChildByIndex(self, name):
            return self.removeChildByNode(self.getChildByIndex(name))

        #获取子节点的个数
        def getChildCount(self):
            return len(self.getChildList())

        #获取所有子节点
        def getChildList(self, includeTextNode=False):
            children = self.elem.childNodes
            childList = []
            for child in children:
                if child.nodeType == minidom.Node.ELEMENT_NODE or \
                                        includeTextNode == True and child.nodeType == minidom.Node.TEXT_NODE:
                    childList.append(XmlTool.XmlNode(child))
            return childList

        #根据id获取节点的属性
        def getAttributeByIndex(self, index):
            attributes = self.elem.attributes
            keys = attributes.keys()
            if index > len(keys):
                raise XmlTool.ChildIndexOutOfBoundsException
            return XmlTool.Attribute(attributes.getNamedItem(keys[index]))

        #根据名字获取节点的属性
        def getAttributeByName(self, name):
            attributes = self.elem.attributes
            keys = attributes.keys()
            for each in keys:
                if each == name:
                    return XmlTool.Attribute(attributes.getNamedItem(name))
            return None

        #根据id删除属性
        def removeAttributeByIndex(self, index):
            result = False
            attr = self.getAttributeByIndex(index)
            if (self.getAttributeByIndex(index)) is not None:
                result = self.removeAttributeByName(attr.getName())
            return result

        #根据名字删除属性
        def removeAttributeByName(self, name):
            if self.getAttributeByName(name) is not None:
                self.elem.removeAttribute(name)
                return True
            else:
                return False

        #添加一个属性
        def addAttribute(self, name, value=''):
            if self.getAttributeByName(name) is None:
                attr = minidom.Attr(name)
                d = attr.__dict__
                d["value"] = d["nodeValue"] = value
                d["ownerDocument"] = self.elem.ownerDocument
                self.elem.setAttributeNode(attr)
                return XmlTool.Attribute(attr)
            else:
                return None

        #获取属性的个数
        def getAttribCount(self):
            return len(self.getAttributeList())

        #获取所有属性
        def getAttributeList(self):
            attributes = self.elem.attributes
            attrList = []
            keys = attributes.keys()
            for key in keys:
                attrList.append(XmlTool.Attribute(attributes.getNamedItem(key)))
            return attrList

    #节点的属性类
    class Attribute:
        def __init__(self, attr):
            self.attr = attr

        #获取属性名
        def getName(self):
            return self.attr.name

        #获取属性值
        def getValue(self):
            return self.attr.value

        #修改属性值
        def setValue(self, value):
            if value is not None and value != '':
                self.attr.value = value
                return True
            else:
                return False


class MMLTool(object):
    def __init__(self, xmlFile):
        self.xml = XmlTool(xmlFile)
        self.root = self.xml.getRootNode()
        self.currentNode = None

    def save(self, targetXml=''):
        self.xml.writeXmlFile(targetXml)

    def __makeParam(self, pName, pValue):
        if self.currentNode is None:
            return False
        else:
            self.currentNode.addAttribute('name', pName)
            self.currentNode.addAttribute('value', pValue)
            return True

    def __getParamNode(self, pName):
        self.currentNode = self.root.getChildByNameAndAttribute('parameter', 'name', pName)
        return self.currentNode

    def __getValue(self):
        return self.currentNode.getAttributeByName('value').getValue()

    def __setValue(self, pValue):
        if self.currentNode is None:
            return False
        else:
            return self.currentNode.getAttributeByName('value').setValue(pValue)

    def insertParamBefore(self, flagName, paramName, paramValue):
        flagNode = self.__getParamNode(flagName)
        if flagNode is None:
            return False
        else:
            self.currentNode = self.root.insertChildBeforeByName('parameter', flagNode, '\n  ', '\n  ')
            return self.__makeParam(paramName, paramValue)

    def appendParam(self, paramName, paramValue):
        self.currentNode = self.root.appendChildByName('parameter', '  ', '\n')
        return self.__makeParam(paramName, paramValue)

    def deleteParam(self, paramName, paramValue=''):
        if paramValue in [None, '']:
            self.root.removeChildByNameAndAttribute('parameter', 'name', paramName)
        else:
            self.root.removeChildByNameAndAttribute('parameter', 'name', paramName, 'value', paramValue)

    def updateParam(self, paramName, paramValue, skipParamValue=''):
        self.__getParamNode(paramName)
        if skipParamValue in [None, ''] or self.__getValue() != skipParamValue:
            return self.__setValue(paramValue)
        else:
            return False

    def getParamValue(self, paramName, defVal=None):
        self.__getParamNode(paramName)
        if self.currentNode is not None:
            return self.__getValue()
        else:
            return defVal

    def getXmlText(self):
        return self.root.getXmlText().encode('utf-8')
