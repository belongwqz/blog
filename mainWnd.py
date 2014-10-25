# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\code\encrypt\mainWnd.ui'
#
# Created: Thu Apr 03 15:28:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import os
import sys
from CryptTool import SumCrypt, CipherCrypt


class FileTextEdit(QtGui.QLineEdit):
        def __init__(self, parent, sumCtrl):
            self.sumCtrl = sumCtrl
            super(FileTextEdit, self).__init__(parent)
            self.setDragEnabled(True)

        def dragEnterEvent(self, event):
            data = event.mimeData()
            urls = data.urls()
            if urls and urls[0].scheme() == 'file' or data.hasFormat('text/plain'):
                event.acceptProposedAction()

        def dragMoveEvent(self, event):
            data = event.mimeData()
            urls = data.urls()
            if urls and urls[0].scheme() == 'file' or data.hasFormat('text/plain'):
                event.acceptProposedAction()

        def dropEvent(self, event):
            data = event.mimeData()
            urls = data.urls()
            if urls and urls[0].scheme() == 'file':
                filePath = unicode(urls[0].path())[1:]
                self.setText(filePath)
                self.sumCtrl.sumDragIn(True)
            elif data.hasFormat('text/plain'):
                self.setText(data.text())
                self.sumCtrl.sumDragIn(False)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(417, 246)
        MainWindow.setMinimumSize(QtCore.QSize(417, 246))
        MainWindow.setMaximumSize(QtCore.QSize(417, 246))
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.tabWidget = QtGui.QTabWidget(self.centralWidget)
        self.tabWidget.setGeometry(QtCore.QRect(9, 9, 401, 231))
        self.tabWidget.setObjectName("tabWidget")
        self.sum = QtGui.QWidget()
        self.sum.setObjectName("sum")
        self.cb_sum_alg_list = QtGui.QComboBox(self.sum)
        self.cb_sum_alg_list.setGeometry(QtCore.QRect(50, 10, 101, 22))
        self.cb_sum_alg_list.setObjectName("cb_sum_alg_list")
        self.label_sum_alg = QtGui.QLabel(self.sum)
        self.label_sum_alg.setGeometry(QtCore.QRect(10, 10, 31, 16))
        self.label_sum_alg.setObjectName("label_sum_alg")
        self.label_sum_input = QtGui.QLabel(self.sum)
        self.label_sum_input.setGeometry(QtCore.QRect(10, 70, 31, 16))
        self.label_sum_input.setObjectName("label_sum_input")
        self.edit_sum_input = FileTextEdit(self.sum, self)
        #self.edit_sum_input = QtGui.QLineEdit(self.sum)
        self.edit_sum_input.setGeometry(QtCore.QRect(50, 70, 291, 20))
        self.edit_sum_input.setObjectName("edit_sum_input")
        self.btn_sum_browser = QtGui.QToolButton(self.sum)
        self.btn_sum_browser.setGeometry(QtCore.QRect(340, 70, 41, 18))
        self.btn_sum_browser.setArrowType(QtCore.Qt.RightArrow)
        self.btn_sum_browser.setObjectName("btn_sum_browser")
        self.label_sum_output = QtGui.QLabel(self.sum)
        self.label_sum_output.setGeometry(QtCore.QRect(10, 130, 31, 16))
        self.label_sum_output.setObjectName("label_sum_output")
        self.edit_sum_output = QtGui.QLineEdit(self.sum)
        self.edit_sum_output.setGeometry(QtCore.QRect(50, 130, 331, 20))
        self.edit_sum_output.setObjectName("edit_sum_output")
        self.btn_sum_calc = QtGui.QPushButton(self.sum)
        self.btn_sum_calc.setGeometry(QtCore.QRect(120, 170, 161, 23))
        self.btn_sum_calc.setObjectName("btn_sum_calc")
        self.label_sum_target_type = QtGui.QLabel(self.sum)
        self.label_sum_target_type.setGeometry(QtCore.QRect(190, 10, 61, 16))
        self.label_sum_target_type.setObjectName("label_sum_target_type")
        self.cb_sum_target_type = QtGui.QComboBox(self.sum)
        self.cb_sum_target_type.setGeometry(QtCore.QRect(250, 10, 131, 22))
        self.cb_sum_target_type.setObjectName("cb_sum_target_type")
        self.cb_sum_target_type.addItem("")
        self.cb_sum_target_type.addItem("")
        self.tabWidget.addTab(self.sum, "")
        self.encryptdecrpyt = QtGui.QWidget()
        self.encryptdecrpyt.setObjectName("encryptdecrpyt")
        self.label_encrypt_input = QtGui.QLabel(self.encryptdecrpyt)
        self.label_encrypt_input.setGeometry(QtCore.QRect(10, 90, 31, 16))
        self.label_encrypt_input.setObjectName("label_encrypt_input")
        self.cb_encrypt_alg_list = QtGui.QComboBox(self.encryptdecrpyt)
        self.cb_encrypt_alg_list.setGeometry(QtCore.QRect(50, 10, 331, 22))
        self.cb_encrypt_alg_list.setObjectName("cb_encrypt_alg_list")
        self.edit_encrypt_output = QtGui.QLineEdit(self.encryptdecrpyt)
        self.edit_encrypt_output.setGeometry(QtCore.QRect(50, 130, 331, 20))
        self.edit_encrypt_output.setObjectName("edit_encrypt_output")
        self.edit_encrypt_input = QtGui.QLineEdit(self.encryptdecrpyt)
        self.edit_encrypt_input.setGeometry(QtCore.QRect(50, 90, 331, 20))
        self.edit_encrypt_input.setObjectName("edit_encrypt_input")
        self.label_encrypt_output = QtGui.QLabel(self.encryptdecrpyt)
        self.label_encrypt_output.setGeometry(QtCore.QRect(10, 130, 31, 16))
        self.label_encrypt_output.setObjectName("label_encrypt_output")
        self.label_encrypt_alg = QtGui.QLabel(self.encryptdecrpyt)
        self.label_encrypt_alg.setGeometry(QtCore.QRect(10, 10, 31, 16))
        self.label_encrypt_alg.setObjectName("label_encrypt_alg")
        self.edit_encrypt_key = QtGui.QLineEdit(self.encryptdecrpyt)
        self.edit_encrypt_key.setGeometry(QtCore.QRect(50, 50, 331, 20))
        self.edit_encrypt_key.setObjectName("edit_encrypt_key")
        self.label_encrypt_key = QtGui.QLabel(self.encryptdecrpyt)
        self.label_encrypt_key.setGeometry(QtCore.QRect(10, 50, 31, 16))
        self.label_encrypt_key.setObjectName("label_encrypt_key")
        self.layoutWidget = QtGui.QWidget(self.encryptdecrpyt)
        self.layoutWidget.setGeometry(QtCore.QRect(70, 170, 241, 25))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_encrypt = QtGui.QPushButton(self.layoutWidget)
        self.btn_encrypt.setObjectName("btn_encrypt")
        self.horizontalLayout.addWidget(self.btn_encrypt)
        self.btn_decrypt = QtGui.QPushButton(self.layoutWidget)
        self.btn_decrypt.setObjectName("btn_decrypt")
        self.horizontalLayout.addWidget(self.btn_decrypt)
        self.tabWidget.addTab(self.encryptdecrpyt, "")
        MainWindow.setCentralWidget(self.centralWidget)
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.__initOther()

    def __initOther(self):
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap('res.dll'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(self.icon)
        self.sumAlgList = [
            'HMAC', 'MD2', 'MD4', 'MD5', 'RIPEMD', 'SHA', 'SHA224', 'SHA256', 'SHA384', 'SHA512', 'CRC32'
        ]
        self.cb_sum_alg_list.addItems(self.sumAlgList)
        self.cb_sum_alg_list.setCurrentIndex(3)
        self.btn_sum_browser.setEnabled(False)
        self.btn_sum_calc.setEnabled(False)
        self.edit_sum_input.setToolTip(u'输入必须为非空字符串或者有效文件名')
        self.edit_sum_input.connect(QtCore.SIGNAL('textChanged (const QString&)'), self.__sum_input_changed)
        self.cb_sum_target_type.connect(QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.__sum_type_changed)
        self.btn_sum_browser.connect(QtCore.SIGNAL('clicked()'), self.__sum_browser)
        self.btn_sum_calc.connect(QtCore.SIGNAL('clicked()'), self.__sum_calc)

        self.encryptAlgList = [
            'BASE64', 'BASE32', 'BASE16', 'AES', 'ARC2', 'ARC4', 'Blowfish',
            'CAST', 'DES', 'DES3', 'XOR'
        ]
        self.desKey = [
            'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
            'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
            'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
            't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5',
            '6', '7', '8', '9', '+', '/'
        ]
        self.mdxAesKey = {
            'DBPASSWORD': '31612745EBBACA34',
            'CONFERENCEPSW': '1A329517E77F917B',
            'WEBMCPSW': '02CAAE8A7526F4A9',
            'SFTPPASSWORD': 'F4DF8A0801805558',
            'OTHERPASSWORD': '2B5684812C0E8530',
            'ENTERPRISEADDRESSBOOKPSW': '5F7135812D0E4690'
        }
        self.cb_encrypt_alg_list.addItems(self.encryptAlgList)
        self.cb_encrypt_alg_list.setCurrentIndex(0)
        self.btn_encrypt.connect(QtCore.SIGNAL('clicked()'), self.__encrypt)
        self.btn_decrypt.connect(QtCore.SIGNAL('clicked()'), self.__decrypt)

    def sumDragIn(self, isFile):
        if isFile:
            self.cb_sum_target_type.setCurrentIndex(1)
        else:
            self.cb_sum_target_type.setCurrentIndex(0)
        self.edit_sum_output.setText('')

    def __sum_browser(self):
        self.edit_sum_input.setText(QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open')[0])

    def __sum_input_changed(self, info):
        input_val = info
        input_type = self.cb_sum_target_type.currentText()
        if (input_type == u'文件' and os.path.isfile(input_val)) or (input_type == u'字符串' and input_val != ''):
            self.edit_sum_input.setToolTip('')
            self.btn_sum_calc.setEnabled(True)
        else:
            self.edit_sum_input.setToolTip(u'输入必须为非空字符串或者有效文件名')
            self.btn_sum_calc.setEnabled(False)
        self.edit_sum_output.setText('')

    def __sum_type_changed(self, info):
        input_val = self.edit_sum_input.text()
        self.btn_sum_browser.setEnabled(info == u'文件')
        if (info == u'文件' and os.path.isfile(input_val)) or (info == u'字符串' and input_val != ''):
            self.edit_sum_input.setToolTip('')
            self.btn_sum_calc.setEnabled(True)
        else:
            self.edit_sum_input.setToolTip(u'输入必须为非空字符串或者有效文件名')
            self.btn_sum_calc.setEnabled(False)

    def __sum_calc(self):
        alg_type = self.cb_sum_alg_list.currentText()
        target_type = self.cb_sum_target_type.currentText()
        input_val = self.edit_sum_input.text()
        self.edit_sum_output.setText(
            SumCrypt(alg_type).File(input_val) if target_type == u'文件' else SumCrypt(alg_type).String(input_val)
        )

    def __encrypt(self):
        input_val = self.edit_encrypt_input.text()
        input_key = self.edit_encrypt_key.text()
        action_type = self.cb_encrypt_alg_list.currentText()
        result = CipherCrypt(action_type, self.mdxAesKey.get(input_key.upper(), input_key), input_val).Encrypt()
        if result is not None:
            self.edit_encrypt_output.setText(result)

    def __decrypt(self):
        input_val = self.edit_encrypt_input.text()
        input_key = self.edit_encrypt_key.text()
        action_type = self.cb_encrypt_alg_list.currentText()
        result = ''
        if action_type == 'AES' and input_key.strip() == '':
            for k, v in self.mdxAesKey.items():
                result = CipherCrypt(action_type, v, input_val).Decrypt()
                if result not in ['', None] and len(result.strip()) > 1:
                    self.edit_encrypt_key.setText(k)
                    break
        else:
            result = CipherCrypt(action_type, self.mdxAesKey.get(input_key.upper(), input_key), input_val).Decrypt()
        self.edit_encrypt_output.setText(result)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "签名加解密工具  ---power by w00177728", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sum_alg.setText(QtGui.QApplication.translate("MainWindow", "算法：", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sum_input.setText(QtGui.QApplication.translate("MainWindow", "输入：", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_sum_browser.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sum_output.setText(QtGui.QApplication.translate("MainWindow", "输出：", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_sum_calc.setText(QtGui.QApplication.translate("MainWindow", "开始计算", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sum_target_type.setText(QtGui.QApplication.translate("MainWindow", "操作对象：", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_sum_target_type.setItemText(0, QtGui.QApplication.translate("MainWindow", "字符串", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_sum_target_type.setItemText(1, QtGui.QApplication.translate("MainWindow", "文件", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sum), QtGui.QApplication.translate("MainWindow", "签名摘要", None, QtGui.QApplication.UnicodeUTF8))
        self.label_encrypt_input.setText(QtGui.QApplication.translate("MainWindow", "输入：", None, QtGui.QApplication.UnicodeUTF8))
        self.label_encrypt_output.setText(QtGui.QApplication.translate("MainWindow", "输出：", None, QtGui.QApplication.UnicodeUTF8))
        self.label_encrypt_alg.setText(QtGui.QApplication.translate("MainWindow", "算法：", None, QtGui.QApplication.UnicodeUTF8))
        self.label_encrypt_key.setText(QtGui.QApplication.translate("MainWindow", "秘钥：", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_encrypt.setText(QtGui.QApplication.translate("MainWindow", "加密", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_decrypt.setText(QtGui.QApplication.translate("MainWindow", "解密", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.encryptdecrpyt), QtGui.QApplication.translate("MainWindow", "加解密", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

