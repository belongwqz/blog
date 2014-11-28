# -*- coding: utf-8 -*-
import os
import re
import gc
import math
import codecs
import traceback
import cPickle
import xlwt
import xlrd
import csv
import logging
import pythoncom
import win32com.client
from zipfile import ZipFile, is_zipfile, ZIP_DEFLATED
from datetime import datetime, date, time
from threading import Thread
from xml.dom import minidom
from pyexpat import ExpatError
from win32event import CreateMutex
from win32api import CloseHandle, GetLastError
from winerror import ERROR_ALREADY_EXISTS
from resource import Data, ReportStyle, LanRes
from PySide.QtCore import Signal, QObject


def autoCode(cont):
    us = cont
    if isinstance(cont, basestring):
        try:
            us = cont.decode('utf-8')
        except:
            us = cont.decode('gbk')
    return us


def autoStr(cont):
    try:
        val = str(cont)
    except:
        val = unicode(cont)
    return val


class singleInstance:
    """ Limits application to single instance """

    def __init__(self):
        self.mutexName = "reportTool_single_instance"
        self.mutex = CreateMutex(None, False, self.mutexName)
        self.lasterror = GetLastError()

    def alreadyRunning(self):
        return self.lasterror == ERROR_ALREADY_EXISTS

    def __del__(self):
        if self.mutex:
            CloseHandle(self.mutex)


def processNum(process_name):
    processCodeCov = []
    try:
        WMI = win32com.client.GetObject('winmgmts:')
        processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % process_name)
    except:
        pass
    return len(processCodeCov)


def KeyByName(nameVal, dataType):
    """
    根据需要获取字段名，入参可以是整形或者字符串的数字
    """
    for info in Data.Info[dataType][Data.struct]:
        if info.endswith(nameVal):
            return info
    return None


def KeyByIndex(index, dataType):
    """
    根据需要获取字段名，入参可以是整形或者字符串的数字
    """
    for k, v in Data.Info[dataType][Data.struct].items():
        if str(v[1]) == str(index):
            return k
    return None


class XmlTool(object):
    """
    xml文件操作封装类

    实现了python对xml文件基本操作的封装
    """

    def __init__(self, fileName='', encode='utf-8'):
        self.xmlFile = fileName
        self.myEncode = encode
        if self.xmlFile != '':
            if not self.readXmlFile(self.xmlFile):
                assert False, "can't read this file[%s]!" % self.xmlFile

    def setEncoding(self, encode):
        self.myEncode = encode

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
        def getChildList(self):
            children = self.elem.childNodes
            childList = []
            for child in children:
                if child.nodeType == minidom.Node.ELEMENT_NODE:
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


class ExcelImpl(object):
    """
    excel的操作实现

    区分两种方法，一种是xlwt的方法，一种是使用com接口。
    小数据量时建议使用xlwt，速度较快，此方法必须保存为exce2003格式（最大列为254，最大行为65535）
    大数据量时由于xlwt占用内存过大，所以建议用com接口方式，保存为excel2007以上格式，可以存放更大的数据，但是速度较慢
    """

    def __init__(self, fileName, useCom=False):
        self.__workBook = None
        self.__useCom = useCom
        self.__fileName = fileName
        self.__workApp = None
        self.__sheets = {}
        self.__firstSheet = None
        if self.__useCom:
            try:
                pythoncom.CoInitialize()
                self.__workApp = win32com.client.Dispatch('Excel.Application')
                #self.__workApp.Visible = False
                self.__workBook = self.__workApp.Workbooks.Add()
            except:
                self.__useCom = False
                self.__workBook = xlwt.Workbook(style_compression=2)
                self.__fileName = self.__fileName.replace('.xlsx', '.xls')
        else:
            self.__workBook = xlwt.Workbook(style_compression=2)

    def isComMode(self):
        return self.__useCom

    def addSheets(self, sheetNameList):
        for sheetName in sheetNameList:
            if self.__firstSheet is None:
                self.__firstSheet = sheetName
            if self.__useCom:
                self.__workBook.Sheets.Add(Before=self.__workBook.Sheets(self.__workBook.Sheets.Count)).Name = sheetName
                self.__sheets[sheetName] = self.__workBook.Sheets[sheetName]
            else:
                self.__sheets[sheetName] = self.__workBook.add_sheet(sheetName, True)
        #删除excel的三个默认页签
        if self.__useCom:
            self.__workBook.Sheets['Sheet1'].Delete()
            self.__workBook.Sheets['Sheet2'].Delete()
            self.__workBook.Sheets['Sheet3'].Delete()

    #只对使用com接口时生效
    def selectFirstSheet(self):
        if self.__useCom and self.__firstSheet is not None:
            self.__workBook.Sheets[self.__firstSheet].Select()

    def getSheet(self, sheetName):
        return ExcelImpl.ExcelSheet(sheetName, self.__sheets, self.__useCom)

    def save(self):
        if self.__useCom:
            var = self.__workBook.Sheets[1].Select
            self.__workBook.SaveAs(self.__fileName)
            self.__workBook.Close(SaveChanges=0)
            self.__workApp.Quit()
        else:
            self.__workBook.save(self.__fileName)
            del self.__workBook

    class ExcelSheet(object):
        class RangeData(object):
            def __init__(self, colLeft, rowTop, colRight, rowBottom):
                self.colLeft = colLeft
                self.rowTop = rowTop
                self.colRight = colRight
                self.rowBottom = rowBottom
                self.data = []

            def release(self):
                del self.data[:]
                del self.data

            def addData(self, colLeft, rowTop, colRight, rowBottom, data):
                self.colLeft = min(self.colLeft, colLeft)
                self.rowTop = min(self.rowTop, rowTop)
                self.colRight = max(self.colRight, colRight)
                self.rowBottom = max(self.rowBottom, rowBottom)
                self.data.append(data)

            def getData(self):
                return self.data

            def count(self):
                return len(self.data)

        def __init__(self, sheetName, sheets, useCom):
            self.__useCom = useCom
            self.__sheets = sheets
            self.__sheetName = sheetName
            self.__sheet = self.__sheets.get(sheetName, None)
            self.__titleStyle = xlwt.easyxf(ReportStyle.TitleStyle)
            self.__contentStyle = xlwt.easyxf(ReportStyle.ContentStyle)
            self.__rangeData = ExcelImpl.ExcelSheet.RangeData(1, 1, 1, 1)
            self.__flushSize = 500

        def flush(self):
            if self.__useCom:
                cellLeftTop = self.__sheet.Cells(self.__rangeData.rowTop + 1, self.__rangeData.colLeft + 1)
                cellRightBottom = self.__sheet.Cells(self.__rangeData.rowBottom + 1, self.__rangeData.colRight + 1)
                sRange = self.__sheet.Range(cellLeftTop, cellRightBottom)
                sRange.Value2 = self.__rangeData.getData()
                newData = ExcelImpl.ExcelSheet.RangeData(self.__rangeData.colLeft, self.__rangeData.rowBottom + 1,
                                                         self.__rangeData.colRight, self.__rangeData.rowBottom)
                self.__rangeData.release()
                del self.__rangeData
                self.__rangeData = newData

        def getName(self):
            return self.__sheetName

        #引入这个方法是为了解决com接口写速度慢的问题，对于非com接口还是一样的效率
        def setRangeValue(self, rowIndex, colStartIndex, colLength, valueArray, releaseData=True):
            if colLength != len(valueArray):
                return False
            if self.__useCom:
                self.__rangeData.addData(colStartIndex, rowIndex, colLength - 1 + colStartIndex, rowIndex, valueArray)
                if self.__rangeData.count() >= self.__flushSize:
                    self.flush()
            else:
                for colIndex in range(colStartIndex, colStartIndex + colLength):
                    self.setCell(rowIndex, colIndex, valueArray[colIndex - colStartIndex])
                if releaseData:
                    del valueArray[:]
            return True

        def exist(self):
            return self.__sheet is not None

        def setCell(self, rowIndex, colIndex, value, isTitle=False):
            if self.__useCom:
                self.__sheet.Cells(rowIndex + 1, colIndex + 1).Value = value
            else:
                self.__sheet.write(rowIndex, colIndex, value, self.__titleStyle if isTitle else self.__contentStyle)

        def setCellFormula(self, rowIndex, colIndex, formula):
            if self.__useCom:
                self.__sheet.Cells(rowIndex + 1, colIndex + 1).FormulaR1C1 = '=' + formula
            else:
                self.__sheet.write(rowIndex, colIndex, xlwt.Formula(formula), self.__contentStyle)

        def setColWidth(self, colIndex, width):
            if self.__useCom:
                self.__sheet.Columns(colIndex + 1).ColumnWidth = width + 6
            else:
                self.__sheet.col(colIndex).width = 256 * (width + 6)

        def __rgb_to_hex(self, r, g, b):
            return int('%02x%02x%02x' % (r, g, b), 16)

        def setRangeStyle(self, rowIndex1, colIndex1, rowIndex2, colIndex2, isTitle=False):
            if self.__useCom:
                xlEdgeLeft = 7
                xlEdgeTop = 8
                xlEdgeBottom = 9
                xlEdgeRight = 10
                xlInsideVertical = 11
                xlInsideHorizontal = 12
                xlThin = 4 if isTitle else 2
                cellLeftTop = self.__sheet.Cells(rowIndex1 + 1, colIndex1 + 1)
                cellRightBottom = self.__sheet.Cells(rowIndex2 + 1, colIndex2 + 1)
                sRange = self.__sheet.Range(cellLeftTop, cellRightBottom)
                sRange.Borders(xlEdgeLeft).Weight = xlThin
                sRange.Borders(xlEdgeTop).Weight = xlThin
                sRange.Borders(xlEdgeBottom).Weight = xlThin
                sRange.Borders(xlEdgeRight).Weight = xlThin
                sRange.Borders(xlInsideVertical).Weight = xlThin
                sRange.Borders(xlInsideHorizontal).Weight = xlThin
                if isTitle:
                    sRange.Font.Bold = True
                    sRange.Font.Color = self.__rgb_to_hex(0, 0, 0)
                    sRange.Interior.Color = self.__rgb_to_hex(0, 255, 0)


class UIUpdate(QObject):
    """
    主要是使用QObject这个类来兼容QT的signal
    """
    msgSig = Signal(str)
    proSig = Signal(int)
    btnRunEnable = Signal(bool)


class ConfData(object):
    """
    会议数据结构

    用于描述数据的会议结构
    """

    def __init__(self, dataType):
        """
        构造会议数据

        数据会议包含大部分数据的信息，可扩展
        """
        super(ConfData, self).__init__()
        self.__struct = Data.Info[dataType][Data.struct]
        self.__data = {}
        for it in self.__struct:
            self.__data[it] = None

    def setData(self, key, val):
        if self.hasKey(key):
            self.__data[key] = self.getFieldVal(val, self.__struct[key][0])

    def setTypeData(self, key, data):
        if self.hasKey(key):
            self.__data[key] = data

    def getData(self, key, defVal=''):
        return self.__data.get(key, defVal)

    def hasKey(self, key):
        for it in self.__struct:
            if it == key:
                return True
        return False

    #根据字段的类型将字符串进行转换
    def getFieldVal(self, fieldStr, fieldType):
        if fieldStr is None or fieldType is None:
            return None
        if fieldType == 'int':
            try:
                result = int(fieldStr)
            except:
                result = None
        elif fieldType in ['str', 'attrib']:
            result = fieldStr
        elif fieldType == 'datetime':
            try:
                result = datetime.strptime(fieldStr, Data.DateTimeFormat)
            except ValueError:
                result = None
        else:
            result = None
        return result


class DataHolder(object):
    """
    数据集合

    包含若干个ConfData的集合
    """

    CanAction = True

    def __init__(self, dataType):
        super(DataHolder, self).__init__()
        self.__dataType = dataType
        self.__confDatas = []

    #采取分段读取的时候，没段数据使用完要及时释放内存
    def release(self):
        del self.__confDatas[:]

    #添加一个数据
    def addConfData(self, confData):
        self.__confDatas.append(confData)

    #返回读取到的数据个数，用于给界面回显百分比
    def count(self):
        return len(self.__confDatas)

    #数据过滤用，这里按照时间来过滤
    def checkDataForXmlType(self, dataInfo, startDate, endDate):
        confStartDate = dataInfo.getData(KeyByName('StartTime', self.__dataType), datetime.now())
        if confStartDate is None:
            return True
        newEndDate = datetime.combine(date(endDate.year, endDate.month, endDate.day), time(23, 59, 59))
        return startDate <= confStartDate <= newEndDate

    def checkDataForExcelType(self, dataStr, startDate, endDate):
        newEndDate = datetime.combine(date(endDate.year, endDate.month, endDate.day), time(23, 59, 59))
        dateInfo = datetime.strptime(dataStr, '%Y%m%d')
        return startDate <= dateInfo <= newEndDate, dateInfo.strftime(Data.DateTimeFormat)

    def getAll(self):
        return self.__confDatas

    def __ReadXml(self, fileObj, StartTime, EndTime):
        dataTool = XmlTool()
        dataTool.readXmlString(fileObj)
        rootNode = dataTool.getRootNode()
        tmpFlag = Data.Info[self.__dataType][Data.flag]
        tmpChildFlag = Data.Info[self.__dataType][Data.childFlag]
        tmpStruct = Data.Info[self.__dataType][Data.struct]
        if rootNode is not None:
            if self.__dataType == Data.HistoryTable:
                #如果只有单个节点，则root节点就是数据节点了
                if rootNode.getName() == tmpFlag:
                    confData = ConfData(self.__dataType)
                    for info in tmpStruct:
                        chileNode = rootNode.getChildByName(info)
                        confData.setData(info, None if chileNode is None else chileNode.getValue())
                    if self.checkDataForXmlType(confData, StartTime, EndTime):
                        self.addConfData(confData)
                else:
                    for node in rootNode.getChildsByName(tmpFlag):
                        confData = ConfData(self.__dataType)
                        for info in tmpStruct:
                            chileNode = node.getChildByName(info)
                            confData.setData(info, None if chileNode is None else chileNode.getValue())
                        if self.checkDataForXmlType(confData, StartTime, EndTime):
                            self.addConfData(confData)
            elif self.__dataType == Data.ScheduleTable:
                #如果只有单个节点，则root节点就是数据节点了
                if rootNode.getName() == tmpFlag:
                    confData = ConfData(self.__dataType)
                    for info in tmpStruct:
                        chileNode = rootNode.getChildByName(tmpChildFlag)
                        chileNode = None if chileNode is None else chileNode.getChildByName(info)
                        confData.setData(info, None if chileNode is None else chileNode.getValue())
                    if self.checkDataForXmlType(confData, StartTime, EndTime):
                        self.addConfData(confData)
                else:
                    for node in rootNode.getChildsByName(tmpFlag):
                        confData = ConfData(self.__dataType)
                        for info in tmpStruct:
                            chileNode = node.getChildByName(tmpChildFlag)
                            chileNode = None if chileNode is None else chileNode.getChildByName(info)
                            confData.setData(info, None if chileNode is None else chileNode.getValue())
                        if self.checkDataForXmlType(confData, StartTime, EndTime):
                            self.addConfData(confData)
            elif self.__dataType == Data.OnlineTable:
                #如果只有单个节点，则root节点就是数据节点了
                if rootNode.getName() == tmpFlag:
                    confData = ConfData(self.__dataType)
                    for info in tmpStruct:
                        chileNode = rootNode.getChildByName(info)
                        confData.setData(info, None if chileNode is None else chileNode.getValue())
                    if self.checkDataForXmlType(confData, StartTime, EndTime):
                        self.addConfData(confData)
                else:
                    for node in rootNode.getChildsByName(tmpFlag):
                        confData = ConfData(self.__dataType)
                        for info in tmpStruct:
                            chileNode = node.getChildByName(info)
                            confData.setData(info, None if chileNode is None else chileNode.getValue())
                        if self.checkDataForXmlType(confData, StartTime, EndTime):
                            self.addConfData(confData)
        #临时变量及时回收，这里可能回收不了，因为被其他地方引用其值，这里可看做申明
        del dataTool

    def __ReadUsersNumberTable(self, fileName, StartTime, EndTime):
        if self.__dataType == Data.UsersNumberTable:
            #这里默认excel为合法文件，如果为非法的数据，则自动抛异常给上层调用
            result, dateInfo = self.checkDataForExcelType(
                os.path.basename(fileName)[0:len('20130724')],
                StartTime,
                EndTime
            )
            if result:
                tableInfo = xlrd.open_workbook(fileName).sheet_by_index(0)
                for rowIndex in range(tableInfo.nrows):
                    if rowIndex > 0:
                        tmpStruct = Data.Info[self.__dataType][Data.struct]
                        confData = ConfData(self.__dataType)
                        for info in tmpStruct:
                            if info == 'DateField':
                                confData.setData(info, dateInfo)
                            else:
                                userData = tableInfo.cell(rowIndex, int(tmpStruct[info][1]) - 1).value
                                confData.setData(info, userData)
                        self.addConfData(confData)

    #渠道数据仅加载到内存，不加页签来显示
    def __ReadChannel(self, fileObj, fileName, StartTime, EndTime):
        result, dataInfo = self.checkDataForExcelType(
            fileName[-1 * len('20130724.zip'):][0:len('20130724')],
            StartTime, EndTime
        )
        if result:
            for line in csv.DictReader(fileObj):
                confData = ConfData(self.__dataType)
                for k, v in Data.Info[self.__dataType][Data.mapInfo].items():
                    for key in line.keys():
                        if k in key:
                            confData.setData(v, autoCode(line[key]))
                if confData.getData('TelNumber') != 'null':
                    self.addConfData(confData)

    def Read(self, fileName, StartTime, EndTime):
        if DataHolder.CanAction:
            DataHolder.CanAction = False
        if fileName.lower().endswith('.zip'):
            with ZipFile(fileName, 'r', ZIP_DEFLATED) as zipFile:
                for fName in zipFile.namelist():
                    if self.__dataType in [
                        Data.HistoryTable,
                        Data.ScheduleTable,
                        Data.OnlineTable,
                        Data.UsersNumberTable
                    ]:
                        self.__ReadXml(zipFile.read(fName), StartTime, EndTime)
                    elif self.__dataType in [Data.ChannelTable]:
                        self.__ReadChannel(zipFile.open(fName), fName, StartTime, EndTime)
        elif fileName.lower().endswith('.xls') or fileName.lower().endswith('.xlsx'):
            if self.__dataType == Data.UsersNumberTable:
                self.__ReadUsersNumberTable(fileName, StartTime, EndTime)
        DataHolder.CanAction = True


class ReportMaker(Thread):
    """
    生成报表的主类
    """
    CanAction = True

    def __init__(self, parent):
        super(ReportMaker, self).__init__()
        self.setDaemon(True)
        self.__dataHolders = {}
        self.__parent = parent
        self.__startDate = None
        self.__endDate = None
        self.__sourceDir = None
        self.__reportFilePath = None
        self.__workBook = None
        self.__supportTableList = [
            #顺序不能变，否则出问题
            Data.ChannelTable,
            Data.UsersNumberTable,
            Data.HistoryTable,
            Data.ScheduleTable,
            Data.OnlineTable,
            Data.UserDetailTable
        ]
        self.__fileList = {}
        for tableInfo in self.__supportTableList:
            self.__fileList[tableInfo] = []
        self.__fileCount = 0
        self.__readCount = 0
        self.__xlApp = None
        self.__xlBook = None
        self.__sheetNameList = []
        self.__excel = None
        self.__useCom = False
        self.signal = UIUpdate()
        self.__exportOrgData = True
        self.__beginTime = datetime.now()
        self.__logger = Logger()
        self.__logger.info('-----start a new task-----')

    def sendMsg(self, msg, log=False):
        if self.__parent is not None and msg is not None:
            self.signal.msgSig.emit(msg)
            if log:
                self.__logger.info(msg)

    def sendPercent(self, value):
        if self.__parent is not None and value is not None:
            try:
                intVal = int(math.ceil(value))
            except:
                intVal = 0
            if 0 <= value <= 100:
                self.signal.proSig.emit(intVal)

    def setReportDateRange(self, startDate, endDate):
        self.__startDate = startDate
        self.__endDate = endDate

    def setIfPubOrgData(self, val):
        self.__exportOrgData = val

    def setReportFilePath(self, filePathName):
        self.__reportFilePath = filePathName

    def setReportSourceDir(self, dirName):
        self.__sourceDir = dirName

    def __readAllFile(self):
        if not os.path.isdir(self.__sourceDir):
            return False
        for tableInfo in self.__supportTableList:
            del self.__fileList[tableInfo][:]
        self.__fileCount = 0
        for fileName in os.listdir(self.__sourceDir):
            fullPathName = os.path.join(self.__sourceDir, fileName)
            self.sendMsg(LanRes.I()['finding'] + '\n[%s]' % fullPathName)
            if is_zipfile(fullPathName):
                if re.match(Data.Info[Data.HistoryTable][Data.fileRule], os.path.basename(fullPathName)) is not None:
                    self.__fileList[Data.HistoryTable].append(fullPathName)
                    self.__fileCount += 1
                elif re.match(Data.Info[Data.ScheduleTable][Data.fileRule], os.path.basename(fileName)) is not None:
                    if not LanRes.I()['sheetSchedule']['isOrg'] or self.__exportOrgData:
                        self.__fileList[Data.ScheduleTable].append(fullPathName)
                        self.__fileCount += 1
                elif re.match(Data.Info[Data.OnlineTable][Data.fileRule], os.path.basename(fileName)) is not None:
                    if not LanRes.I()['sheetOnline']['isOrg'] or self.__exportOrgData:
                        self.__fileList[Data.OnlineTable].append(fullPathName)
                        self.__fileCount += 1
                elif re.match(Data.Info[Data.ChannelTable][Data.fileRule],
                              os.path.basename(fileName)) is not None:
                    #if not LanRes.I()['sheetChannel']['isOrg'] or self.__exportOrgData:
                    self.__fileList[Data.ChannelTable].append(fullPathName)
                    self.__fileCount += 1
            elif re.match(Data.Info[Data.UsersNumberTable][Data.fileRule], os.path.basename(fileName)) is not None:
                if not LanRes.I()['sheetUsersNumber']['isOrg'] or self.__exportOrgData:
                    self.__fileList[Data.UsersNumberTable].append(fullPathName)
                    self.__fileCount += 1

    def __statTotalConference(self, sheet, titles, dataType):
        if not sheet.exist():
            return
        dataCount = self.__dataHolders[dataType].count()
        for rowIndex, tmpData in enumerate(self.__dataHolders[dataType].getAll()):
            msgInfo = LanRes.getTable(dataType) + '(%d/%d)' % (rowIndex, dataCount)
            msgInfo += "\n" + LanRes.I()['warnMsg']['comTip']
            self.sendMsg(msgInfo)
            tmpRange = []
            for titleIndexStr in titles:
                tmpRange.append(unicode(tmpData.getData(KeyByIndex(titleIndexStr, dataType))))
            sheet.setRangeValue(rowIndex + 1, 0, len(titles), tmpRange)
            self.sendPercent(float(rowIndex) / self.__dataHolders[dataType].count() * 100)
        sheet.flush()
        if dataCount > 0:
            sheet.setRangeStyle(1, 0, self.__dataHolders[dataType].count(), len(titles) - 1, False)

    def __getHisTitleInfoBySheetName(self, sheetsName, sheetName):
        for k, v in LanRes.I()[sheetsName].items():
            if v['sheetName'] == sheetName:
                return v['title']
        return []

    def __statUserConference(self, sheet):
        dataType = Data.HistoryTable
        #第二列为con:WebAccount
        #keyWebAccount = KeyByIndex('2', dataType)
        keyWebAccount = 'his:WebAccount'
        #第三列为con:OrganizationID
        #keyOrgID = KeyByIndex('3', dataType)
        keyOrgID = 'his:OrganizationID'
        #第四列为con:StartTime，但是读取时只取年月日
        #keyStartDate = KeyByIndex('4', dataType)
        keyStartDate = 'his:StartTime'
        #第六列为con:FactLength
        #keyConfLen = KeyByIndex('6', dataType)
        keyConfLen = 'his:FactLength'
        self.sendMsg(LanRes.I()['processTable'] % LanRes.I()['sheetHistoryList'][0]['sheetName'])
        self.sendPercent(0)
        keyWebIDOrgIDSet = set([
            (x.getData(keyWebAccount), x.getData(keyOrgID)) for x in self.__dataHolders[dataType].getAll()
        ])
        columnCount = 0
        rowCount = 0
        for wordIndex, (webAccount, OrgID) in enumerate(keyWebIDOrgIDSet):
            dataByWord = [
                x for x in self.__dataHolders[dataType].getAll() if
                x.getData(keyWebAccount) == webAccount
                and x.getData(keyOrgID) == OrgID
            ]
            #先写入第一列【web ID】、第二列【组织ID】
            tmpRange = [webAccount, OrgID]
            curColumnIndex = 1
            #然后在按月统计，写入会议数和会议时长
            dateList = {}
            self.sendPercent(float(wordIndex) / len(keyWebIDOrgIDSet) * 100)
            for yearIndex in range(self.__startDate.year, self.__endDate.year + 1):
                for monthIndex in range(self.__startDate.month if yearIndex == self.__startDate.year else 1,
                                        (self.__endDate.month if yearIndex == self.__endDate.year else 12) + 1):
                    #按月统计的数据
                    dataByMonth = [x for x in dataByWord if x.getData(keyStartDate).year == yearIndex and x.getData(
                        keyStartDate).month == monthIndex]

                    curColumnIndex += 1
                    sFormat = LanRes.I()['yearMonthFormat'] % (yearIndex, monthIndex)
                    if not dateList.get((yearIndex, monthIndex), False):
                        #添加一列title
                        title = self.__getHisTitleInfoBySheetName('sheetHistoryList', sheet.getName())[2]
                        title = title % sFormat
                        sheet.setCell(0, curColumnIndex, title, True)
                        sheet.setColWidth(curColumnIndex, len(title.encode('utf-8')))
                    #添加月份的会议个数数据
                    tmpRange.append(len(dataByMonth))

                    curColumnIndex += 1
                    if not dateList.get((yearIndex, monthIndex), False):
                        #添加一列title
                        title = self.__getHisTitleInfoBySheetName('sheetHistoryList', sheet.getName())[3]
                        title = title % sFormat
                        sheet.setCell(0, curColumnIndex, title, True)
                        sheet.setColWidth(curColumnIndex, len(title.encode('utf-8')))
                    #添加月份的会议时长数据
                    tmpRange.append(sum([x.getData(keyConfLen) for x in dataByMonth]))
                    dateList[(yearIndex, monthIndex)] = True

                    rowCount = wordIndex + 1
                    columnCount = curColumnIndex
            sheet.setRangeValue(wordIndex + 1, 0, columnCount + 1, tmpRange)
        sheet.flush()
        if self.__dataHolders[dataType].count() > 0:
            sheet.setRangeStyle(0, 0, 0, columnCount, True)
            sheet.setRangeStyle(1, 0, rowCount, columnCount, False)

    def __statOrgConference(self, sheet):
        dataType = Data.HistoryTable
        #第三列为con:OrganizationID
        keyOrgID = KeyByIndex('3', dataType)
        #第四列为con:StartTime，但是读取时只取年月日
        keyStartDate = KeyByIndex('4', dataType)
        #第六列为con:FactLength
        keyConfLen = KeyByIndex('6', dataType)
        self.sendMsg(LanRes.I()['processTable'] % LanRes.I()['sheetHistoryList'][1]['sheetName'])
        self.sendPercent(0)
        keyOrgIDSet = set([x.getData(keyOrgID) for x in self.__dataHolders[dataType].getAll()])
        columnCount = 0
        rowCount = 0
        for OrgIndex, OrgID in enumerate(keyOrgIDSet):
            tmpRange = []
            #先写入第一列【组织ID】
            dataByWord = [x for x in self.__dataHolders[dataType].getAll() if x.getData(keyOrgID) == OrgID]
            tmpRange.append(OrgID)
            #sheet.setCell(OrgIndex + 1, 0, OrgID)
            curColumnIndex = 0
            dateList = {}
            self.sendPercent(float(OrgIndex) / len(keyOrgIDSet) * 100)
            for yearIndex in range(self.__startDate.year, self.__endDate.year + 1):
                for monthIndex in range(self.__startDate.month if yearIndex == self.__startDate.year else 1,
                                        (self.__endDate.month if yearIndex == self.__endDate.year else 12) + 1):
                    #按月统计的数据
                    dataByMonth = [x for x in dataByWord if x.getData(keyStartDate).year == yearIndex and x.getData(
                        keyStartDate).month == monthIndex]

                    curColumnIndex += 1
                    sFormat = LanRes.I()['yearMonthFormat'] % (yearIndex, monthIndex)
                    if not dateList.get((yearIndex, monthIndex), False):
                        #添加一列title
                        title = self.__getHisTitleInfoBySheetName('sheetHistoryList', sheet.getName())[1]
                        title = title % sFormat
                        sheet.setCell(0, curColumnIndex, title, True)
                        sheet.setColWidth(curColumnIndex, len(title.encode('utf-8')))
                    #添加月份的会议个数数据
                    tmpRange.append(len(dataByMonth))

                    curColumnIndex += 1
                    if not dateList.get((yearIndex, monthIndex), False):
                        #添加一列title
                        title = self.__getHisTitleInfoBySheetName('sheetHistoryList', sheet.getName())[2]
                        title = title % sFormat
                        sheet.setCell(0, curColumnIndex, title, True)
                        sheet.setColWidth(curColumnIndex, len(title.encode('utf-8')))

                    #添加月份的会议时长数据
                    tmpRange.append(sum([x.getData(keyConfLen) for x in dataByMonth]))
                    rowCount = OrgIndex + 1
                    columnCount = curColumnIndex
                    dateList[(yearIndex, monthIndex)] = True
            sheet.setRangeValue(OrgIndex + 1, 0, columnCount + 1, tmpRange)
        sheet.flush()
        if self.__dataHolders[dataType].count() > 0:
            sheet.setRangeStyle(0, 0, 0, columnCount, True)
            sheet.setRangeStyle(1, 0, rowCount, columnCount, False)

    #防止文件重复
    def __preventDuplication(self, removeIfExist=True):
        try:
            if removeIfExist:
                if os.path.isfile(self.__reportFilePath):
                    os.remove(self.__reportFilePath)
            else:
                if os.path.isfile(self.__reportFilePath + '_bak'):
                    os.remove(self.__reportFilePath + '_bak')
                os.rename(self.__reportFilePath, self.__reportFilePath + '_bak')
            return True
        except WindowsError:
            self.sendMsg(LanRes.I()['errorMsg']['canNotOpenFile'])
            return False
        except IOError:
            self.sendMsg(LanRes.I()['errorMsg']['canNotOpenFile'])
            return False

    def __getHisSheetIndexByName(self, sheetName):
        for k, v in LanRes.I()['sheetHistoryList'].items():
            if v['sheetName'] == sheetName:
                return k
        return None

    def __publicHistoryReport(self):
        sheetCount = len(LanRes.I()['sheetHistoryList'])
        for sheetIndex in range(sheetCount):
            info = LanRes.I()['sheetHistoryList'][sheetIndex]
            sheet = self.__excel.getSheet(info['sheetName'])
            if not sheet.exist():
                continue
            titleCount = len(info['title'])
            for titleIndex in range(titleCount):
                title = info['title'][titleIndex]
                if title.find('%s') == -1:
                    sheet.setCell(0, titleIndex, title, True)
            sheet.setRangeStyle(0, 0, 0, titleCount - 1, True)
            sheetName = sheet.getName()
            if sheetName == LanRes.I()['sheetHistoryList'][0]['sheetName']:
                self.__statUserConference(sheet)
            elif sheetName == LanRes.I()['sheetHistoryList'][1]['sheetName']:
                self.__statOrgConference(sheet)
            elif sheetName == LanRes.I()['sheetHistoryList'][2]['sheetName']:
                self.__statTotalConference(sheet, info['title'], Data.HistoryTable)
            for colIndex in range(titleCount):
                sheet.setColWidth(colIndex, len(info['title'][colIndex].encode('utf-8')))

    def __publicCommonReport(self, dataType):
        if dataType == Data.ScheduleTable:
            sheet, titles = self.__setSheetTitle('sheetSchedule')
        elif dataType == Data.OnlineTable:
            sheet, titles = self.__setSheetTitle('sheetOnline')
        elif dataType == Data.UsersNumberTable:
            sheet, titles = self.__setSheetTitle('sheetUsersNumber')
        else:
            return
        self.__statTotalConference(sheet, titles, dataType)

    def __calcUserDetailData(self):
        dataType = Data.UserDetailTable
        holder = DataHolder(dataType)
        historyData = self.__dataHolders[Data.HistoryTable].getAll()
        scheduleData = self.__dataHolders[Data.ScheduleTable].getAll()
        onlineData = self.__dataHolders[Data.OnlineTable].getAll()
        bChannel = self.__hasChannel()
        channelData = self.__dataHolders[Data.ChannelTable].getAll() if bChannel else None
        #先从历史会议表里取"会议创建者"信息
        for index, data in enumerate(historyData):
            self.sendPercent(float(index) / len(historyData) * 100)
            orgID = data.getData('his:OrganizationID')
            #if orgID != 'GMCCMMEET':
            #    continue
            confID = data.getData('his:ConferenceID')
            callerID = data.getData('his:WebAccount')
            confData = ConfData(dataType)
            confData.setTypeData('Creator', callerID)
            confData.setTypeData('OrgID', orgID)
            confData.setTypeData('ConfID', confID)
            confData.setTypeData('StartTime', data.getData('his:StartTime'))
            confData.setTypeData('EndTime', data.getData('his:FactEndTime'))
            confData.setTypeData('ConfLength', data.getData('his:FactLength'))
            confData.setTypeData('CallerCount', self.__getCallerCount(confID, scheduleData))
            confData.setTypeData('RealCallerCount', self.__getRealCallerCount(confID, onlineData))
            confData.setTypeData('ChannelID', self.__getChannelID(callerID, channelData) if bChannel else 'null')
            holder.addConfData(confData)
        self.__dataHolders[dataType] = holder
        return holder

    def __getCallerCount(self, confID, scheduleData):
        for info in scheduleData:
            if info.getData('sch:MeetingID') == confID:
                return info.getData('sch:OrderParty')
        return 0

    def __getRealCallerCount(self, confID, onlineData):
        return len([x for x in onlineData if x.getData('con:MeetingID') == confID])

    def __getChannelID(self, TelNumber, channelData):
        if channelData is None:
            return 'null'
        for info in channelData:
            if info.getData('TelNumber') == TelNumber:
                return info.getData('ChannelName')
        return "None"

    def __processActiveUserDetails(self):
        dataType = Data.UserDetailTable
        sheet, titles = self.__setSheetTitle('sheetUserDetail')
        titleCount = len(titles)
        if not sheet.exist():
            return
        self.sendMsg(LanRes.I()['processTable'] % LanRes.getTable(dataType))
        #计算出细节数据，然后写入到页签中
        holder = self.__calcUserDetailData()
        for rowIndex, tmpData in enumerate(holder.getAll()):
            rangeData = []
            for titleIndex in range(titleCount):
                rangeData.append(autoStr(tmpData.getData(KeyByIndex(titleIndex, dataType))))
            sheet.setRangeValue(rowIndex + 1, 0, titleCount, rangeData)
            self.sendPercent(float(rowIndex) / holder.count() * 100)
        if holder.count() > 0:
            sheet.setRangeStyle(1, 0, holder.count(), titleCount - 1, False)
        sheet.flush()

    def __publicUserDetailReport(self):
        self.__processActiveUserDetails()
        self.__statChannelData()

    def __getChannelRangeData(self, channel, newCont, oldCont):
        activeUserCount = len([x for x in newCont if x.getData('ChannelID') == channel])
        totalCallsNum = len([x for x in oldCont if x.getData('ChannelID') == channel])
        totalCallsDuration = sum([x.getData('ConfLength') for x in oldCont if x.getData('ChannelID') == channel])
        return [
            LanRes.I()['other'] if channel == 'None' else channel,
            str(activeUserCount),
            str(totalCallsNum),
            str(totalCallsDuration),
            "0" if activeUserCount == 0 else "%.4f" % (totalCallsNum * 1.0 / activeUserCount),
            "0" if activeUserCount == 0 else "%.4f" % (totalCallsDuration * 1.0 / activeUserCount)
        ]

    def __deRepeat(self, cont, specKey):
        newCont = []
        keyList = []
        for info in cont:
            if specKey is None or specKey in info.getData('OrgID'):
                key = info.getData('Creator')
                if key not in keyList:
                    newCont.append(info)
                    keyList.append(key)
        return newCont

    def __statChannelData(self):
        dataType = Data.UserDetailTable
        sheet, titles = self.__setSheetTitle('sheetChannel')
        if not sheet.exist():
            return
        self.sendMsg(LanRes.I()['processTable'] % LanRes.getTable(dataType))
        holder = self.__dataHolders[dataType]
        specKey = Data.Info[Data.ChannelTable][Data.other]
        channelSet = set([x.getData('ChannelID') for x in holder.getAll() if
                          x.getData('ChannelID') != 'None' and (specKey is None or specKey in x.getData('OrgID'))])
        oldCont = [x for x in holder.getAll() if (specKey is None or specKey in x.getData('OrgID'))]
        newCont = [x for x in self.__deRepeat(holder.getAll(), specKey)]
        for index, channel in enumerate(channelSet):
            sheet.setRangeValue(index + 1, 0, len(titles), self.__getChannelRangeData(channel, newCont, oldCont))
            self.sendPercent(float(index) / len(channelSet) * 100)
        else:
            rangeData = self.__getChannelRangeData('None', newCont, oldCont)
            sheet.setRangeValue(len(channelSet) + 1, 0, len(titles), rangeData)
            self.sendPercent(100)
        if holder.count() > 0:
            sheet.setRangeStyle(1, 0, len(channelSet) + 1, len(titles) - 1, False)
        sheet.flush()

    #设置标题行，根据标题行设置列宽，然后返回sheet对象和标题数据
    def __setSheetTitle(self, sheetName):
        info = LanRes.I()[sheetName]
        sheet = self.__excel.getSheet(info['sheetName'])
        if not sheet.exist():
            return sheet, []
        titles = info['title']
        titleCount = len(titles)
        for titleIndex in range(titleCount):
            sheet.setCell(0, titleIndex, info['title'][titleIndex], True)
        sheet.setRangeStyle(0, 0, 0, titleCount - 1, True)
        for colIndex in range(titleCount):
            sheet.setColWidth(colIndex, len(info['title'][colIndex].encode('utf-8')))
        return sheet, titles

    def __setSheetTitleByTitles(self, sheet, titles):
        titleCount = len(titles)
        for titleIndex in range(titleCount):
            sheet.setCell(0, titleIndex, titles[titleIndex], True)
        sheet.setRangeStyle(0, 0, 0, titleCount - 1, True)
        for colIndex in range(titleCount):
            sheet.setColWidth(colIndex, len(titles[colIndex].encode('utf-8')))

    def __getDateStr(self, dateVal):
        if isinstance(dateVal, datetime):
            return "%04d%02d%02d" % (dateVal.year, dateVal.month, dateVal.day)
        else:
            return 'null'

    def __publicUsersNumber(self):
        dataType = Data.UsersNumberTable
        sheetName = LanRes.getTable(dataType)
        self.sendMsg(LanRes.I()['processTable'] % sheetName)
        sheet = self.__excel.getSheet(sheetName)
        if not sheet.exist():
            return
        holder = self.__dataHolders[dataType]
        dateSet = sorted(set([x.getData('DateField') for x in holder.getAll()]))
        orgSet = set([(x.getData('OrganizationID'), x.getData('OrganizationName')) for x in holder.getAll()])
        titleList = [LanRes.I()[LanRes.mapData[dataType]]['title'][1], LanRes.I()[LanRes.mapData[dataType]]['title'][2]]
        #写入标题
        for dataInfo in dateSet:
            titleList.append(self.__getDateStr(dataInfo))
        self.__setSheetTitleByTitles(sheet, titleList)
        #写入数据
        for orgIndex, (orgID, orgName) in enumerate(orgSet):
            tmpData = [orgID, orgName]
            for dateIndex, dateInfo in enumerate(dateSet):
                val = sum([
                    x.getData('TotalUserNumber') for x in holder.getAll()
                    if x.getData('DateField') == dateInfo and x.getData('OrganizationID') == orgID
                ])
                tmpData.append(val)
            sheet.setRangeValue(orgIndex + 1, 0, len(tmpData), tmpData)
            self.sendPercent(float(orgIndex) / len(orgSet) * 100)
        sheet.flush()
        #设置格式
        if holder.count() > 0:
            sheet.setRangeStyle(1, 0, len(orgSet), len(dateSet) + 1, False)

    def __publicReport(self, dataType):
        if dataType == Data.HistoryTable:
            self.__publicHistoryReport()
        elif dataType == Data.UserDetailTable:
            self.__publicUserDetailReport()
        elif dataType == Data.UsersNumberTable:
            self.__publicUsersNumber()
        else:
            self.__publicCommonReport(dataType)

    def __process(self, dataType):
        if dataType in [Data.ChannelTable] and not self.__hasChannel():
            return
        self.sendMsg(LanRes.I()['info']['beginReadSource'])
        self.__dataHolders[dataType] = DataHolder(dataType)
        for fileName in self.__fileList[dataType]:
            msgInfo = LanRes.I()['loading'] % os.path.basename(fileName)
            msgInfo += '\n' + LanRes.I()['warnMsg']['comTip']
            self.sendMsg(msgInfo)
            self.__dataHolders[dataType].Read(fileName, self.__startDate, self.__endDate)
            self.__readCount += 1
            self.sendPercent(float(self.__readCount) / self.__fileCount * 100 + 0.5)
        self.sendMsg(LanRes.I()['info']['ReadSourceFinish'] + ',' + LanRes.I()['info']['beginMakeReport'])
        self.__publicReport(dataType)
        self.sendPercent(100)

    def __hasChannel(self):
        return len(self.__fileList[Data.ChannelTable]) > 0

    def __checkAddSheet(self, sheetList, sheetInfo):
        if not sheetInfo['isOrg'] or self.__exportOrgData:
            sheetList.append(sheetInfo['sheetName'])

    def __getSheetNameList(self):
        sheetNameList = []
        self.__checkAddSheet(sheetNameList, LanRes.I()['sheetUsersNumber'])
        self.__checkAddSheet(sheetNameList, LanRes.I()['sheetUserDetail'])
        if self.__hasChannel():
            self.__checkAddSheet(sheetNameList, LanRes.I()['sheetChannel'])
        sheetInfo = LanRes.I()['sheetHistoryList']
        for sheetIndex in range(len(sheetInfo)):
            self.__checkAddSheet(sheetNameList, sheetInfo[sheetIndex])
        self.__checkAddSheet(sheetNameList, LanRes.I()['sheetSchedule'])
        self.__checkAddSheet(sheetNameList, LanRes.I()['sheetOnline'])
        return sheetNameList

    def getTimeDelta(self):
        return (datetime.now() - self.__beginTime).total_seconds()

    def run(self):
        if ReportMaker.CanAction:
            ReportMaker.CanAction = False
        else:
            self.sendMsg(LanRes.I()['info']['waitForLastAction'])
            return
        if not self.__preventDuplication():
            return True
        self.signal.btnRunEnable.emit(False)
        self.__beginTime = datetime.now()
        try:
            try:
                self.__readAllFile()
                if self.__fileCount == 0:
                    self.sendMsg(LanRes.I()['noData'])
                    return
                limitNum = math.floor(float(Data.MaxRowCountInExcel2003) / Data.MaxSizeInOneZip)
                #由于com api优化之后效率很高，尽量使用com接口
                self.__useCom = self.__fileCount > int(limitNum - 2)
                if self.__useCom:
                    limitNum = math.floor(float(Data.MaxRowCountInExcel2007) / Data.MaxSizeInOneZip)
                    if self.__fileCount > limitNum:
                        #当数据量已经超过excel2007的限制，不再处理
                        self.sendMsg(LanRes.I()['outOfMemory'])
                        return
                    suffix = '.xlsx'
                    self.sendMsg(LanRes.I()['warnMsg']['comTip'])
                else:
                    suffix = '.xls'
                self.__parent.setSuffix(suffix)
                self.__reportFilePath += suffix
                self.__excel = ExcelImpl(self.__reportFilePath, self.__useCom)
                if self.__useCom and not self.__excel.isComMode():
                    self.__parent.setSuffix('.xls')
                    self.__reportFilePath += '.xls'
                    self.__logger.info('not install excel yet.')
                self.__excel.addSheets(self.__getSheetNameList())
                #执行发布过程
                for tableInfo in self.__supportTableList:
                    self.__process(tableInfo)
                self.__excel.selectFirstSheet()
                #回收临时内存
                for tableInfo in self.__supportTableList:
                    if tableInfo == Data.ChannelTable and not self.__hasChannel():
                        continue
                    self.__dataHolders[tableInfo].release()
                    del self.__dataHolders[tableInfo]
                gc.collect()
                self.sendMsg(LanRes.I()['waiting'])
            except pythoncom.com_error as error:
                self.sendMsg(LanRes.I()['outOfMemory'])
                print (error)
                print (vars(error))
                print (error.args)
                self.__logger.error(traceback.format_exc())
            except MemoryError:
                self.sendMsg(LanRes.I()['outOfMemory'])
                self.__logger.error(traceback.format_exc())
            except:
                self.__logger.error(traceback.format_exc())
        finally:
            if self.__excel:
                self.__excel.save()
                del self.__excel
                #由于excel对象占用很大内存，执行完了手动回收一下
                gc.collect()
                self.sendMsg(LanRes.I()['info']['makeReportFinish'] % (self.__reportFilePath, self.getTimeDelta()))
            self.signal.btnRunEnable.emit(True)
            ReportMaker.CanAction = True


class Logger(object):
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt=' %m-%d %H:%M',
            filename='trace.log',
            filemode='a')
        self.logger = logging.getLogger(os.path.basename(__file__))

    def error(self, msg):
        self.logger.error(msg)

    def info(self, msg):
        self.logger.info(msg)


class Config(object):
    """
    配置类，用于保存配置数据
    """
    def __init__(self, fileName):
        self.__fileName = fileName

    def save(self, content):
        with open(self.__fileName, 'wb') as f:
            try:
                cPickle.dump(content, f, 1)
            except:
                pass

    def load(self):
        tmp = []
        if os.path.isfile(self.__fileName):
            with open(self.__fileName, 'rb') as f:
                try:
                    tmp = cPickle.load(f)
                except:
                    pass
        return tmp

    def delete(self):
        if os.path.isfile(self.__fileName):
            os.remove(self.__fileName)
