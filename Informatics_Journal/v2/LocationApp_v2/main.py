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
from barcode_reader_imac import Barcode_reader_imac
import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins'
os.environ["PATH"] += ":/usr/local/bin:/usr/local/bin/gs"

class LocationApp(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
#        Form.resize(880, 640)
        Form.resize(1600,880)
        self.font_imac = QtGui.QFont('Laksaman',15)
        self.font_imac_small = QtGui.QFont('Laksaman',12)
 #       self.font_imac.setPointSize(15)
#         self.font_imac_bold = QtGui.QFont('Laksaman',15)
#         #font.setPointSize(12)    
#         self.font_imac_bold.setBold(True)
#         self.font_imac_bold.setWeight(150)
        
        self.tableWidget_Group = QtWidgets.QTableWidget(Form)
        self.tableWidget_Group.setGeometry(QtCore.QRect(350, 10, 720, 820))
        self.tableWidget_Group.setObjectName("tableWidget_Group")
        self.tableWidget_Group.setColumnCount(5)
        self.total_rows = 200
        self.tableWidget_Group.setRowCount(self.total_rows)
        #width of table column
        self.tableWidget_Group.setColumnWidth(0, 250)

        
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
        self.btn_auto_fill.setGeometry(QtCore.QRect(20, 340, 310, 50))
        self.btn_auto_fill.setObjectName("btn_auto_fill")
        self.btn_auto_fill.setFont(self.font_imac)

        self.btn_locatoin_sync = QtWidgets.QPushButton(Form)
        self.btn_locatoin_sync.setGeometry(QtCore.QRect(20, 410, 310, 50))
        self.btn_locatoin_sync.setObjectName("btn_locatoin_sync")
        self.btn_locatoin_sync.setFont(self.font_imac)
        
        self.label_comment = QtWidgets.QLabel(Form)
        self.label_comment.resize(300, 20)
        self.label_comment.move(20, 470)
        self.label_comment.setFont(self.font_imac_small)
        
        self.plain_comment = QtWidgets.QPlainTextEdit(Form)
        self.plain_comment.resize(310,180)
        self.plain_comment.move(20, 490)
        self.plain_comment.setFont(self.font_imac_small)
        
        self.btn_destroy_barcode = QtWidgets.QPushButton(Form)
        self.btn_destroy_barcode.setGeometry(QtCore.QRect(20, 690, 310, 50))
        self.btn_destroy_barcode.setObjectName("btn_destroy_barcode")
        self.btn_destroy_barcode.setFont(self.font_imac)
        
        self.btn_clear_form = QtWidgets.QPushButton(Form)
        self.btn_clear_form.setGeometry(QtCore.QRect(20, 760, 310, 50))
        self.btn_clear_form.setObjectName("btn_clear_form")
        self.btn_clear_form.setFont(self.font_imac)
        
        # label =>>> INPUT
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 25, 60, 20))
        self.label.setObjectName("label")
        font = QtGui.QFont('Laksaman')
        font.setPointSize(15)    
        font.setBold(True)
        font.setWeight(150)        
        self.label.setFont(font)
        
        self.textbox_barcode_id = QtWidgets.QLineEdit(Form)
        self.textbox_barcode_id.setGeometry(QtCore.QRect(70, 15, 220, 35))
        self.textbox_barcode_id.setText("")
        self.textbox_barcode_id.setObjectName("textbox_barcode_id")  
        self.textbox_barcode_id.setFont(self.font_imac)

        self.btn_scanned = QtWidgets.QPushButton(Form)
        self.btn_scanned.setGeometry(QtCore.QRect(290, 15, 50, 35))
        self.btn_scanned.setObjectName("btn_scanned")
        self.btn_scanned.setFont(self.font_imac)

        
        self.label_processed_by = QtWidgets.QLabel(Form)
        self.label_processed_by.resize(130, 20)
        self.label_processed_by.move(10, 65)
        self.label_processed_by.setFont(self.font_imac)
             
        self.cb_processed_by = QtWidgets.QComboBox(Form)
        self.cb_processed_by.resize(200,35)
        self.cb_processed_by.move(140, 60)
        self.cb_processed_by.addItem('')
        self.cb_processed_by.addItems(["Sophie", "Regina"]) 
        self.cb_processed_by.setFont(self.font_imac)
        self.cb_processed_by.setCurrentIndex(0)
        
        self.label_biopsies_type = QtWidgets.QLabel(Form)
        self.label_biopsies_type.resize(130, 20)
        self.label_biopsies_type.move(10, 285)
        self.label_biopsies_type.setFont(self.font_imac)
        
        self.cb_biopsies_type = QtWidgets.QComboBox(Form)
        self.cb_biopsies_type.resize(200,30)
        self.cb_biopsies_type.move(140, 280)
        self.cb_biopsies_type.addItem('')
        self.cb_biopsies_type.addItems(["Right colon - RC", "Transverse colon - TC", 'Left colon - LC', 'Sigmoid colon - SC', 'Rectum - R']) 
        self.cb_biopsies_type.setFont(self.font_imac)
        self.cb_biopsies_type.setCurrentIndex(0)

        self.cam_label = QtWidgets.QLabel(Form)
        self.cam_label.setGeometry(QtCore.QRect(10, 100, 330, 150))
        self.cam_label.setObjectName("cam_label")
        
        
        self.plain_console = QtWidgets.QTextEdit(Form)
        self.plain_console.setGeometry(QtCore.QRect(1080, 10, 440, 730))
        self.plain_console.setObjectName("plain_console")
        self.plain_console.setFont(self.font_imac)
        
        self.label_contact_us = QtWidgets.QLabel(Form)
        self.label_contact_us.setGeometry(QtCore.QRect(1400, 760, 100, 50))
        self.label_contact_us.setObjectName("label_contact_us")
        self.label_contact_us.setFont(self.font_imac)
        
        self.label_version = QtWidgets.QLabel(Form)
        self.label_version.setGeometry(QtCore.QRect(1080, 760, 150, 50))
        self.label_version.setObjectName("label_version")
        self.label_version.setFont(self.font_imac)
        
        self.masi_label = QtWidgets.QLabel(Form)
        self.masi_label.setGeometry(QtCore.QRect(1240, 720, 150, 150))
        self.masi_label.setObjectName("masi_label")

        self.retranslateUi(Form)
        
        # signal defined.
        
        self.btn_auto_fill.clicked.connect(self.autofillForm)
        self.btn_locatoin_sync.clicked.connect(self.locationSync)
        self.btn_destroy_barcode.clicked.connect(self.destroyBarcode)
        self.btn_clear_form.clicked.connect(self.clearFormContent)
        
        self.textbox_barcode_id.returnPressed.connect(self.getBarcodeFromScanner)
        
        self.th_webcam = Barcode_reader_imac()
        self.th_webcam.change_pixmap.connect(self.set_webcam_image)
        self.th_webcam.found_qr.connect(self.set_scanned_id)
        self.btn_scanned.clicked.connect(self.setStatusScanned) 
        
        # global variable
        self.studyTypeDict = {} # a dictionary to store study type to avoid too many queries
        self._barcode_list=[]
        self.barcode_id = ''
        f_redcap_key = open("/app/v2/LocationApp_v2/REDCAP_API_KEY.txt", "r")
        redcap_key = str(f_redcap_key.read())
        if '\n' in redcap_key:
            redcap_key = redcap_key.replace('\n','')
        self.redcapExec = RedcapHelper(redcap_key)
        #self.redcapExec = RedcapHelper(str(f_redcap_key.read()))
        
        ### THE following two operations are for code optimzations, avoid duplicate Redcap query
        self.redcapExec.getBarcodeSubset_StudyType_Action_CustomOption() # for one time query...the program is not strict sync...may have risk if multiple users run program at the same time...
        self.nextAvailActionId = self.redcapExec.getCurrentActionId()
    
#        QtWidgets.QMessageBox.about(Form, "WARNING", 
#                              "Please select current user first please.")
            
        QtCore.QMetaObject.connectSlotsByName(Form)
        
    def refresh_redcap(self):
        self.redcapExec.getBarcodeSubset_StudyType_Action_CustomOption() # for one time query...the program is not strict sync...may have risk if multiple users run program at the same time...
        self.nextAvailActionId = self.redcapExec.getCurrentActionId()
        
    def set_webcam_image(self, image):
        """
        Get video image from webcam and print to GUI
        """
        self.cam_label.setPixmap(QtGui.QPixmap.fromImage(image).scaled(480,240,QtCore.Qt.KeepAspectRatio))
    
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
        self.biopsies_type = self.cb_biopsies_type.currentText()
        self.barcode_id = self.stringUpperLowerHack(self.textbox_barcode_id.text())
    
    def stringUpperLowerHack(self,tmp_text):
        # for Sophie, especially when she type words in Capital....
        # No matter what string got type, convert to Uppercase...
        tmp_text_upper = tmp_text.upper()
        
        tmpReplace = ''

#         print(tmp_text_upper)
        
        if 'DOD' in tmp_text_upper:
            tmpReplace = tmp_text_upper.replace('DOD','DoD')
            
        if 'ADDFROZEN' in tmp_text_upper:
            tmpReplace = tmpReplace.replace("ADDFROZEN", "AddFrozen")
            return tmpReplace
        elif 'FIXED' in tmp_text_upper:
            tmpReplace = tmpReplace.replace("FIXED", "Fixed")
            return tmpReplace
        elif 'FRESH' in tmp_text_upper:
            tmpReplace = tmpReplace.replace("FRESH", "Fresh")
            return tmpReplace
        elif 'FROZEN' in tmp_text_upper:
            tmpReplace = tmpReplace.replace("FROZEN", "Frozen")
            return tmpReplace
        
        print(tmp_text)    
        return tmp_text       
        
    def destroyBarcode(self):
        to_import = []
        col_barcode_id = 0
        
#        self.redcapExec.getBarcodeSubset_StudyType_Action_CustomOption() # for one time query...
        
        for row in range(0, self.total_rows):
            tmpBarcodeId = self.tableWidget_Group.item(row, col_barcode_id).text()
            if tmpBarcodeId is not "":
                # get subject_id
                tmpBarcodeSubjectId = tmpBarcodeId[4:7]
                
                # remove for reduce duplicate query...
               # tmpSubjStudyType = self.getSubjStudyType(tmpBarcodeSubjectId) 
 
                tmpSubjStudyType,tmp_action_type,tmp_custom_option = self.redcapExec.getSubjectLastestActionAndCustomOption(tmpBarcodeId,tmpBarcodeSubjectId)
                
                barcodeExec = BarcodeGenerator(tmpBarcodeSubjectId,tmpSubjStudyType)
                
                ean8_code = barcodeExec.recordId_to_ean8(tmpBarcodeId)
                print('tmpBarcodeSubjectId:%s' % tmpBarcodeSubjectId)
          
                        
                if 'destroyed' in tmp_action_type:
                
                    reply = QtWidgets.QMessageBox.question(Form, u'destroy barcode',
                                         u'Barcode %s should be destroyed, do you want to destroy it again?' % str(tmpBarcodeId), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

                    if reply == QtWidgets.QMessageBox.No:
                        continue;
                        
                if 'rack' in tmp_action_type:
                    reply = QtWidgets.QMessageBox.question(Form, u'destroy barcode',
                                         u'Barcode %s should be storaged, do you want to destroy it?' % str(tmpBarcodeId), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

                    if reply == QtWidgets.QMessageBox.No:
                        continue;
                        
                if 'Lau' in tmp_action_type or 'TPSR' in tmp_action_type or 'Vantage' in tmp_action_type:
                    reply = QtWidgets.QMessageBox.question(Form, u'destroy barcode',
                                         u'Barcode %s should be distributed, do you want to destroy it?' % str(tmpBarcodeId), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

                    if reply == QtWidgets.QMessageBox.No:
                        continue;
                    
                
                self.nextAvailActionId += 1
                
                tmpActionType = 'Barcode destroyed'
                # currently we don't have add comment field.... need to add in future....
                # update my valuable barcode redcap form :-)
                self.redcapExec.destroyBarcode(self.nextAvailActionId, tmpBarcodeId, tmpSubjStudyType,self.processed_by,tmpActionType,self.plain_comment.toPlainText(),ean8_code,tmp_custom_option)
######SHUNXING DOD
                self.redcapExec.destroy_REDCAP_SOPHIE_FROM_LOCATION_APP('DoD_%s' % str((tmpBarcodeSubjectId)),tmpBarcodeId,tmpSubjStudyType)
######SHUNXING DOD
   
        # new feature to do bulk import to the REDCap
        self.redcapExec.redcap_import_records()
        self.refresh_redcap()
       
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.append("\n%s\nDestroy Barcode DONE!" % (str(cur_date)))
        #self.plain_console.repaint()
        self.plain_console_repaint()
        self.cb_biopsies_type.setCurrentIndex(0)
        
    def locationSync(self):
        to_import = []
        self.autofillForm()
        self.getGUIFieldValue()
        col_barcode_id = 0
        col_freezer = 1
        col_rack = 2
        col_box_id = 3
        col_box_pos = 4
        
#         self.redcapExec.getBarcodeSubset_StudyType_Action_CustomOption() # for one time query...
        
        for row in range(0, self.total_rows):
            tmpBarcodeId = self.tableWidget_Group.item(row, col_barcode_id).text()
            if tmpBarcodeId is not "" and tmpBarcodeId is not None:
                # get subject_id
                
                tmpBarcodeSubjectId = tmpBarcodeId[4:7]
                print('INFO - sync tmpBarcodeSubjectId:%s' % tmpBarcodeSubjectId)
                               
                tmpLocationTuple=[
                    self.tableWidget_Group.item(row, col_barcode_id).text(),
                    self.tableWidget_Group.item(row, col_freezer).text(),
                    self.tableWidget_Group.item(row, col_rack).text(),
                    self.tableWidget_Group.item(row, col_box_id).text(),
                    self.tableWidget_Group.item(row, col_box_pos).text()]
                
 #               tmpSubjStudyType = self.getSubjStudyType(tmpBarcodeSubjectId)
                tmpSubjStudyType, tmp_action_type, tmp_custom_option = self.redcapExec.getSubjectLastestActionAndCustomOption(tmpBarcodeId,tmpBarcodeSubjectId)
                
                barcodeExec = BarcodeGenerator(tmpBarcodeSubjectId,tmpSubjStudyType)
                ean8_code = barcodeExec.recordId_to_ean8(tmpBarcodeId)
                
                print(tmpBarcodeId)
                print(tmp_action_type)
                if 'destroyed' in tmp_action_type:
                
                    reply = QtWidgets.QMessageBox.question(Form, u'destroy barcode',
                                         u'Barcode %s should be destroyed, location sync failed...' % str(tmpBarcodeId), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

                    if reply == QtWidgets.QMessageBox.No:
                        continue;
                        
                if 'rack' in tmp_action_type:
                    reply = QtWidgets.QMessageBox.question(Form, u'destroy barcode',
                                         u'Barcode %s should be storaged, do you want to store it again?' % str(tmpBarcodeId), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

                    if reply == QtWidgets.QMessageBox.No:
                        continue;
                        
                if 'Lau' in tmp_action_type or 'TPSR' in tmp_action_type or 'Vantage' in tmp_action_type:
                    
                    reply = QtWidgets.QMessageBox.question(Form, u'destroy barcode',
                                         u'Barcode %s should be distributed, do you want to distribute it again?' % str(tmpBarcodeId), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

                    if reply == QtWidgets.QMessageBox.No:
                        continue;        
            
                self.nextAvailActionId += 1             
                
                tmpActionType = ''
                if 'SR' in tmpBarcodeId:
                    tmpActionType = 'Serum stored in rack'
#                 elif 'ST' in tmpBarcodeId:
#                     tmpActionType = 'Stool stored in rack'
                elif 'Frozen' in tmpBarcodeId:
                    tmpActionType = 'Frozen stored in rack'
                elif 'Fresh' in tmpBarcodeId:
                    tmpActionType = 'Fresh distributed to Lau'
                elif 'DNA' in tmpBarcodeId:
                    tmpActionType = 'DNA distributed to Vantage. Relevant DNA field will be filled manually.'
                elif 'Fixed' in tmpBarcodeId:
                    tmpActionType = 'Fixed distributed to TPSR. Relevant Fixed specimen field will be filled manually.'
                
                # currently we don't have add comment field.... need to add in future....
                # update my valuable barcode redcap form :-)
                
 
               # self.biopsies_type = 
                if 'Frozen' in tmpBarcodeId or 'Fresh' in tmpBarcodeId or 'Fixed' in tmpBarcodeId:
                    if self.biopsies_type == '' or self.biopsies_type ==None:
                        QtWidgets.QMessageBox.about(Form, "WARNING", "Please Choose Frozen biopsies type." )
                        return
                
                self.redcapExec.execLocationAppSync(self.nextAvailActionId, tmpBarcodeId, tmpSubjStudyType,self.processed_by,tmpActionType,tmpLocationTuple,self.plain_comment.toPlainText(),ean8_code,tmp_custom_option,self.biopsies_type)
                
                    
                # only update for 
#                 (1) SR
#                 (2) Frozen
#                 (4) Fresh -> update ID
#                 (5) Fixed -> update ID
#                 (6) No need for DNA

                #For rack 
                tmpRackSophie = ''
                if self.tableWidget_Group.item(row, col_rack).text() == 'A':
                    tmpRackSophie = '1'
                elif self.tableWidget_Group.item(row, col_rack).text() == 'B':
                    tmpRackSophie = '2'
                elif self.tableWidget_Group.item(row, col_rack).text() == 'C':
                    tmpRackSophie = '3'
                    
                tmpLocationTuple=[
                    self.tableWidget_Group.item(row, col_barcode_id).text(),
                    '1', # always freezer FFFFFFFFFFFF
                    tmpRackSophie,
                    self.tableWidget_Group.item(row, col_box_id).text(),
                    self.tableWidget_Group.item(row, col_box_pos).text()]
######SHUNXING DOD                
                self.redcapExec.update_REDCAP_SOPHIE_FROM_LOCATION_APP(
                    'DoD_%s' % str((tmpBarcodeSubjectId)),tmpBarcodeId,tmpSubjStudyType,tmpLocationTuple,self.biopsies_type) # to be continued. - DONE?
######SHUNXING DOD

        # new feature to do bulk import to the REDCap
        self.redcapExec.redcap_import_records()
        self.refresh_redcap()
        
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.append("\n%s\nsync Barcode list DONE!" % (str(cur_date)))
        #self.plain_console.repaint()
        self.plain_console_repaint()
        self.cb_biopsies_type.setCurrentIndex(0)
                
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
        if scanned_id[0:3] == 'DoD' or scanned_id[0:3] == 'DOD':
            print('why not')
            self.barcode_id = self.stringUpperLowerHack(scanned_id)
            print('why not???')
            print(self.barcode_id)
            print('wocao????')
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
            
        
        self.subjectId = self.barcode_id[4:7]
#         self.redcapExec.getBarcodeSubset_StudyType_Action_CustomOption() # for one time query...
        tmp_study_type,tmp_action_type,tmp_custom_option = self.redcapExec.getSubjectLastestActionAndCustomOption(self.barcode_id,self.subjectId)
        
        if tmp_custom_option is False:
            print('########')
            print(self.barcode_id)
            print(self.subjectId)
            print('########')
            self.refresh_redcap()
            tmp_study_type,tmp_action_type,tmp_custom_option = self.redcapExec.getSubjectLastestActionAndCustomOption(self.barcode_id,self.subjectId)
#             QtWidgets.QMessageBox.about(Form, "WARNING", 
#                               "Barcode %s is not found \n\n " % str(self.barcode_id))
#             return False
        
        # a hack way to refresh ...
        
        if tmp_custom_option is False:
            QtWidgets.QMessageBox.about(Form, "WARNING", 
                              "Barcode %s is not found \n\n " % str(self.barcode_id))
            return False
        
       # self.textbox_barcode_id.setText(self.barcode_id)
        # initialize barcodeExec class variables
        barcodeExec._subject_id = self.subjectId
        barcodeExec._studyType = tmp_study_type
        
        self.fillScannedBarcodeToTable(self.barcode_id)
#         tmp_studyType = scanned_id[0:1]
#         tmpstudyType = ''
#         if tmp_studyType == '1':
#             tmpstudyType = "CD_ENDO"
#         elif tmp_studyType == '2':
#             tmpstudyType = "CTL_ENDO"
#         elif tmp_studyType == '3':
#             tmpstudyType = "CD_Surgery"
#         elif tmp_studyType == '4':
#             tmpstudyType = "CTL_Surgery"

        self.nextAvailActionId += 1
#         self.redcapExec.setScannedAction(nextAvailActionId, self.barcode_id, tmpstudyType,self.processed_by,self.action_comment,scanned_id,tmp_custom_option)
        
        # remove action comment since it seems that useless for now ...
        # once we confirmed the input id exists, we can safely convert the id to ean8 code.
        # This is only for manually input...
        if scanned_id[0:3] == 'DoD':
            scanned_id = barcodeExec.recordId_to_ean8(self.barcode_id)
            
        self.redcapExec.setScannedAction(self.nextAvailActionId, self.barcode_id, tmp_study_type,self.processed_by,self.plain_comment.toPlainText(),scanned_id,tmp_custom_option)
        
        curTime = datetime.now()
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
        item.setFont(self.font_imac)
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
        item.setFont(self.font_imac)
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
        font = QtGui.QFont('Laksaman')
        font.setPointSize(15)    
        font.setBold(True)
        font.setWeight(150)   
        
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
        self.redcapExec.redcap_import_records()
        self.refresh_redcap()
        reply = QtWidgets.QMessageBox.question(Form, u'clear form',
                                     u'Are you sure to clear the form?', QtWidgets.QMessageBox.Yes |
                                     QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
      
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
            self.cb_biopsies_type.setCurrentIndex(0)
        
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
            QtWidgets.QMessageBox.about(Form, "WARNING", "Please check your location input. The Frozen Speciman box position should be in range [1,81].\nThe Serum Speciman box position should be in range [1,81].\n")
        
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
        self.plain_comment.clear()
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
        self.btn_clear_form.setText(_translate("Form", "Refresh/Clear Form"))
        self.label_comment.setText(_translate("Form","------ Comment / Note ------"))
        
        self.btn_scanned.setText(_translate("Form", "cam"))
        self.plain_console.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.SF NS Text\'; font-size:16pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">-----------------Output Log-----------------</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p></body></html>"))
              
        self.label_contact_us.setText(_translate("Form", "<a href=\"mailto:shunxing.bao@vanderbilt.edu\">Contact us</a>"))
        self.label_version.setText(_translate("Form", "Version 1.0.0"))
        
        #self.cam_label.setText(_translate("Form", "Webcam"))
        pixmap = QtGui.QPixmap('/app/v2/LocationApp_v2/VUMC.png')
        self.cam_label.setPixmap(pixmap.scaled(480,240,QtCore.Qt.KeepAspectRatio))
        self.cam_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.masi_label.setText(_translate("Form", "/app/v2/LocationApp_v2/MASI.png"))
        pixmap = QtGui.QPixmap('/app/v2/LocationApp_v2/masi.png')
        self.masi_label.setPixmap(pixmap.scaled(160,80,QtCore.Qt.KeepAspectRatio))

        self.label_processed_by.setText(_translate("Form", "Processed by"))
        self.label_biopsies_type.setText(_translate("Form", "Biopsies Type"))
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()

    resolution = QtWidgets.QDesktopWidget().screenGeometry()
    Form.move( int((resolution.width() / 2) - (1600 / 2)),
                  int((resolution.height() / 2) - (800 / 2))) 
    
    ui = LocationApp()
    
    ui.setupUi(Form)
    
    Form.setWindowTitle('DoD Redcap Location Toolkit_v1')
    Form.show()
    
    sys.exit(app.exec_())
