# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Location.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from locationHelper import LocationHelper
from redcapHelper import RedcapHelper
from barcodeGenerator import BarcodeGenerator
from datetime import datetime
import pandas as pd
from barcode_reader import Barcode_reader

class LocationApp(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(860, 640)
       
        
        self.tableWidget_Group = QtWidgets.QTableWidget(Form)
        self.tableWidget_Group.setGeometry(QtCore.QRect(270, 10, 580, 620))
        self.tableWidget_Group.setObjectName("tableWidget_Group")
        self.tableWidget_Group.setColumnCount(5)
        self.total_rows = 200
        self.tableWidget_Group.setRowCount(self.total_rows)
        #width of table column
        self.tableWidget_Group.setColumnWidth(0, 150)

        
        for row in range (0,self.total_rows):
            item = self.createEmptyCellItem()
            self.tableWidget_Group.setVerticalHeaderItem(row, self.createEmptyCellItem())
        
        for col in range (0,5):
            item = self.createColumnIdItem()
            self.tableWidget_Group.setHorizontalHeaderItem(col, item)
        
        for row in range(0,self.total_rows):
            col_barcode_id = 0
            item = self.createEmptyCellAlignLeftItem()
            self.tableWidget_Group.setItem(row,col_barcode_id, item)    
                
            for col in range(1,5):
                item = self.createEmptyCellItem()
                self.tableWidget_Group.setItem(row,col, item)      
        
        self.btn_auto_fill = QtWidgets.QPushButton(Form)
        self.btn_auto_fill.setGeometry(QtCore.QRect(5, 210, 128, 40))
        self.btn_auto_fill.setObjectName("btn_auto_fill")
        self.btn_locatoin_sync = QtWidgets.QPushButton(Form)
        self.btn_locatoin_sync.setGeometry(QtCore.QRect(140, 210, 128, 40))
        self.btn_locatoin_sync.setObjectName("btn_locatoin_sync")
        
        # label =>>> INPUT
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 20, 40, 15))
        self.label.setObjectName("label")
        
        self.textbox_barcode_id = QtWidgets.QLineEdit(Form)
        self.textbox_barcode_id.setGeometry(QtCore.QRect(55, 18, 165, 20))
        self.textbox_barcode_id.setText("")
        self.textbox_barcode_id.setObjectName("textbox_barcode_id")  
        
        self.btn_scanned = QtWidgets.QPushButton(Form)
        self.btn_scanned.setGeometry(QtCore.QRect(220, 13, 50, 25))
        self.btn_scanned.setObjectName("btn_scanned")
        
        self.label_processed_by = QtWidgets.QLabel(Form)
        self.label_processed_by.resize(100, 20)
        self.label_processed_by.move(10, 50)
             
        self.cb_processed_by = QtWidgets.QComboBox(Form)
        self.cb_processed_by.resize(115,20)
        self.cb_processed_by.move(110, 50)
        self.cb_processed_by.addItem('')
        self.cb_processed_by.addItems(["Sophie", "Regina"]) 
        
        self.cam_label = QtWidgets.QLabel(Form)
        self.cam_label.setGeometry(QtCore.QRect(15, 80, 240, 130))
        self.cam_label.setObjectName("cam_label")
        
        self.plain_console = QtWidgets.QTextEdit(Form)
        self.plain_console.setGeometry(QtCore.QRect(10, 250, 251, 291))
        self.plain_console.setObjectName("plain_console")
        

        
        self.btn_clear_form = QtWidgets.QPushButton(Form)
        self.btn_clear_form.setGeometry(QtCore.QRect(140, 540, 128, 50))
        self.btn_clear_form.setObjectName("btn_clear_form")
        self.label_contact_us = QtWidgets.QLabel(Form)
        self.label_contact_us.setGeometry(QtCore.QRect(190, 610, 71, 16))
        self.label_contact_us.setObjectName("label_contact_us")
        self.label_version = QtWidgets.QLabel(Form)
        self.label_version.setGeometry(QtCore.QRect(10, 610, 81, 16))
        self.label_version.setObjectName("label_version")
        self.btn_destroy_barcode = QtWidgets.QPushButton(Form)
        self.btn_destroy_barcode.setGeometry(QtCore.QRect(5, 540, 128, 50))
        self.btn_destroy_barcode.setObjectName("btn_destroy_barcode")
        self.masi_label = QtWidgets.QLabel(Form)
        self.masi_label.setGeometry(QtCore.QRect(110, 590, 63, 50))
        self.masi_label.setObjectName("masi_label")

        self.retranslateUi(Form)
        
        # signal defined.
        
        self.btn_auto_fill.clicked.connect(self.autofillForm)
        self.btn_locatoin_sync.clicked.connect(self.locationSync)
        self.btn_destroy_barcode.clicked.connect(self.destroyBarcode)
        self.btn_clear_form.clicked.connect(self.clearFormContent)
        
        self.textbox_barcode_id.returnPressed.connect(self.getBarcodeFromScanner)
        
        self.th_webcam = Barcode_reader()
        self.th_webcam.change_pixmap.connect(self.set_webcam_image)
        self.th_webcam.found_qr.connect(self.set_scanned_id)
        self.btn_scanned.clicked.connect(self.setStatusScanned) 
        
        # global variable
        self.studyTypeDict = {} # a dictionary to store study type to avoid too many queries
        self._barcode_list=[]
        self.barcode_id = ''
        f_redcap_key = open("REDCAP_API_KEY.txt", "r")
        self.redcapExec = RedcapHelper(str(f_redcap_key.read()))
        
        QtWidgets.QMessageBox.about(Form, "WARNING", 
                              "Please select current user first please.")
            
        QtCore.QMetaObject.connectSlotsByName(Form)
    
    def set_webcam_image(self, image):
        """
        Get video image from webcam and print to GUI
        """
        self.cam_label.setPixmap(QtGui.QPixmap.fromImage(image).scaled(320,160,QtCore.Qt.KeepAspectRatio))
    
    def setStatusScanned(self):
        """
        Start a webcam thread
        """
        self.getGUIFieldValue()
        self.th_webcam.start()
         
    def getGUIFieldValue(self): # actually just need to get the processed by ....
        """
        Get all filed values from UI for laziness
        """
        self.processed_by = self.cb_processed_by.currentText()
        self.barcode_id = self.stringUpperLowerHack(self.textbox_barcode_id.text())
    
    def stringUpperLowerHack(self,tmp_text):
        # for Sophie, especially when she type words in Capital....
        # No matter what string got type, convert to Uppercase...
        tmp_text_upper = tmp_text.upper()
        
        tmpReplace = ''
        if 'FROZEN' in tmp_text_upper:
            tmpReplace = tmp_text_upper.replace("FROZEN", "Frozen")
            return tmpReplace 
        elif 'FIXED' in tmp_text_upper:
            tmpReplace = tmp_text_upper.replace("FIXED", "Fixed")
            return tmpReplace 
        elif 'FRESH' in tmp_text_upper:
            tmpReplace = tmp_text_upper.replace("FRESH", "Fresh")
            return tmpReplace 
        #nothing changed..
        print(tmp_text)
        return tmp_text      
        
    def destroyBarcode(self):
        col_barcode_id = 0
        for row in range(0, self.total_rows):
            tmpBarcodeId = self.tableWidget_Group.item(row, col_barcode_id).text()
            if tmpBarcodeId is not "":
                # get subject_id
                tmpBarcodeSubjectId = tmpBarcodeId[3:6]
                print('tmpBarcodeSubjectId:%s' % tmpBarcodeSubjectId)
                tmpSubjStudyType = self.getSubjStudyType(tmpBarcodeSubjectId)
                
                
                barcodeExec = BarcodeGenerator(tmpBarcodeSubjectId,tmpSubjStudyType)
                ean8_code = barcodeExec.recordId_to_ean8(tmpBarcodeId)
                tmp_custom_option = self.redcapExec.getSubjectLastestCustomOption(tmpBarcodeId,tmpBarcodeSubjectId)
                
                nextAvailActionId = self.redcapExec.getNextAvailActionId()
                
                
                tmpActionType = 'Barcode destroyed'
                # currently we don't have add comment field.... need to add in future....
                # update my valuable barcode redcap form :-)
                self.redcapExec.destroyBarcode(nextAvailActionId, tmpBarcodeId, tmpSubjStudyType,self.processed_by,tmpActionType,"",ean8_code,tmp_custom_option)
                
#                 if 'SR' in tmpBarcodeSubjectId or 'ST' in tmpBarcodeSubjectId or 'Frozen' in tmpBarcodeSubjectId:
#                     tmpActionType = 'stored in rack'
#                 elif 'Fresh' in tmpBarcodeSubjectId:
#                     tmpActionType = 'distributed to Lau'
#                 elif 'DNA' in tmpBarcodeSubjectId:
#                     tmpActionType = 'Relevant DNA field will be filled manually'
#                 elif 'Fixed' in tmpBarcodeSubjectId:
                    
                # only update for 
#                 (1) SR
#                 (2) ST
#                 (3) Frozen
#                 (4) Fresh - distribute to lau and update the table
#                 (5) - (6) fixed need to update the table
                bool_update_redcap_sophie = self.redcapExec.destroy_REDCAP_SOPHIE_FROM_LOCATION_APP(str(int(tmpBarcodeSubjectId)),tmpBarcodeId,tmpSubjStudyType)
        
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.append("\n%s\nDestroy Barcode %s  DONE!" % (str(cur_date),str(tmpBarcodeId)))
        #self.plain_console.repaint()
        self.plain_console_repaint()
        
    def locationSync(self):
        self.autofillForm()
        self.getGUIFieldValue()
        col_barcode_id = 0
        col_freezer = 1
        col_rack = 2
        col_box_id = 3
        col_box_pos = 4
        for row in range(0, self.total_rows):
            tmpBarcodeId = self.tableWidget_Group.item(row, col_barcode_id).text()
            if tmpBarcodeId is not "" and tmpBarcodeId is not None:
                # get subject_id
                
                tmpBarcodeSubjectId = tmpBarcodeId[3:6]
                print('INFO - sync tmpBarcodeSubjectId:%s' % tmpBarcodeSubjectId)
                tmpSubjStudyType = self.getSubjStudyType(tmpBarcodeSubjectId)
                
                tmpLocationTuple=[
                    self.tableWidget_Group.item(row, col_barcode_id).text(),
                    self.tableWidget_Group.item(row, col_freezer).text(),
                    self.tableWidget_Group.item(row, col_rack).text(),
                    self.tableWidget_Group.item(row, col_box_id).text(),
                    self.tableWidget_Group.item(row, col_box_pos).text()]
                
                barcodeExec = BarcodeGenerator(tmpBarcodeSubjectId,tmpSubjStudyType)
                ean8_code = barcodeExec.recordId_to_ean8(tmpBarcodeId)
                tmp_custom_option = self.redcapExec.getSubjectLastestCustomOption(tmpBarcodeId,tmpBarcodeSubjectId)
                
                nextAvailActionId = self.redcapExec.getNextAvailActionId()               
                
                tmpActionType = ''
                if 'SR' in tmpBarcodeId:
                    tmpActionType = 'Serum stored in rack'
                elif 'ST' in tmpBarcodeId:
                    tmpActionType = 'Stool stored in rack'
                elif 'Frozen' in tmpBarcodeId:
                    tmpActionType = 'Frozen stored in rack'
                elif 'Fresh' in tmpBarcodeId:
                    tmpActionType = 'Fresh distributed to Lau'
                elif 'DNA' in tmpBarcodeId:
                    tmpActionType = 'LocationApp record. Relevant DNA field will be filled manually.'
                elif 'Fixed' in tmpBarcodeId:
                    tmpActionType = 'LocationApp record. Relevant Fixed specimen field will be filled manually.'
                
                # currently we don't have add comment field.... need to add in future....
                # update my valuable barcode redcap form :-)
                self.redcapExec.execLocationAppSync(nextAvailActionId, tmpBarcodeId, tmpSubjStudyType,self.processed_by,tmpActionType,tmpLocationTuple,"",ean8_code,tmp_custom_option)
                
#                 if 'SR' in tmpBarcodeSubjectId or 'ST' in tmpBarcodeSubjectId or 'Frozen' in tmpBarcodeSubjectId:
#                     tmpActionType = 'stored in rack'
#                 elif 'Fresh' in tmpBarcodeSubjectId:
#                     tmpActionType = 'distributed to Lau'
#                 elif 'DNA' in tmpBarcodeSubjectId:
#                     tmpActionType = 'Relevant DNA field will be filled manually'
#                 elif 'Fixed' in tmpBarcodeSubjectId:
                    
                # only update for 
#                 (1) SR
#                 (2) ST
#                 (3) Frozen
#                 (4) Fresh - distribute to lau and update the table
#                 (5) - (6) fixed need to update the table

                tmpRackSophie = ''
                if self.tableWidget_Group.item(row, col_rack).text() == 'A':
                    tmpRackSophie = '1'
                elif self.tableWidget_Group.item(row, col_rack).text() == 'B':
                    tmpRackSophie = '2'
                elif self.tableWidget_Group.item(row, col_rack).text() == 'C':
                    tmpRackSophie = '3'
                    
                tmpLocationTuple=[
                    self.tableWidget_Group.item(row, col_barcode_id).text(),
                    '1', # always freezer c
                    tmpRackSophie,
                    self.tableWidget_Group.item(row, col_box_id).text(),
                    self.tableWidget_Group.item(row, col_box_pos).text()]
                
                bool_update_redcap_sophie = self.redcapExec.update_REDCAP_SOPHIE_FROM_LOCATION_APP(str(int(tmpBarcodeSubjectId)),tmpBarcodeId,tmpSubjStudyType,tmpLocationTuple) # to be continued.
    
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.append("\n%s\nsync Barcode list DONE!" % (str(cur_date)))
        #self.plain_console.repaint()
        self.plain_console_repaint()
                
        
    def getSubjStudyType(self,tmp_subject_id):
        """
        Get selected subject id
        """
#         self.getGUIFieldValue()
#         if tmp_subject_id == '' or tmp_subject_id == None:
#             #QMessageBox.about(self, "WARNING", "Subject id is empty. Get subject %s type failed." % str(self.subjectId)  )
#             return
        if tmp_subject_id in self.studyTypeDict:
            return self.studyTypeDict[tmp_subject_id]
        else:
    
            curSubj = self.redcapExec.getInputPatient()

            df = pd.DataFrame.from_dict(curSubj)
            record = df.loc[df['record_id_dem_endo'] == str(int(tmp_subject_id))]

            if len(record) is 0 or None:
                QMessageBox.about(self, "WARNING", '-- Please create subject %s form first' % str(int(tmp_subject_id)))
                return

            studyType_redcap = record.get('redcap_event_name').values

            #"CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"
            if studyType_redcap == 'cd_arm_1':
                self.studyTypeDict[tmp_subject_id] = "CD_ENDO"
            elif studyType_redcap == 'control_arm_1':
                self.studyTypeDict[tmp_subject_id] = "CTL_ENDO"
            elif studyType_redcap == 'cd_arm_2':
                self.studyTypeDict[tmp_subject_id] = "CD_Surgery"
            elif studyType_redcap == 'control_arm_2':
                self.studyTypeDict[tmp_subject_id] = "CTL_Surgery"

            return self.studyTypeDict[tmp_subject_id]
    
    def getBarcodeFromScanner(self):
        """
        Read barcode ean8 code from webcam
        """
        self.getGUIFieldValue()        
        if self.set_scanned_id(self.textbox_barcode_id.text()) is True:

            # fill self.barcode_id to the table
           # self.fillScannedBarcodeToTable(self.barcode_id)
            self.sortBarcodeIdList() # SHUNXING NEW FEATURE TO SORT THE TABLE
        
        
    def set_scanned_id(self, scanned_id):
        """
        Convert ean8 id to real barcode id
        """
#         scanned_id = '30500020'
        barcodeExec = BarcodeGenerator()
    
        # hacking in case the input code is GCA blabla blabla     
        # 
        tmp_barcode_id = ''
        # hacking because location app does not have self.subject field
        if scanned_id[0:3] == 'GCA':
            self.barcode_id = self.stringUpperLowerHack(scanned_id)
 #           scanned_id = barcodeExec.recordId_to_ean8(self.barcode_id)
        else:
            if barcodeExec.is_valid(str(scanned_id)) is False:
                QtWidgets.QMessageBox.about(Form, "WARNING", "Barcode is not valid(1). Please contact to administrator" )
                #self.plain_console.repaint()
                self.plain_console_repaint()
                return False

            tmp_barcode_id = barcodeExec.ean8_to_recordId(scanned_id)
            if tmp_barcode_id is None:
                QtWidgets.QMessageBox.about(Form, "WARNING", "Barcode is not valid(2). Please contact to administrator" )
                #self.plain_console.repaint()
                self.plain_console_repaint()
                return False       
        
            # set GUI
            self.barcode_id = tmp_barcode_id
            
        
        self.subjectId = self.barcode_id[3:6]
        tmp_custom_option = self.redcapExec.getSubjectLastestCustomOption(self.barcode_id,self.subjectId)
        if tmp_custom_option is False:
            QtWidgets.QMessageBox.about(Form, "WARNING", 
                              "Barcode %s is not found \n\n " % str(self.barcode_id))
            return False
        
       # self.textbox_barcode_id.setText(self.barcode_id)
    
        self.fillScannedBarcodeToTable(self.barcode_id)
        tmp_studyType = scanned_id[0:1]
        tmpstudyType = ''
        if tmp_studyType == '1':
            tmpstudyType = "CD_ENDO"
        elif tmp_studyType == '2':
            tmpstudyType = "CTL_ENDO"
        elif tmp_studyType == '3':
            tmpstudyType = "CD_Surgery"
        elif tmp_studyType == '4':
            tmpstudyType = "CTL_Surgery"

        nextAvailActionId = self.redcapExec.getNextAvailActionId()
#         self.redcapExec.setScannedAction(nextAvailActionId, self.barcode_id, tmpstudyType,self.processed_by,self.action_comment,scanned_id,tmp_custom_option)
        
        # remove action comment since it seems that useless for now ...
        self.redcapExec.setScannedAction(nextAvailActionId, self.barcode_id, tmpstudyType,self.processed_by,"",scanned_id,tmp_custom_option)
        

        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.append("\n\n%s\nSet barcode %s scanned status DONE!" % (str(cur_date),str(self.barcode_id)))
        #self.plain_console.repaint()
        self.plain_console_repaint()
        return True
    
    def setBarcodeList(self):
        self._barcode_list=[]
        
#        print(self.tableWidget_Group.item(190, 0).text())
        for row in range(0,self.total_rows):
#            print(row)
            tmpText = self.tableWidget_Group.item(row, 0).text()
#            print(tmpText)
            if tmpText is not "":
                self._barcode_list.append(tmpText)
            else:
                self._barcode_list.append("")
    
    def fillScannedBarcodeToTable(self,tmp_barcode_id):
        col_barcode_id = 0
        for row in range (0,self.total_rows):
            if self.tableWidget_Group.item(row, col_barcode_id).text() is "":
                item = self.createCellItemAlignLeftWithText(tmp_barcode_id)
                self.tableWidget_Group.setItem(row,col_barcode_id,item)
                break
                
        for row in range(0,self.total_rows):
            # fill location infos as empty if has new barcode scanned
           
            for col in range(1,5):
                item = self.createEmptyCellItem()
                self.tableWidget_Group.setItem(row,col, item) 
    
    def createEmptyCellItem(self):
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
#         font = QtGui.QFont()
#         font.setPointSize(10)
#         item.setFont(font)
        font = QtGui.QFont()
        font.setPointSize(12)    
        item.setFont(font)
        return item
    
    def createCellItemWithText(self,text):
        item = self.createEmptyCellItem()
        item.setText(text)
        return item 
    
    def createEmptyCellAlignLeftItem(self):
        item = QtWidgets.QTableWidgetItem()
#        item.setTextAlignment(QtCore.Qt.AlignCenter)
#         font = QtGui.QFont()
#         font.setPointSize(10)
#         item.setFont(font)
        font = QtGui.QFont()
        font.setPointSize(12)    
        item.setFont(font)
        return item
    
    def createCellItemAlignLeftWithText(self,text):
        item = self.createEmptyCellAlignLeftItem()
        item.setText(text)
        return item
    
    
    
#     def createRowIdItem(self):
#         return self.createEmptyCellItem()
    
    def createColumnIdItem(self):
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)    
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        return item
            
    def refreshBarcodeIdCell(self,tmpBarcodeList):
        tmpIdx = 0
        for row in range(0,self.total_rows):
            
            item = self.createCellItemAlignLeftWithText(tmpBarcodeList[tmpIdx])
            self.tableWidget_Group.setItem(row,0,item)
            tmpIdx += 1
            
    def barcodeListCustomSort(self,tmpBarcodeList):
        locationHelperExec = LocationHelper()
        barcodeList_customSort = locationHelperExec.barcodeListCustomSort(tmpBarcodeList)
        return barcodeList_customSort
#         # ADDFrozen always goes After regular TI And AC
#         # TI comes before AC
#         # logic:
#         # - TI -> FrozenOrder1
#         # - AC -> FrozenOrder2
#         # - ADDFrozenTI -> FrozenOrder3
#         # - ADDFrozenAC -> FrozenOrder4
        
#         # need to check ADD case, since Frozen contains in ADDFrozen... 
#         for i in range(0,len(tmpBarcodeList)):
#             tmpFrozenId = tmpBarcodeList[i]
            
#             if 'ADDFrozenAC' in tmpFrozenId:
                
#                 tmpReplace = tmpFrozenId.replace("ADDFrozenAC", "FrozenOrder4")
#                 tmpBarcodeList[i] = tmpReplace

#             elif 'ADDFrozenTI' in tmpFrozenId: 
#                 tmpReplace = tmpFrozenId.replace("ADDFrozenTI", "FrozenOrder3")
#                 tmpBarcodeList[i] = tmpReplace
                
#             elif 'AC' in tmpFrozenId: # hacking for Fresh and Fixed
#                 tmpReplace = tmpFrozenId.replace("AC", "Order2")
#                 tmpBarcodeList[i] = tmpReplace
                
#             elif 'TI' in tmpFrozenId: 
#                 tmpReplace = tmpFrozenId.replace("TI", "Order1")
#                 tmpBarcodeList[i] = tmpReplace
             
#             # for lazy, still use tmpFrozenId as variable..
#             elif 'SR10' in tmpFrozenId:
#                 tmpReplace = tmpFrozenId.replace("10", "9910")
#                 tmpBarcodeList[i] = tmpReplace
#             elif 'SR11' in tmpFrozenId:
#                 tmpReplace = tmpFrozenId.replace("11", "9911")
#                 tmpBarcodeList[i] = tmpReplace
                                 
#         tmpBarcodeList.sort() # regular String list sort
       
#         # Remove hacking substring and use original Barcode Id. 
#         for i in range(0,len(tmpBarcodeList)):
#             tmpFrozenId = tmpBarcodeList[i]
#             if 'FrozenOrder4' in tmpFrozenId:
#                 tmpReplace = tmpFrozenId.replace("FrozenOrder4", "ADDFrozenAC")
#                 tmpBarcodeList[i] = tmpReplace
#             elif 'FrozenOrder3' in tmpFrozenId: 
#                 tmpReplace = tmpFrozenId.replace("FrozenOrder3", "ADDFrozenTI")
#                 tmpBarcodeList[i] = tmpReplace
#             elif 'Order2' in tmpFrozenId: 
#                 tmpReplace = tmpFrozenId.replace("Order2", "AC")
#                 tmpBarcodeList[i] = tmpReplace
#             elif 'Order1' in tmpFrozenId: 
#                 tmpReplace = tmpFrozenId.replace("Order1", "TI")
#                 tmpBarcodeList[i] = tmpReplace
#             elif '9910' in tmpFrozenId:
#                 tmpReplace = tmpFrozenId.replace("9910", "10")
#                 tmpBarcodeList[i] = tmpReplace
#             elif '9911' in tmpFrozenId:
#                 tmpReplace = tmpFrozenId.replace("9911", "11")
#                 tmpBarcodeList[i] = tmpReplace
                      
#         return tmpBarcodeList
                
    def sortBarcodeIdList(self):
        self.setBarcodeList()
 #       print(len(self._barcode_list))

        tmpBarcodeSet = set(self._barcode_list) # for remove duplicate barcode
        barcodeListUniq  = list(tmpBarcodeSet)
        barcodeListUniqSort = self.barcodeListCustomSort(barcodeListUniq)

#        print(len(barcodeListUniqSort))
        # after sorting, the first string could be "", need to remove
        if barcodeListUniqSort[0] is "" and len(barcodeListUniqSort) != 1:
            barcodeListUniqSort.pop(0)

        #add null, 200 means we need 200 element...
        null_start_index=len(barcodeListUniqSort) + 1
        for i in range(null_start_index,201):
            barcodeListUniqSort.append("")
        
  #      print(len(barcodeListUniqSort))
        # add sorted id to interface.    
        self.refreshBarcodeIdCell(barcodeListUniqSort)
        self.textbox_barcode_id.clear()
        self.textbox_barcode_id.setFocus()
        self.tablesRepaint()
    
    def clearFormContent(self):
        self.tableWidget_Group.clearContents()
        for row in range (0,self.total_rows):
            item = self.createEmptyCellItem()
            self.tableWidget_Group.setVerticalHeaderItem(row, self.createEmptyCellItem())
        
        for col in range (0,5):
            item = self.createColumnIdItem()
            self.tableWidget_Group.setHorizontalHeaderItem(col, item)
        
        for row in range(0,self.total_rows):
            col_barcode_id = 0
            item = self.createEmptyCellAlignLeftItem()
            self.tableWidget_Group.setItem(row,col_barcode_id, item)    
                
            for col in range(1,5):
                item = self.createEmptyCellItem()
                self.tableWidget_Group.setItem(row,col, item) 
        self.tablesRepaint()
        
#         curTime = datetime.now()
#         cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        
#         self.plain_console.append("\n\n%s\nClear DONE!" % str(cur_date))
#         self.plain_console.repaint()
#         self.plain_console.moveCursor(QtGui.QTextCursor.End)

        
    def tablesRepaint(self): 
        self.tableWidget_Group.repaint()
        self.tableWidget_Group.clearSelection()

        self.plain_console_repaint()
        
        for row in range (0,self.total_rows):
            table1_idx = row + 1
            item = self.tableWidget_Group.verticalHeaderItem(row)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setText(str(table1_idx))
            
        item = self.tableWidget_Group.horizontalHeaderItem(0)
        item.setText( "Barcode ID")
        item = self.tableWidget_Group.horizontalHeaderItem(1)
        item.setText("Freezer")
        item = self.tableWidget_Group.horizontalHeaderItem(2)
        item.setText("Rack")
        item = self.tableWidget_Group.horizontalHeaderItem(3)
        item.setText("Box ID")
        item = self.tableWidget_Group.horizontalHeaderItem(4)
        item.setText("Box Pos.")
        
        
        self.textbox_barcode_id.setFocus()

#         self.tableWidget_Group.setItem(0,0,QtWidgets.QTableWidgetItem('nima'))
#         self.tableWidget_Group.repaint()
#         print(self.tableWidget_Group.itemAt(0, 0).text())
    
    def createTuple(self):
        tmpTuple=[]
        col_barcode_id = 0
        col_freezer = 1
        col_rack = 2
        col_box_id = 3
        col_box_pos = 4
        for row in range(0,self.total_rows):
            tmpLoc=[self.tableWidget_Group.item(row, col_barcode_id).text(),
                    self.tableWidget_Group.item(row, col_freezer).text(),
                    self.tableWidget_Group.item(row, col_rack).text(),
                    self.tableWidget_Group.item(row, col_box_id).text(),
                    self.tableWidget_Group.item(row, col_box_pos).text()]
            tmpTuple.append(tmpLoc)
              
        return tmpTuple
    
    def autofillForm(self):

        tmpTuple = self.createTuple()
        locationHelperExec = LocationHelper()
        
        
        newTuple = locationHelperExec.fillBoxLocationInfo(tmpTuple,self.total_rows)
        
        print('nima:%s' % str(newTuple))
        if newTuple is None:
            self.msgBoxWarning("Location input wrong")
            return
        self.setLocationTuple(newTuple)
        self.tablesRepaint()
        
    def msgBoxWarning(self,err_msg):
        if err_msg == "Location input wrong":
            QtWidgets.QMessageBox.about(Form, "WARNING", "Please check your location input. The box position should be in range [1,81]")
        
    def setLocationTuple(self,tmpTuple):
        tmpIdx = 0
        col_barcode_id = 0
        col_freezer = 1
        col_rack = 2
        col_box_id = 3
        col_box_pos = 4
        
        
        for row in range(0,self.total_rows):
            print(row)
            print(tmpIdx)
            print(tmpTuple[tmpIdx])
            
            item = self.createCellItemAlignLeftWithText(tmpTuple[tmpIdx][0])
            self.tableWidget_Group.setItem(row,col_barcode_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][1])
            self.tableWidget_Group.setItem(row,col_freezer,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][2])
            self.tableWidget_Group.setItem(row,col_rack,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][3])
            self.tableWidget_Group.setItem(row,col_box_id,item)
            
            item = self.createCellItemWithText(tmpTuple[tmpIdx][4])
            self.tableWidget_Group.setItem(row,col_box_pos,item)
            
            tmpIdx += 1
   
    def plain_console_repaint(self):
        self.plain_console.repaint()
        self.plain_console.moveCursor(QtGui.QTextCursor.End)
        
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
#         self.centerOnScreen()
        
        for row in range (0,self.total_rows):
            table1_idx = row + 1
            item = self.tableWidget_Group.verticalHeaderItem(row)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setText(_translate("Form", str(table1_idx)))
            
        item = self.tableWidget_Group.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Barcode ID"))
        item = self.tableWidget_Group.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Freezer"))
        item = self.tableWidget_Group.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Rack"))
        item = self.tableWidget_Group.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Box ID"))
        item = self.tableWidget_Group.horizontalHeaderItem(4)
        item.setText(_translate("Form", "Box Pos."))
        
        __sortingEnabled = self.tableWidget_Group.isSortingEnabled()
        self.tableWidget_Group.setSortingEnabled(False)
        self.tableWidget_Group.setSortingEnabled(__sortingEnabled)
        
        
        self.label.setText(_translate("Form", "INPUT"))
        self.btn_auto_fill.setText(_translate("Form", "Auto-Fill"))
        self.btn_locatoin_sync.setText(_translate("Form", "Location Sync"))
        self.btn_destroy_barcode.setText(_translate("Form", "Destroy Barcode"))
        self.btn_clear_form.setText(_translate("Form", "Clear Form"))
        
        self.btn_scanned.setText(_translate("Form", "cam"))
        self.plain_console.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.SF NS Text\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">-------------Output Log-------------</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p></body></html>"))
              
        self.label_contact_us.setText(_translate("Form", "<a href=\"mailto:shunxing.bao@vanderbilt.edu\">Contact us</a>"))
        self.label_version.setText(_translate("Form", "Version 1.0.0"))
        
        #self.cam_label.setText(_translate("Form", "Webcam"))
        pixmap = QtGui.QPixmap('GCA.png')
        self.cam_label.setPixmap(pixmap.scaled(320,160,QtCore.Qt.KeepAspectRatio))
        self.cam_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.masi_label.setText(_translate("Form", "MASI.png"))
        pixmap = QtGui.QPixmap('masi.png')
        self.masi_label.setPixmap(pixmap.scaled(80,40,QtCore.Qt.KeepAspectRatio))

        self.label_processed_by.setText(_translate("Form", "Processed by"))
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()

    resolution = QtWidgets.QDesktopWidget().screenGeometry()
    Form.move((resolution.width() / 2) - (860 / 2),
                  (resolution.height() / 2) - (640 / 2)) 
    
    ui = LocationApp()
    
    ui.setupUi(Form)
    
    Form.setWindowTitle('GCA Redcap Location Toolkit_v1')
    Form.show()
    
    sys.exit(app.exec_())