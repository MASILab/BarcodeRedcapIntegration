import sys
import redcap
from PyQt5.QtWidgets import QDesktopWidget,QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox,QFileDialog,QLabel,QApplication,QComboBox,QPlainTextEdit,QSplitter,QGroupBox
from PyQt5.QtGui import QIcon, QFont, QPixmap, QImage

from PyQt5.QtCore import *
import pandas as pd
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
from pyzbar.wrapper import ZBarSymbol
from playsound import playsound
import os
from datetime import datetime

from barcodeGenerator import BarcodeGenerator
from labelPrintHelper_mac import LabelPrintHelper_mac
from redcapHelper import RedcapHelper
from barcode_reader import Barcode_reader

class RedcapLabelwriterApp_v3(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'GCA Redcap LabelPrinter Toolkit_v1'
        self.left = 10
        self.top = 10
        self.width = 400 # 400
        self.height = 750
        self.initUI()
        # create redcap instance
        f_redcap_key = open("REDCAP_API_KEY.txt", "r")
        self.redcapExec = RedcapHelper(str(f_redcap_key.read()))
        
        # class vairables definition for getting value from GUI
        self.subjectId = ''
        self.studyType = ''
        self.processed_by = ''
        self.action_comment = ''
        self.barcode_id = ''
        self.freezer = ''
        self.rack = ''
        self.box_id = ''
        self.box_position = ''
        self.stats_type = ''
        
        self.th_webcam = Barcode_reader()
        self.th_webcam.change_pixmap.connect(self.set_webcam_image)
        self.th_webcam.found_qr.connect(self.set_scanned_id)

    def initUI(self):
        """
        UI vairable setup
        """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.centerOnScreen()
        
        myFont=QFont()
        myFont.setBold(True)
        
        # Create textbox
        self.label_subject_id = QLabel(self)
        self.label_subject_id.resize(130, 20)
        self.label_subject_id.move(20, 20)
        self.label_subject_id.setText('Subject ID')
        
        
        self.textbox_subject_id = QLineEdit(self)
        self.textbox_subject_id.resize(130,20)
        self.textbox_subject_id.move(150, 20)
        
        self.btn_get_next_subject = QPushButton('Next Subject', self)
        self.btn_get_next_subject.resize(120,30)
        self.btn_get_next_subject.move(280,15)
        
        
        self.label_study_type = QLabel(self)
        self.label_study_type.resize(130, 20)
        self.label_study_type.move(20, 45)
        self.label_study_type.setText('Study Type')
        

        self.cb_study_type = QComboBox(self)
        self.cb_study_type.resize(130,20)
        self.cb_study_type.move(150,45)
        self.cb_study_type.addItem('')
        self.cb_study_type.addItems(["CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"])    
        
        self.btn_get_subject_type = QPushButton('Subject Type', self)
        self.btn_get_subject_type.resize(120,30)
        self.btn_get_subject_type.move(280,40)
        
        self.btn_get_last_printed = QPushButton('Last Printed', self)
        self.btn_get_last_printed.resize(120,30)
        self.btn_get_last_printed.move(280,65)
        
        
        self.label_processed_by = QLabel(self)
        self.label_processed_by.resize(130, 20)
        self.label_processed_by.move(20, 70)
        self.label_processed_by.setText('Processed by')
             
        self.cb_processed_by = QComboBox(self)
        self.cb_processed_by.resize(130,20)
        self.cb_processed_by.move(150, 70)
        self.cb_processed_by.addItem('')
        self.cb_processed_by.addItems(["Sophie", "Regina", "Tyree"])  
                
        self.label_comment = QLabel(self)
        self.label_comment.resize(130, 20)
        self.label_comment.move(20, 95)
        self.label_comment.setText('Comment / Note')
        
        self.masi_label = QLabel(self)
        self.masi_label.resize(82, 65)
        self.masi_label.move(20, 115)
        pixmap = QPixmap('masi.png')
        self.masi_label.setPixmap(pixmap.scaled(82,65,Qt.KeepAspectRatio))
        
        self.plain_comment = QPlainTextEdit(self)
        self.plain_comment.resize(230,80)
        self.plain_comment.move(150, 95)
                
        self.label_new_pack = QLabel(self)
        self.label_new_pack.resize(360, 20)
        self.label_new_pack.move(20, 180)
        self.label_new_pack.setText('--------New Barcode Pack Action------------------------------------')
        self.label_new_pack.setFont(myFont)
        
        self.btn_gen_new_pack = QPushButton('Generate and Print new Barcode Pack', self)
        self.btn_gen_new_pack.resize(360,30)
        self.btn_gen_new_pack.move(20,205)
        
        self.label_single_barcode = QLabel(self)
        self.label_single_barcode.resize(360, 20)
        self.label_single_barcode.move(20, 240)
        self.label_single_barcode.setText('--------Single Barcode Action------------------------------------')
        self.label_single_barcode.setFont(myFont)
        
        self.label_barcode_id = QLabel(self)
        self.label_barcode_id.resize(130, 20)
        self.label_barcode_id.move(20, 265)
        self.label_barcode_id.setText('Barcode ID')
        
        # Create textbox
        self.textbox_barcode_id = QLineEdit(self)
        self.textbox_barcode_id.resize(145,20)
        self.textbox_barcode_id.move(105, 265)
        
        self.btn_scanned = QPushButton('Webcam', self)
        self.btn_scanned.resize(100,25)
        self.btn_scanned.move(280,260)     
        
        self.label_action_type = QLabel(self)
        self.label_action_type.resize(80, 30)
        self.label_action_type.move(20, 290)
        self.label_action_type.setText('Action List')

        self.cb_action_type = QComboBox(self)
        self.cb_action_type.resize(230,30)
        self.cb_action_type.move(100,290)
        self.cb_action_type.addItem('')
        self.cb_action_type.addItems(['Re-print',
                                      'DNA distributed to Vantage', 
                                      'DNA extracted and banked', 
                                      'Distributed to Lau',
                                      'Distributed to TPSR',
                                      'Paraffin blocks back from TPSR',
                                      'Distributed to Vantage'])   
        
        
        self.btn_sent_to = QPushButton('Run', self)
        self.btn_sent_to.resize(50,30)
        self.btn_sent_to.move(330,290)

        self.cam_label = QLabel(self)
        self.cam_label.resize(340, 200)
        self.cam_label.move(35, 325)
        
        pixmap = QPixmap('GCA.png')
        self.cam_label.setPixmap(pixmap)
        
        self.label_single_barcode = QLabel(self)
        self.label_single_barcode.resize(360, 20)
        self.label_single_barcode.move(20, 525)
        self.label_single_barcode.setText('--------Stats Summary------------------------------------')
        self.label_single_barcode.setFont(myFont)
        
        self.label_stats_type = QLabel(self)
        self.label_stats_type.resize(90, 20)
        self.label_stats_type.move(20, 550)
        self.label_stats_type.setText('Stats Type')
        
        self.cb_stats_type = QComboBox(self)
        self.cb_stats_type.resize(90,20)
        self.cb_stats_type.move(110,550)
        self.cb_stats_type.addItem('')
        self.cb_stats_type.addItems(["Project", "Subject", "Barcode"])
        
        self.label_stats_type = QLabel(self)
        self.label_stats_type.resize(90, 20)
        self.label_stats_type.move(310, 545)
        self.label_stats_type.setText('Version 1.0.0')
        
        self.label_contact_us = QLabel(self)
        self.label_contact_us.resize(90, 40)
        self.label_contact_us.move(310, 560)
        self.label_contact_us.setText(" <a href=\"mailto:shunxing.bao@vanderbilt.edu\">Contact us</a>")
        self.label_contact_us.setOpenExternalLinks(True)
        
        self.btn_stats = QPushButton('Print Stats', self)
        self.btn_stats.resize(180,30)
        self.btn_stats.move(20,570)

        self.plain_console = QPlainTextEdit(self)
        self.plain_console.resize(360,130)
        self.plain_console.move(20, 600)
        self.plain_console.setPlainText('--------------Output Log--------------')

        # connect button to on_click functions
        self.btn_get_next_subject.clicked.connect(self.getNextSubject)
        self.btn_gen_new_pack.clicked.connect(self.genPrintNewPack)
        self.btn_get_subject_type.clicked.connect(self.getSubjectType)
        self.btn_get_last_printed.clicked.connect(self.getLastPrinted)
        self.btn_sent_to.clicked.connect(self.setStatusSetAction)
        self.btn_scanned.clicked.connect(self.setStatusScanned)        
        self.btn_stats.clicked.connect(self.getBarcodeStats)
        # return enter event
        self.textbox_barcode_id.returnPressed.connect(self.getBarcodeFromScanner)
        # show the UI
        self.show()
    
        
    def centerOnScreen (self):
        '''centerOnScreen()
Centers the window on the screen.'''
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2)) 
        
    def getGUIFieldValue(self):
        """
        Get all filed values from UI for laziness
        """
        self.subjectId = self.textbox_subject_id.text()
            
        self.studyType = self.cb_study_type.currentText()
        self.processed_by = self.cb_processed_by.currentText()
        self.action_comment = self.plain_comment.toPlainText()
        self.barcode_id = self.textbox_barcode_id.text()
        self.action_type = self.cb_action_type.currentText()
        self.stats_type = self.cb_stats_type.currentText()
      
    @pyqtSlot()
    def getNextSubject(self):
        """
        The idea is to get next not printed subject id with sequential order. 
        Probably not very useful right now because patient may not show up in order
        """
        barcodeSubset =  self.redcapExec.getBarcodeSubset()
        next_subject_id = ''
  
        # if nothing printed
        if len(barcodeSubset) == 0 :
            next_subject_id = 1
        else:
            df = pd.DataFrame.from_dict(barcodeSubset)
            barcodeSubsetList  = df['barcode_sample_id'].values


            printBarcodeSubsetList = []
            for x in barcodeSubsetList:
                printBarcodeSubsetList.append(int(x[3:6]))

            printBarcodeSubsetList_np = np.asarray(printBarcodeSubsetList)
            printBarcodeSubsetList_np_unique = np.unique(printBarcodeSubsetList_np)
            
            if len(printBarcodeSubsetList_np_unique) is 0:
                next_subject_id = 1
            else:
                tmp = 0
                for i in printBarcodeSubsetList_np_unique:
                    if i - tmp == 1:
                        tmp = i
                        next_subject_id = i +  1
                    else:
                        next_subject_id = tmp +  1
                        break

        # Query from Sophie's redcap form to get existent patient entries       
        curSubj = self.redcapExec.getInputPatient()
        
        df = pd.DataFrame.from_dict(curSubj)
        record = df.loc[df['record_id_dem_endo'] == str(next_subject_id)]

        if len(record) is 0 or None:
            QMessageBox.about(self, "WARNING", '- Please create subject %s form first' % str(next_subject_id))
            return
            
        next_print_subject_id_verified = self.getPatentId(next_subject_id)
        self.textbox_subject_id.setText(next_print_subject_id_verified)
        
        studyType_redcap = record.get('redcap_event_name').values
        
        #"CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"
        if studyType_redcap == 'cd_arm_1':
            self.cb_study_type.setCurrentIndex(1)
        elif studyType_redcap == 'control_arm_1':
            self.cb_study_type.setCurrentIndex(2)
        elif studyType_redcap == 'cd_arm_2':
            self.cb_study_type.setCurrentIndex(3)
        elif studyType_redcap == 'control_arm_2':
            self.cb_study_type.setCurrentIndex(4)
        
        self.cb_study_type.repaint()
    
    @pyqtSlot()
    def getSubjectType(self):
        """
        Get selected subject id
        """
        self.getGUIFieldValue()
        if self.subjectId == '' or self.subjectId == None:
            QMessageBox.about(self, "WARNING", "Subject id is empty. Get subject %s type failed." % str(self.subjectId)  )
            return
        
        curSubj = self.redcapExec.getInputPatient()
        
        df = pd.DataFrame.from_dict(curSubj)
        record = df.loc[df['record_id_dem_endo'] == str(int(self.subjectId))]

        if len(record) is 0 or None:
            QMessageBox.about(self, "WARNING", '-- Please create subject %s form first' % str(int(self.subjectId)))
            return
        
        studyType_redcap = record.get('redcap_event_name').values
        
        #"CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"
        if studyType_redcap == 'cd_arm_1':
            self.cb_study_type.setCurrentIndex(1)
        elif studyType_redcap == 'control_arm_1':
            self.cb_study_type.setCurrentIndex(2)
        elif studyType_redcap == 'cd_arm_2':
            self.cb_study_type.setCurrentIndex(3)
        elif studyType_redcap == 'control_arm_2':
            self.cb_study_type.setCurrentIndex(4)
        
        self.cb_study_type.repaint()
    
    @pyqtSlot()
    def getLastPrinted(self):
        """
        Get last printed subject id
        """
        tmp_subset = self.redcapExec.project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id','barcode_action_type','barcode_processed_by'])
        barcodeSubset = self.redcapExec.getBarcodeSubset()
        if len(barcodeSubset) == 0: 
            QMessageBox.about(self, "WARNING", 'No subject got printed yet' )
            return

        df = pd.DataFrame.from_dict(tmp_subset)
        record = df.loc[df['barcode_action_type'] == 'printed']

        if len(record) is 0 or None:
            QMessageBox.about(self, "WARNING", 'Something wrong, please contact administrator!')
        else:
            record_list = record['barcode_sample_id'].tolist()
            last_print_subj = record_list[len(record_list)-1][3:6]
            
            last_record = df.iloc[-1,:]
            last_record_list = last_record.tolist()
            last_print_subj = last_record_list[2][3:6]
            last_processed_by = last_record_list[3]
            QMessageBox.about(self, "WARNING", 'Last printed subject: %s\nProcessed by: %s' % (str(last_print_subj),str(last_processed_by)))
    
    @pyqtSlot()
    def genPrintNewPack(self):
        """
        Generate and print new pack of barcodes
        """
        self.getGUIFieldValue()
        if self.subjectId == '' or self.subjectId == None:
            QMessageBox.about(self, "WARNING", "Subject id is empty. Generate / Print new pack for subject %s failed." % str(self.subjectId)  )
            return
        
        if len(self.subjectId) != 3:
            QMessageBox.about(self, "WARNING", "Subject id should be three digit. Please double-check" )
            return
        
        if self.studyType == '' or self.studyType == None:
            QMessageBox.about(self, "WARNING", "Study type is empty. Generate / Print new pack for subject %s failed." % str(self.subjectId)  )
            return
        
        if self.processed_by == '' or self.processed_by ==None:
            QMessageBox.about(self, "WARNING", "Please select current user." )
            return
        
        ###add constraint to restrict one patient can only be one type
        curSubj = self.redcapExec.getInputPatient()
        df = pd.DataFrame.from_dict(curSubj)
        record = df.loc[df['record_id_dem_endo'] == str(int(self.subjectId))]

        if len(record) is 0 or None:
            QMessageBox.about(self, "WARNING", "--- Please create subject %s form first" % str(self.subjectId)  )
            return

        studyType_redcap = record.get('redcap_event_name').values
        
        #"CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"
        if studyType_redcap == 'cd_arm_1':
            studyType_checker = 'CD_ENDO'
        elif studyType_redcap == 'control_arm_1':
            studyType_checker = 'CTL_ENDO'
        elif studyType_redcap == 'cd_arm_2':
            studyType_checker = 'CD_Surgery'
        elif studyType_redcap == 'control_arm_2':
            studyType_checker = 'CTL_Surgery'
            
        if studyType_checker != self.studyType:
            print(studyType_redcap)
            QMessageBox.about(self, "WARNING", "Study type for subject %s does not match. Should it be %s?" % (str(self.subjectId),str(studyType_checker)))
            return
        
        # all set, ready to generate barcode pack
        barcodeExec = BarcodeGenerator(self.subjectId,self.studyType)
        barcodeExec.execute()
        
        #can optimize - done?
        nextAvailActionId = self.redcapExec.getNextAvailActionId()
        tmp_barcode_list = barcodeExec.get_barcode_list() 

        #set generate action
        for tmp_barcode_id in tmp_barcode_list:
            ean8_code = barcodeExec.recordId_to_ean8(tmp_barcode_id)
            
            # generate ean8 code to make sure it matches our criteria
            if ean8_code is None:
                QMessageBox.about(self, "WARNING", "Something wrong with barcode id %s?" % (tmp_barcode_id))
                return
            
            self.printLabel(tmp_barcode_id, ean8_code)
            # add barcode ean8 code
            self.redcapExec.setPrintedAction(nextAvailActionId, tmp_barcode_id, self.studyType,self.processed_by,self.action_comment,ean8_code)
            nextAvailActionId += 1
        
        bool_update_redcap_sophie = self.redcapExec.update_REDCAP_SOPHIE(self.studyType,str(int(self.subjectId)),tmp_barcode_list)
        
        self.plain_comment.clear()
        
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.appendPlainText("\n\n%s\nGenerate new pack for subject %s DONE! Printing may takes time, please be patient.\nTotal barcodes to print: %s" 
                                           % (str(cur_date),str(self.subjectId),str(len(tmp_barcode_list))))
        self.plain_console.repaint()
        

    @pyqtSlot()
    def rePrintSingleLabel(self, tmp_ean8_code):
        """
        Reprint label
        """
        self.printLabel(self.barcode_id,tmp_ean8_code)
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.appendPlainText("\n\n%s\nReprint barcode %s DONE!" % (str(cur_date),str(self.barcode_id)))
    
    def printLabel(self, _barcode_id,_ean8_code):
        """
        Use dymo printer to print label 
        """
        tmpLabelPrint = LabelPrintHelper_mac(_barcode_id, _ean8_code)
        tmpLabelPrint.execute()
        return True 
        
    @pyqtSlot()
    def setStatusSetAction(self):
        """
        Set all actions of individual barcode
        """
        self.getGUIFieldValue()
        
        if self.barcode_id is '' or self.barcode_id is None:
            QMessageBox.about(self, "WARNING", "Barcode id is empty. Action failed. \n\n Please fill up barcode id box" )
            return
        
        if self.studyType == '' or self.studyType == None:
            QMessageBox.about(self, "WARNING", "Study type is empty. Do action for barcode %s failed." % str(self.barcode_id))
            return
        
        if self.processed_by == '' or self.processed_by ==None:
            QMessageBox.about(self, "WARNING", "Please select current user." )
            return
        
        # check barcode exists
        barcode_checker = self.redcapExec.ifBarcodeExist(self.barcode_id)
        if barcode_checker is False:
            QMessageBox.about(self, "WARNING", 
                              "Barcode %s is not found \n\n please generate barcode first" % str(self.barcode_id))
            return
        
    
        nextAvailActionId = self.redcapExec.getNextAvailActionId()
        self.subjectId = self.barcode_id[3:6]
        # add real barcode to ean8 code
        barcodeExec = BarcodeGenerator(self.subjectId,self.studyType)
        ean8_code = barcodeExec.recordId_to_ean8(self.barcode_id)

        if ean8_code is None:
            QMessageBox.about(self, "WARNING", "Something wrong with barcode id %s? \n Or please double-check your subject type" % (self.barcode_id))
            return
        
        # re-print has unique operation
        if self.action_type == 'Re-print':
            self.rePrintSingleLabel(ean8_code)
            
        self.redcapExec.setAction(nextAvailActionId, self.barcode_id, self.studyType,self.processed_by,self.action_type,self.action_comment,ean8_code)

        self.plain_comment.clear()
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.appendPlainText("\n\n%s\nbarcode %s action: %s DONE!" % (str(cur_date),str(self.barcode_id),self.action_type))
        self.plain_console.repaint()
        self.textbox_barcode_id.selectAll()
        
    @pyqtSlot(QImage)
    def set_webcam_image(self, image):
        """
        Get video image from webcam and print to GUI
        """
        self.cam_label.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot()
    def getBarcodeFromScanner(self):
        """
        Read barcode ean8 code from webcam
        """
        self.set_scanned_id(self.textbox_barcode_id.text())

    @pyqtSlot('QString')
    def set_scanned_id(self, scanned_id):
        """
        Convert ean8 id to real barcode id
        """
#         scanned_id = '30500020'
        barcodeExec = BarcodeGenerator()
    
        # hacking in case the input code is GCA blabla blabla      
        if scanned_id[0:3] == 'GCA':
            self.barcode_id = scanned_id
            scanned_id = barcodeExec.recordId_to_ean8(self.barcode_id)
        
        if barcodeExec.is_valid(str(scanned_id)) is False:
            QMessageBox.about(self, "WARNING", "Barcode is not valid(1). Please contact to administrator" )
            self.plain_console.repaint()
            return
        
        tmp_barcode_id = barcodeExec.ean8_to_recordId(scanned_id)
        if tmp_barcode_id is None:
            QMessageBox.about(self, "WARNING", "Barcode is not valid(2). Please contact to administrator" )
            self.plain_console.repaint()
            return
    
        barcode_checker = self.redcapExec.ifBarcodeExist(tmp_barcode_id)
        if barcode_checker is False:
            QMessageBox.about(self, "WARNING", 
                              "Barcode %s is not found \n\n please generate barcode first" % str(self.barcode_id))
            return
        
        
        # set GUI
        self.barcode_id = tmp_barcode_id
        self.textbox_barcode_id.setText(self.barcode_id)
        tmp_studyType = scanned_id[0:1]
        
        if tmp_studyType == '1':
            self.cb_study_type.setCurrentIndex(1)
        elif tmp_studyType == '2':
            self.cb_study_type.setCurrentIndex(2)
        elif tmp_studyType == '3':
            self.cb_study_type.setCurrentIndex(3)
        elif tmp_studyType == '4':
            self.cb_study_type.setCurrentIndex(4)

        nextAvailActionId = self.redcapExec.getNextAvailActionId()
        self.redcapExec.setScannedAction(nextAvailActionId, self.barcode_id, self.studyType,self.processed_by,self.action_comment,scanned_id)
        self.plain_comment.clear()
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.appendPlainText("\n\n%s\nSet barcode %s scanned status DONE!" % (str(cur_date),str(self.barcode_id)))
        self.plain_console.repaint()
                
    @pyqtSlot()
    def setStatusScanned(self):
        """
        Start a webcam thread
        """
        self.getGUIFieldValue()
        self.th_webcam.start()

    @pyqtSlot()   
    def getBarcodeStats(self):
        """
        Simple project / subject / barcode stats
        """
        self.getGUIFieldValue()
        
        if self.stats_type == 'Project':
            proj_stats = self.redcapExec.getProjectStats()
            curTime = datetime.now()
            cur_date = curTime.strftime('%Y-%m-%d %H:%M')
            self.plain_console.appendPlainText("\n\n%s\nProject Stats:\n%s" % (str(cur_date),proj_stats))
            
        elif self.stats_type == 'Subject':
            
            if self.subjectId == '' or self.subjectId == None:
                QMessageBox.about(self, "WARNING", "Subject id is empty. Get stats for subject %s failed." % str(self.subjectId)  )
                return
        
            self.getSubjectType()  # --> force to select correct subject type
            
            if self.studyType == '' or self.studyType == None:
                QMessageBox.about(self, "WARNING", "Study type is empty. Get stats for subject %s failed." % str(self.subjectId))
                return
            
            barcodeExec = BarcodeGenerator(self.subjectId,self.studyType)
            barcodeExec.execute()
            tmp_barcode_list = barcodeExec.get_barcode_list() 
            subj_stats = self.redcapExec.getSubjectStats(tmp_barcode_list)
            
            curTime = datetime.now()
            cur_date = curTime.strftime('%Y-%m-%d %H:%M')
            self.plain_console.appendPlainText("\n\n%s\nSubject %s Stats:\n%s" % (str(cur_date),self.subjectId, subj_stats))
         
        elif self.stats_type == 'Barcode':
            if self.barcode_id is '' or self.barcode_id is None:
                QMessageBox.about(self, "WARNING", "Barcode id is empty. Set scan status failed. \n\n Please fill up barcode id box" )
                return
            barcode_stats = self.redcapExec.getBarcodeStats(self.barcode_id)
            
            curTime = datetime.now()
            cur_date = curTime.strftime('%Y-%m-%d %H:%M')
            self.plain_console.appendPlainText("\n\n%s\nBarcode %s Stats is stored in :\n%s" % (str(cur_date),self.barcode_id, barcode_stats))

        self.plain_console.repaint()
        
            
    def getPatentId(self,cur_id):
        ""
        int_cur_id = int(cur_id)
        if int_cur_id < 10:
            return '00%s' % str(int_cur_id)
        elif int_cur_id < 100:
            return '0%s' % str(int_cur_id)
        else:
            return '%s' % str(int_cur_id)
        

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = RedcapLabelwriterApp_v3()
    sys.exit(app.exec_())
