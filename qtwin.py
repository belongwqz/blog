# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\code\confReport\reportWnd.ui'
#
# Created: Tue Apr 23 09:48:11 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

import os
import sys
import subprocess
from PySide import QtCore, QtGui
from tool import *
from resource import LanRes
from datetime import datetime


def MsgBox(flag, caption, msg):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap('res.dll'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    msg_box = QtGui.QMessageBox(flag, caption, msg)
    msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    msg_box.setWindowIcon(icon)
    msg_box.show()
    msg_box.exec_()


class ReportWindow(object):
    def __init__(self):
        self.__sourceDir = None
        self.__outputPath = os.path.join(os.getcwd() + os.sep + 'output')
        self.__reportName = ''
        self.__suffix = ''
        self.__currentProgress = 0
        self.wndIns = None
        self.__confDataFile = os.path.join(QtCore.QDir.currentPath(), 'conf.data')
        self.__fromDataTime = QtCore.QDateTime.currentDateTime().addMonths(-1)
        self.__toDataTime = QtCore.QDateTime.currentDateTime().addMonths(1)
        self.__dataDir = QtCore.QDir.currentPath()
        self.__ifPubOrgData = True
        self.__config = Config(self.__confDataFile)
        self.loadConf()

    def loadConf(self):
        if os.path.isfile(self.__confDataFile):
            confData = self.__config.load()
            if len(confData) == 5:
                self.__fromDataTime = confData[0]
                self.__toDataTime = confData[1]
                self.__dataDir = confData[2]
                self.__ifPubOrgData = confData[3]
                self.setLanguageType(confData[4])
            else:
                self.__config.delete()

    def saveConf(self):
        dataToSave = [self.editStartDate.dateTime(),
                      self.editEndDate.dateTime(),
                      self.editDataSource.text(),
                      self.cbPublicOrgData.isChecked(),
                      LanRes.Type]
        self.__config.save(dataToSave)

    def setSuffix(self, cont):
        self.__suffix = cont

    def getSuffix(self):
        return self.__suffix

    def startStat(self):
        if self.wndIns.isExcelRun() and self.wndIns.needSingleExcel:
            self.wndIns.warn(LanRes.I()['warnMsg']['closeExcel'])
            self.wndIns.bKill = False
            return
        if self.editEndDate.dateTime() > self.editStartDate.dateTime().addDays(
                Data.MaxDataDelta) or self.editStartDate.date() >= self.editEndDate.date():
            self.wndIns.warn(LanRes.I()['warnMsg']['dataIsWrong'])
            return
        self.__sourceDir = self.editDataSource.text()
        if not (self.__sourceDir is not None and os.path.isdir(self.__sourceDir)):
            self.wndIns.warn(LanRes.I()['warnMsg']['noDataSource'])
            return
        if not os.path.isdir(self.__outputPath):
            os.makedirs(self.__outputPath)
        self.__reportName = '%s-%s_report_%s' % (
            self.editStartDate.dateTime().toString('yyyyMMdd'),
            self.editEndDate.dateTime().toString('yyyyMMdd'),
            datetime.now().strftime('%Y%m%d%H%M%S')
        )
        oper = ReportMaker(self)
        dtStart = datetime.fromtimestamp(self.editStartDate.dateTime().toTime_t())
        dtEnd = datetime.fromtimestamp(self.editEndDate.dateTime().toTime_t())
        oper.setIfPubOrgData(self.cbPublicOrgData.isChecked())
        oper.setReportDateRange(dtStart, dtEnd)
        oper.setReportSourceDir(self.__sourceDir)
        oper.setReportFilePath(os.path.join(self.__outputPath, self.__reportName))
        oper.signal.msgSig.connect(self.msg)
        oper.signal.proSig.connect(self.progress)
        oper.signal.btnRunEnable.connect(self.setActionEnable)
        oper.start()
        self.wndIns.bKill = True

    def getSourceDir(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(None, LanRes.I()['dataSourceCation'], self.editDataSource.text())
        if os.path.isdir(unicode(dirName)):
            self.editDataSource.setText(dirName)
            self.__sourceDir = unicode(dirName)

    def openResultPath(self):
        if not os.path.isdir(self.__outputPath):
            self.wndIns.warn(LanRes.I()['warnMsg']['fileNotExist'])
            return
        pathName = os.path.join(self.__outputPath, self.__reportName + self.__suffix)
        if not os.path.isfile(pathName):
            cmdInfo = os.path.join(os.environ.get('WINDIR'), 'explorer.exe %s') % self.__outputPath
        else:
            cmdInfo = os.path.join(os.environ.get('WINDIR'), 'explorer.exe /n,/select,%s') % pathName
        os.popen(cmdInfo)

    def changeLanguage(self, index):
        for i, info in enumerate(LanRes.LanSupport):
            if i == index:
                self.setLanguageType(info)

    def msg(self, info):
        self.labelCurrentState.setText(info)

    def progress(self, value):
        if self.__currentProgress != value:
            self.__currentProgress = value
            self.ctlProgress.setValue(value)

    def setActionEnable(self, bEnable):
        self.wndIns.setEnabled(bEnable)

    def setupUi(self, MainWindow):
        self.wndIns = MainWindow
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('res.dll'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(349, 455)
        MainWindow.setMinimumSize(QtCore.QSize(349, 455))
        MainWindow.setMaximumSize(QtCore.QSize(349, 455))
        MainWindow.setWindowIcon(icon)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.btnRun = QtGui.QPushButton(self.centralWidget)
        self.btnRun.setGeometry(QtCore.QRect(60, 410, 111, 23))
        self.btnRun.setObjectName("btnRun")
        self.btnOpenReport = QtGui.QPushButton(self.centralWidget)
        self.btnOpenReport.setGeometry(QtCore.QRect(180, 410, 111, 23))
        self.btnOpenReport.setObjectName("btnOpenReport")
        self.gbCurrentStep = QtGui.QGroupBox(self.centralWidget)
        self.gbCurrentStep.setGeometry(QtCore.QRect(20, 260, 311, 131))
        self.gbCurrentStep.setObjectName("gbCurrentStep")
        self.labelCurrentState = QtGui.QLabel(self.gbCurrentStep)
        self.labelCurrentState.setGeometry(QtCore.QRect(20, 20, 261, 71))
        self.labelCurrentState.setStyleSheet("")
        self.labelCurrentState.setFrameShape(QtGui.QFrame.StyledPanel)
        self.labelCurrentState.setTextFormat(QtCore.Qt.AutoText)
        self.labelCurrentState.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.labelCurrentState.setWordWrap(True)
        self.labelCurrentState.setObjectName("labelCurrentState")
        self.ctlProgress = QtGui.QProgressBar(self.gbCurrentStep)
        self.ctlProgress.setGeometry(QtCore.QRect(20, 100, 291, 23))
        self.ctlProgress.setStyleSheet("")
        self.ctlProgress.setProperty("value", 0)
        self.ctlProgress.setObjectName("ctlProgress")
        self.gbSetting = QtGui.QGroupBox(self.centralWidget)
        self.gbSetting.setGeometry(QtCore.QRect(20, 20, 311, 221))
        self.gbSetting.setObjectName("gbSetting")
        self.cbPublicOrgData = QtGui.QCheckBox(self.gbSetting)
        self.cbPublicOrgData.setGeometry(QtCore.QRect(70, 180, 141, 20))
        self.cbPublicOrgData.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.cbPublicOrgData.setChecked(self.__ifPubOrgData)
        self.cbPublicOrgData.setObjectName("cbPublicOrgData")
        self.editEndDate = QtGui.QDateEdit(self.gbSetting)
        self.editEndDate.setGeometry(QtCore.QRect(100, 103, 171, 20))
        self.editEndDate.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.editEndDate.setAutoFillBackground(True)
        self.editEndDate.setFrame(True)
        self.editEndDate.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.editEndDate.setDateTime(self.__toDataTime)
        self.editEndDate.setCalendarPopup(True)
        self.editEndDate.setObjectName("editEndDate")
        self.labelEndTime = QtGui.QLabel(self.gbSetting)
        self.labelEndTime.setGeometry(QtCore.QRect(7, 103, 81, 20))
        self.labelEndTime.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.labelEndTime.setObjectName("labelEndTime")
        self.cbLanguage = QtGui.QComboBox(self.gbSetting)
        self.cbLanguage.setGeometry(QtCore.QRect(100, 26, 171, 22))
        self.cbLanguage.setObjectName("cbLanguage")
        for k, v in LanRes.LanSupport.items():
            self.cbLanguage.addItem(v)
        for i, info in enumerate(LanRes.LanSupport):
            if LanRes.Type == info:
                self.cbLanguage.setCurrentIndex(i)
        self.labelDataSource = QtGui.QLabel(self.gbSetting)
        self.labelDataSource.setGeometry(QtCore.QRect(7, 140, 81, 20))
        self.labelDataSource.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.labelDataSource.setObjectName("labelDataSource")
        self.labelLanguage = QtGui.QLabel(self.gbSetting)
        self.labelLanguage.setGeometry(QtCore.QRect(7, 26, 81, 20))
        self.labelLanguage.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.labelLanguage.setObjectName("labelLanguage")
        self.editDataSource = QtGui.QLineEdit(self.gbSetting)
        self.editDataSource.setGeometry(QtCore.QRect(100, 141, 171, 20))
        self.editDataSource.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.editDataSource.setReadOnly(True)
        self.editDataSource.setObjectName("editDataSource")
        self.editDataSource.setText(self.__dataDir)
        self.editStartDate = QtGui.QDateEdit(self.gbSetting)
        self.editStartDate.setGeometry(QtCore.QRect(100, 66, 171, 20))
        self.editStartDate.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.editStartDate.setAutoFillBackground(True)
        self.editStartDate.setInputMethodHints(QtCore.Qt.ImhPreferNumbers)
        self.editStartDate.setWrapping(False)
        self.editStartDate.setFrame(True)
        self.editStartDate.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.editStartDate.setAccelerated(False)
        self.editStartDate.setDateTime(self.__fromDataTime)
        self.editStartDate.setCurrentSection(QtGui.QDateTimeEdit.YearSection)
        self.editStartDate.setCalendarPopup(True)
        self.editStartDate.setObjectName("editStartDate")
        self.labelStartTime = QtGui.QLabel(self.gbSetting)
        self.labelStartTime.setGeometry(QtCore.QRect(7, 66, 81, 20))
        self.labelStartTime.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.labelStartTime.setObjectName("labelStartTime")
        self.btnSetDataSource = QtGui.QPushButton(self.gbSetting)
        self.btnSetDataSource.setGeometry(QtCore.QRect(270, 140, 21, 21))
        self.btnSetDataSource.setObjectName("btnSetDataSource")
        MainWindow.setCentralWidget(self.centralWidget)
        MainWindow.setWindowFlags(MainWindow.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        QtCore.QObject.connect(self.btnRun, QtCore.SIGNAL("clicked()"), self.startStat)
        QtCore.QObject.connect(self.btnOpenReport, QtCore.SIGNAL("clicked()"), self.openResultPath)
        QtCore.QObject.connect(self.btnSetDataSource, QtCore.SIGNAL("clicked()"), self.getSourceDir)
        QtCore.QObject.connect(self.cbLanguage, QtCore.SIGNAL("currentIndexChanged(int)"), self.changeLanguage)

    def retranslateUi(self, MainWindow):
        if MainWindow is None:
            return
        MainWindow.setWindowTitle(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['winTitle'], None, QtGui.QApplication.UnicodeUTF8))
        self.btnRun.setText(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['execStat'], None, QtGui.QApplication.UnicodeUTF8))
        self.btnOpenReport.setText(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['openResultPath'], None, QtGui.QApplication.UnicodeUTF8))
        self.gbCurrentStep.setTitle(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['process'], None, QtGui.QApplication.UnicodeUTF8))
        self.labelCurrentState.setText(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['initState'], None, QtGui.QApplication.UnicodeUTF8))
        self.gbSetting.setTitle(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['setting'], None, QtGui.QApplication.UnicodeUTF8))
        self.cbPublicOrgData.setText(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['ifPubOrgData'], None, QtGui.QApplication.UnicodeUTF8))
        self.editEndDate.setDisplayFormat(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['dateFormat'], None, QtGui.QApplication.UnicodeUTF8))
        self.labelEndTime.setText(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['endDate'], None, QtGui.QApplication.UnicodeUTF8))
        self.labelDataSource.setText(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['dataSource'], None, QtGui.QApplication.UnicodeUTF8))
        self.labelLanguage.setText(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['language'], None, QtGui.QApplication.UnicodeUTF8))
        self.editStartDate.setDisplayFormat(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['dateFormat'], None, QtGui.QApplication.UnicodeUTF8))
        self.labelStartTime.setText(
            QtGui.QApplication.translate("MainWindow", LanRes.I()['startDate'], None, QtGui.QApplication.UnicodeUTF8))
        self.btnSetDataSource.setText(
            QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))

    def setLanguageType(self, lanType):
        LanRes.Type = lanType
        self.retranslateUi(self.wndIns)


#重载QtGui.QMainWindow来捕获一些事件
class MyWnd(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MyWnd, self).__init__(parent)
        self.bKill = False

        #是否要求关闭Excel再运行任务
        self.needSingleExcel = False

    def killExcel(self):
        if self.bKill:
            subprocess.call(['taskkill', '/f', '/im', 'excel.exe'])

    def isExcelRun(self):
        return processNum('excel.exe') > 0

    def closeEvent(self, event):
        if ReportMaker.CanAction or self.ask(LanRes.I()['askMsg']['taskNotFinish']):
            if self.isExcelRun() and self.needSingleExcel:
                self.killExcel()
            event.accept()
        else:
            event.ignore()

    def ask(self, msg):
        reply = QtGui.QMessageBox.question(self, LanRes.I()['askCaption'], msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        return reply == QtGui.QMessageBox.Yes

    def warn(self, msg):
        QtGui.QMessageBox.question(self, LanRes.I()['warnCaption'], msg, QtGui.QMessageBox.Warning)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ins = singleInstance()
    if ins.alreadyRunning():
        MsgBox(QtGui.QMessageBox.Warning, LanRes.I()['warnCaption'], LanRes.I()['single'])
        sys.exit(0)
    MainWindow = MyWnd()
    MainWindow = MyWnd()
    ui = ReportWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    val = app.exec_()
    ui.saveConf()
    del MainWindow
    sys.exit(val)
