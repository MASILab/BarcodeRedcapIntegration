# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Location.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from locationHelper import LocationHelper

class LocationApp(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1331, 640)
        self.tableWidget_Group1 = QtWidgets.QTableWidget(Form)
        self.tableWidget_Group1.setGeometry(QtCore.QRect(270, 10, 210, 620))
        self.tableWidget_Group1.setObjectName("tableWidget_Group1")
        self.tableWidget_Group1.setColumnCount(3)
        self.tableWidget_Group1.setRowCount(20)
        #width of table column
        self.tableWidget_Group1.setColumnWidth(0, 130)
        self.tableWidget_Group1.setColumnWidth(1, 28)
        self.tableWidget_Group1.setColumnWidth(2, 28)
        
        self.tableWidget_Group2 = QtWidgets.QTableWidget(Form)
        self.tableWidget_Group2.setGeometry(QtCore.QRect(480, 10, 210, 620))        
        self.tableWidget_Group2.setObjectName("tableWidget_Group2")
        self.tableWidget_Group2.setColumnCount(3)
        self.tableWidget_Group2.setRowCount(20)
        #width of table column
        self.tableWidget_Group2.setColumnWidth(0, 130)
        self.tableWidget_Group2.setColumnWidth(1, 28)
        self.tableWidget_Group2.setColumnWidth(2, 28)
        
        self.tableWidget_Group3 = QtWidgets.QTableWidget(Form)
        self.tableWidget_Group3.setGeometry(QtCore.QRect(690, 10, 210, 620))        
        self.tableWidget_Group3.setObjectName("tableWidget_Group3")
        self.tableWidget_Group3.setColumnCount(3)
        self.tableWidget_Group3.setRowCount(20)
        #width of table column
        self.tableWidget_Group3.setColumnWidth(0, 130)
        self.tableWidget_Group3.setColumnWidth(1, 28)
        self.tableWidget_Group3.setColumnWidth(2, 28)
        
        self.tableWidget_Group4 = QtWidgets.QTableWidget(Form)
        self.tableWidget_Group4.setGeometry(QtCore.QRect(900, 10, 210, 620))        
        self.tableWidget_Group4.setObjectName("tableWidget_Group4")
        self.tableWidget_Group4.setColumnCount(3)
        self.tableWidget_Group4.setRowCount(20)
        #width of table column
        self.tableWidget_Group4.setColumnWidth(0, 130)
        self.tableWidget_Group4.setColumnWidth(1, 28)
        self.tableWidget_Group4.setColumnWidth(2, 28)
        
        self.tableWidget_Group5 = QtWidgets.QTableWidget(Form)
        self.tableWidget_Group5.setGeometry(QtCore.QRect(1110, 10, 215, 620))        
        self.tableWidget_Group5.setObjectName("tableWidget_Group5")
        self.tableWidget_Group5.setColumnCount(3)
        self.tableWidget_Group5.setRowCount(20)
        #width of table column
        self.tableWidget_Group5.setColumnWidth(0, 130)
        self.tableWidget_Group5.setColumnWidth(1, 28)
        self.tableWidget_Group5.setColumnWidth(2, 28)
        
        for row in range (0,20):
            item = self.createEmptyCellItem()
            self.tableWidget_Group1.setVerticalHeaderItem(row, self.createEmptyCellItem())
            
            item = self.createEmptyCellItem()
            self.tableWidget_Group2.setVerticalHeaderItem(row, item)
             
            item = self.createEmptyCellItem()
            self.tableWidget_Group3.setVerticalHeaderItem(row, item)

            item = self.createEmptyCellItem()
            self.tableWidget_Group4.setVerticalHeaderItem(row, item)
            
            item = self.createEmptyCellItem()
            self.tableWidget_Group5.setVerticalHeaderItem(row, item)
        
        for col in range (0,3):
            item = self.createColumnIdItem()
            self.tableWidget_Group1.setHorizontalHeaderItem(col, item)
            
            item = self.createColumnIdItem()
            self.tableWidget_Group2.setHorizontalHeaderItem(col, item)
            
            item = self.createColumnIdItem()       
            self.tableWidget_Group3.setHorizontalHeaderItem(col, item)
            
            item = self.createColumnIdItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)            
            self.tableWidget_Group4.setHorizontalHeaderItem(col, item)
            
            item = self.createColumnIdItem()           
            self.tableWidget_Group5.setHorizontalHeaderItem(col, item)
            
        
        for row in range(0,20):
            for col in range(0,3):
                item = self.createRowIdItem()
                self.tableWidget_Group1.setItem(row,col, item)

                item = self.createRowIdItem()
                self.tableWidget_Group2.setItem(row,col, item)
 
                item = self.createRowIdItem()
                self.tableWidget_Group3.setItem(row,col, item)

                item = self.createRowIdItem()
                self.tableWidget_Group4.setItem(row,col, item)

                item = self.createRowIdItem()
                self.tableWidget_Group5.setItem(row,col, item)       
        
        self.btn_auto_fill = QtWidgets.QPushButton(Form)
        self.btn_auto_fill.setGeometry(QtCore.QRect(10, 200, 100, 50))
        self.btn_auto_fill.setObjectName("btn_auto_fill")
        self.textbox_barcode_id = QtWidgets.QLineEdit(Form)
        self.textbox_barcode_id.setGeometry(QtCore.QRect(59, 15, 120, 20))
        self.textbox_barcode_id.setText("")
        self.textbox_barcode_id.setObjectName("textbox_barcode_id")   
        
        self.cam_label = QtWidgets.QLabel(Form)
        self.cam_label.setGeometry(QtCore.QRect(20, 60, 241, 131))
        self.cam_label.setObjectName("cam_label")
        self.btn_scanned = QtWidgets.QPushButton(Form)
        self.btn_scanned.setGeometry(QtCore.QRect(180, 10, 80, 25))
        self.btn_scanned.setObjectName("btn_scanned")
        self.plain_console = QtWidgets.QTextEdit(Form)
        self.plain_console.setGeometry(QtCore.QRect(10, 250, 251, 291))
        self.plain_console.setObjectName("plain_console")
        
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 20, 41, 16))
        self.label.setObjectName("label")
        self.btn_locatoin_sync = QtWidgets.QPushButton(Form)
        self.btn_locatoin_sync.setGeometry(QtCore.QRect(150, 200, 100, 50))
        self.btn_locatoin_sync.setObjectName("btn_locatoin_sync")
        self.btn_clear_form = QtWidgets.QPushButton(Form)
        self.btn_clear_form.setGeometry(QtCore.QRect(150, 540, 100, 50))
        self.btn_clear_form.setObjectName("btn_clear_form")
        self.label_contact_us = QtWidgets.QLabel(Form)
        self.label_contact_us.setGeometry(QtCore.QRect(190, 610, 71, 16))
        self.label_contact_us.setObjectName("label_contact_us")
        self.label_version = QtWidgets.QLabel(Form)
        self.label_version.setGeometry(QtCore.QRect(10, 610, 81, 16))
        self.label_version.setObjectName("label_version")
        self.btn_destroy_barcode = QtWidgets.QPushButton(Form)
        self.btn_destroy_barcode.setGeometry(QtCore.QRect(10, 540, 100, 50))
        self.btn_destroy_barcode.setObjectName("btn_destroy_barcode")
        self.masi_label = QtWidgets.QLabel(Form)
        self.masi_label.setGeometry(QtCore.QRect(110, 590, 63, 50))
        self.masi_label.setObjectName("masi_label")

        self.retranslateUi(Form)
        self.btn_scanned.clicked.connect(self.sortBarcodeIdList) # need to remove in future
        self.btn_auto_fill.clicked.connect(self.autofillForm)
        self.btn_clear_form.clicked.connect(self.clearFormContent)
        
        # global variable
        self._barcode_list=[]
        
        QtCore.QMetaObject.connectSlotsByName(Form)
    
    def setBarcodeList(self):
        self._barcode_list=[]
        
        for row in range(0,20):
            
            tmpText = self.tableWidget_Group1.item(row, 0).text()
            if tmpText is not "":
                self._barcode_list.append(tmpText)
            else:
                self._barcode_list.append("")
            
        for row in range(0,20):
            tmpText = self.tableWidget_Group2.item(row, 0).text()
            if tmpText is not "":
                self._barcode_list.append(tmpText)
            else:
                self._barcode_list.append("")
            
        for row in range(0,20):
            tmpText = self.tableWidget_Group3.item(row, 0).text()
            if tmpText is not "":
                self._barcode_list.append(tmpText)
            else:
                self._barcode_list.append("")      
            
        for row in range(0,20):
            tmpText = self.tableWidget_Group4.item(row, 0).text()
            if tmpText is not "":
                self._barcode_list.append(tmpText)
            else:
                self._barcode_list.append("")  
                            
        for row in range(0,20):
            tmpText = self.tableWidget_Group5.item(row, 0).text()
            if tmpText is not "":
                self._barcode_list.append(tmpText)
            else:
                self._barcode_list.append("")
            
            
    def createEmptyCellItem(self):
        item = QtWidgets.QTableWidgetItem()
#             item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        return item
    
    def createCellItemWithText(self,text):
        item = self.createEmptyCellItem()
        item.setText(text)
        return item
    
    def createRowIdItem(self):
        return self.createEmptyCellItem()
    
    def createColumnIdItem(self):
        item = QtWidgets.QTableWidgetItem()
#             item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)    
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        return item
            
    def refreshBarcodeIdCell(self,tmpBarcodeList):
        tmpIdx = 0
        for row in range(0,20):
            item = self.createCellItemWithText(tmpBarcodeList[tmpIdx])
            self.tableWidget_Group1.setItem(row,0,item)
            tmpIdx += 1
        
        tmpIdx -= 1
        for row in range(0,20):
            item = self.createCellItemWithText(tmpBarcodeList[tmpIdx])
            self.tableWidget_Group2.setItem(row,0,item)
            tmpIdx += 1
        
        tmpIdx -= 1
        for row in range(0,20):
            item = self.createCellItemWithText(tmpBarcodeList[tmpIdx])
            self.tableWidget_Group3.setItem(row,0,item)
            tmpIdx += 1
        
        tmpIdx -= 1
        for row in range(0,20):
            item = self.createCellItemWithText(tmpBarcodeList[tmpIdx])
            self.tableWidget_Group4.setItem(row,0,item)
            tmpIdx += 1
        
        tmpIdx -= 1
        for row in range(0,20):
            item = self.createCellItemWithText(tmpBarcodeList[tmpIdx])
            self.tableWidget_Group5.setItem(row,0,item)
            tmpIdx += 1
            
    def barcodeListCustomSort(self,tmpBarcodeList):
        # ADDFrozen always goes After regular TI And AC
        # TI comes before AC
        # logic:
        # - TI -> FrozenOrder1
        # - AC -> FrozenOrder2
        # - ADDFrozenTI -> FrozenOrder3
        # - ADDFrozenAC -> FrozenOrder4
        
        # need to check ADD case, since Frozen contains in ADDFrozen... 
        for i in range(0,len(tmpBarcodeList)):
            tmpFrozenId = tmpBarcodeList[i]
            
            if 'ADDFrozenAC' in tmpFrozenId:
                
                tmpReplace = tmpFrozenId.replace("ADDFrozenAC", "FrozenOrder4")
                tmpBarcodeList[i] = tmpReplace

            elif 'ADDFrozenTI' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("ADDFrozenTI", "FrozenOrder3")
                tmpBarcodeList[i] = tmpReplace
                
            elif 'AC' in tmpFrozenId: # hacking for Fresh and Fixed
                tmpReplace = tmpFrozenId.replace("AC", "Order2")
                tmpBarcodeList[i] = tmpReplace
                
            elif 'TI' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("TI", "Order1")
                tmpBarcodeList[i] = tmpReplace
                                 
        tmpBarcodeList.sort() # regular String list sort
       
        # Remove hacking substring and use original Barcode Id. 
        for i in range(0,len(tmpBarcodeList)):
            tmpFrozenId = tmpBarcodeList[i]
            if 'FrozenOrder4' in tmpFrozenId:
                tmpReplace = tmpFrozenId.replace("FrozenOrder4", "ADDFrozenAC")
                tmpBarcodeList[i] = tmpReplace
            elif 'FrozenOrder3' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("FrozenOrder3", "ADDFrozenTI")
                tmpBarcodeList[i] = tmpReplace
            elif 'Order2' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("Order2", "AC")
                tmpBarcodeList[i] = tmpReplace
            elif 'Order1' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("Order1", "TI")
                tmpBarcodeList[i] = tmpReplace
                      
        return tmpBarcodeList
                
    def sortBarcodeIdList(self):
        self.setBarcodeList()
        print(len(self._barcode_list))

        tmpBarcodeSet = set(self._barcode_list) # for remove duplicate barcode
        barcodeListUniq  = list(tmpBarcodeSet)
        barcodeListUniqSort = self.barcodeListCustomSort(barcodeListUniq)

        # after sorting, the first string could be "", need to remove
        if barcodeListUniqSort[0] is "":
            barcodeListUniqSort.pop(0)

        #add null, 100 means we need 100 element...
        null_start_index=len(barcodeListUniqSort)+1
        for i in range(null_start_index,100):
            barcodeListUniqSort.append("")

        # add sorted id to interface.    
        self.refreshBarcodeIdCell(barcodeListUniqSort)
        self.textbox_barcode_id.clear()
        self.textbox_barcode_id.setFocus()
        self.tablesRepaint()
    
    def clearFormContent(self):
        self.tableWidget_Group1.clearContents()
        self.tableWidget_Group2.clearContents()
        self.tableWidget_Group3.clearContents()
        self.tableWidget_Group4.clearContents()
        self.tableWidget_Group5.clearContents()
        self.tablesRepaint()

        
    def tablesRepaint(self): 
        self.tableWidget_Group1.repaint()
        self.tableWidget_Group2.repaint()
        self.tableWidget_Group3.repaint()
        self.tableWidget_Group4.repaint()
        self.tableWidget_Group5.repaint()
        self.tableWidget_Group1.clearSelection()
        self.tableWidget_Group2.clearSelection()
        self.tableWidget_Group3.clearSelection()
        self.tableWidget_Group4.clearSelection()
        self.tableWidget_Group5.clearSelection()
        self.plain_console.repaint()
        self.textbox_barcode_id.setFocus()

#         self.tableWidget_Group1.setItem(0,0,QtWidgets.QTableWidgetItem('nima'))
#         self.tableWidget_Group1.repaint()
#         print(self.tableWidget_Group1.itemAt(0, 0).text())
    
    def createTuple(self):
        tmpTuple=[]
        col_barcode_id = 0
        col_box_id = 1
        col_box_pos = 2
        for row in range(0,20):
            tmpLoc=[self.tableWidget_Group1.item(row, col_barcode_id).text(),
                    self.tableWidget_Group1.item(row, col_box_id).text(),
                    self.tableWidget_Group1.item(row, col_box_pos).text()]
            tmpTuple.append(tmpLoc)
        
        for row in range(0,20):
            tmpLoc=[self.tableWidget_Group2.item(row, col_barcode_id).text(),
                    self.tableWidget_Group2.item(row, col_box_id).text(),
                    self.tableWidget_Group2.item(row, col_box_pos).text()]
            tmpTuple.append(tmpLoc)
            
        for row in range(0,20):
            tmpLoc=[self.tableWidget_Group3.item(row, col_barcode_id).text(),
                    self.tableWidget_Group3.item(row, col_box_id).text(),
                    self.tableWidget_Group3.item(row, col_box_pos).text()]
            tmpTuple.append(tmpLoc)
        
        for row in range(0,20):
            tmpLoc=[self.tableWidget_Group4.item(row, col_barcode_id).text(),
                    self.tableWidget_Group4.item(row, col_box_id).text(),
                    self.tableWidget_Group4.item(row, col_box_pos).text()]
            tmpTuple.append(tmpLoc)
            
        for row in range(0,20):
            tmpLoc=[self.tableWidget_Group5.item(row, col_barcode_id).text(),
                    self.tableWidget_Group5.item(row, col_box_id).text(),
                    self.tableWidget_Group5.item(row, col_box_pos).text()]
            tmpTuple.append(tmpLoc)        
        return tmpTuple
    
    def autofillForm(self):
        tmpTuple = self.createTuple()
        locationHelperExec = LocationHelper()
        print(tmpTuple[0][0])
        newTuple = locationHelperExec.fillBoxLocationInfo(tmpTuple)
        if newTuple is None:
            self.msgBoxWarning("Location input wrong")
            return
        self.setLocationTuple(newTuple)
        self.tablesRepaint()
        
    def msgBoxWarning(self,err_msg):
        if err_msg == "Location input wrong":
            FQtWidgets.QMessageBox.about(Form, "WARNING", "Please check your location input. The box position should be in range [1,81]")
        
    def setLocationTuple(self,tmpTuple):
        tmpIdx = 0
        col_barcode_id = 0
        col_box_id = 1
        col_box_pos = 2
        
        for row in range(0,20):
            item = self.createCellItemWithText(tmpTuple[tmpIdx][0])
            self.tableWidget_Group1.setItem(row,col_barcode_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][1])
            self.tableWidget_Group1.setItem(row,col_box_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][2])
            self.tableWidget_Group1.setItem(row,col_box_pos,item)
            
            tmpIdx += 1
        
        tmpIdx -= 1
        for row in range(0,20):
            item = self.createCellItemWithText(tmpTuple[tmpIdx][0])
            self.tableWidget_Group2.setItem(row,col_barcode_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][1])
            self.tableWidget_Group2.setItem(row,col_box_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][2])
            self.tableWidget_Group2.setItem(row,col_box_pos,item)
            tmpIdx += 1
        
        tmpIdx -= 1
        for row in range(0,20):
            item = self.createCellItemWithText(tmpTuple[tmpIdx][0])
            self.tableWidget_Group3.setItem(row,col_barcode_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][1])
            self.tableWidget_Group3.setItem(row,col_box_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][2])
            self.tableWidget_Group3.setItem(row,col_box_pos,item)
            tmpIdx += 1
        
        tmpIdx -= 1
        for row in range(0,20):
            item = self.createCellItemWithText(tmpTuple[tmpIdx][0])
            self.tableWidget_Group4.setItem(row,col_barcode_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][1])
            self.tableWidget_Group4.setItem(row,col_box_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][2])
            self.tableWidget_Group4.setItem(row,col_box_pos,item)
            tmpIdx += 1
        
        tmpIdx -= 1
        for row in range(0,20):
            item = self.createCellItemWithText(tmpTuple[tmpIdx][0])
            self.tableWidget_Group5.setItem(row,col_barcode_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][1])
            self.tableWidget_Group5.setItem(row,col_box_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][2])
            self.tableWidget_Group5.setItem(row,col_box_pos,item)
            tmpIdx += 1
    
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
#         self.centerOnScreen()
        
        for row in range (0,20):
            table1_idx = row + 1
            item = self.tableWidget_Group1.verticalHeaderItem(row)
            item.setText(_translate("Form", str(table1_idx)))
            
            table2_idx = row + 21
            item = self.tableWidget_Group2.verticalHeaderItem(row)
            item.setText(_translate("Form", str(table2_idx)))
            
            table3_idx = row + 41
            item = self.tableWidget_Group3.verticalHeaderItem(row)
            item.setText(_translate("Form", str(table3_idx)))
        
            table4_idx = row + 61
            item = self.tableWidget_Group4.verticalHeaderItem(row)
            item.setText(_translate("Form", str(table4_idx)))
            
            table5_idx = row + 81
            item = self.tableWidget_Group5.verticalHeaderItem(row)
            item.setText(_translate("Form", str(table5_idx)))
            
        item = self.tableWidget_Group1.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Barcode ID"))
        item = self.tableWidget_Group1.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Box"))
        item = self.tableWidget_Group1.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Pos"))
        __sortingEnabled = self.tableWidget_Group1.isSortingEnabled()
        self.tableWidget_Group1.setSortingEnabled(False)
        self.tableWidget_Group1.setSortingEnabled(__sortingEnabled)
        
            
        item = self.tableWidget_Group2.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Barcode ID"))
        item = self.tableWidget_Group2.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Box"))
        item = self.tableWidget_Group2.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Pos"))
        __sortingEnabled = self.tableWidget_Group2.isSortingEnabled()
        self.tableWidget_Group2.setSortingEnabled(False)
        self.tableWidget_Group2.setSortingEnabled(__sortingEnabled)
    
        item = self.tableWidget_Group3.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Barcode ID"))
        item = self.tableWidget_Group3.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Box"))
        item = self.tableWidget_Group3.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Pos"))
        __sortingEnabled = self.tableWidget_Group3.isSortingEnabled()
        self.tableWidget_Group3.setSortingEnabled(False)
        self.tableWidget_Group3.setSortingEnabled(__sortingEnabled)
                
        item = self.tableWidget_Group4.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Barcode ID"))
        item = self.tableWidget_Group4.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Box"))
        item = self.tableWidget_Group4.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Pos"))
        __sortingEnabled = self.tableWidget_Group4.isSortingEnabled()
        self.tableWidget_Group4.setSortingEnabled(False)
        self.tableWidget_Group4.setSortingEnabled(__sortingEnabled)        
        
        item = self.tableWidget_Group5.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Barcode ID"))
        item = self.tableWidget_Group5.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Box"))
        item = self.tableWidget_Group5.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Pos"))
        __sortingEnabled = self.tableWidget_Group5.isSortingEnabled()
        self.tableWidget_Group5.setSortingEnabled(False)
        self.tableWidget_Group5.setSortingEnabled(__sortingEnabled)
        
        self.label.setText(_translate("Form", "INPUT"))
        self.btn_auto_fill.setText(_translate("Form", "auto-fill"))
        self.btn_locatoin_sync.setText(_translate("Form", "Location\nSync"))
        self.btn_destroy_barcode.setText(_translate("Form", "Destroy\n"
"Barcode"))
        self.btn_clear_form.setText(_translate("Form", "Clear\n"
"Form"))
        
        self.btn_scanned.setText(_translate("Form", "webcam"))
        self.plain_console.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.SF NS Text\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">-------------Output Log-------------</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p></body></html>"))
              
        self.label_contact_us.setText(_translate("Form", "<a href=\"mailto:shunxing.bao@vanderbilt.edu\">Contact us</a>"))
        self.label_version.setText(_translate("Form", "Version 1.0.0"))
        
        self.cam_label.setText(_translate("Form", "Webcam"))
        pixmap = QtGui.QPixmap('GCA.png')

        self.cam_label.setPixmap(pixmap)
        
        self.masi_label.setText(_translate("Form", "MASI.png"))
        pixmap = QtGui.QPixmap('masi.png')
        self.masi_label.setPixmap(pixmap.scaled(80,40,QtCore.Qt.KeepAspectRatio))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    
    resolution = QtWidgets.QDesktopWidget().screenGeometry()
    Form.move((resolution.width() / 2) - (1331 / 2),
                  (resolution.height() / 2) - (640 / 2)) 
    ui = LocationApp()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())