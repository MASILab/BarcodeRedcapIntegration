import sys
import redcap
from PyQt5.QtWidgets import QDesktopWidget,QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox,QFileDialog,QLabel,QApplication,QComboBox,QPlainTextEdit,QSplitter,QGroupBox, QButtonGroup, QRadioButton
from PyQt5.QtGui import QIcon, QFont, QPixmap, QImage,QTextCursor

from PyQt5.QtCore import *
import pandas as pd
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
from pyzbar.wrapper import ZBarSymbol
from playsound import playsound
import os
from datetime import datetime
import shutil

from barcodeGenerator import BarcodeGenerator
from labelPrintHelper_mac import LabelPrintHelper_mac
from redcapHelper import RedcapHelper
from barcode_reader import Barcode_reader

class PrinterApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'GCA Redcap LabelPrinter Toolkit_v1'
        self.left = 10
        self.top = 10
        self.width = 800 # 400
        self.height = 585 # 585
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
        self.custom_option = ''
        
        self.th_webcam = Barcode_reader()
        self.th_webcam.change_pixmap.connect(self.set_webcam_image)
        self.th_webcam.found_qr.connect(self.set_scanned_id)
        
        curDir = os.getcwd()
        barcode_tmp_path = curDir + '/tmp'
        try:
            os.mkdir(barcode_tmp_path)
        except OSError:
            print ("Creation of the directory %s failed" % barcode_tmp_path)
        
        # setup default label printer use system command. 
        os.system('lpoptions -d DYMO_LabelWriter_450')

    def initUI(self):
        """
        UI vairable setup
        """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.centerOnScreen()
        
        myFont=QFont()
        myFont.setBold(True)
       
        self.label_setup = QLabel(self)
        self.label_setup.resize(360, 20)
        self.label_setup.move(20, 15)
        self.label_setup.setText('--------Subject Setup------------------------------------')
        self.label_setup.setFont(myFont)        
        
        self.label_subject_id = QLabel(self)
        self.label_subject_id.resize(130, 20)
        self.label_subject_id.move(20, 40)
        self.label_subject_id.setText('Subject ID')
        
        
        self.textbox_subject_id = QLineEdit(self)
        self.textbox_subject_id.resize(130,20)
        self.textbox_subject_id.move(150, 40)
        
        self.btn_get_next_subject = QPushButton('Next Subject', self)
        self.btn_get_next_subject.resize(120,30)
        self.btn_get_next_subject.move(280,35)
        
        
        self.label_study_type = QLabel(self)
        self.label_study_type.resize(130, 20)
        self.label_study_type.move(20, 65)
        self.label_study_type.setText('Study Type')
        

        self.cb_study_type = QComboBox(self)
        self.cb_study_type.resize(130,20)
        self.cb_study_type.move(150,65)
        self.cb_study_type.addItem('')
        self.cb_study_type.addItems(["CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"])    
        
        self.btn_get_subject_type = QPushButton('Subject Type', self)
        self.btn_get_subject_type.resize(120,30)
        self.btn_get_subject_type.move(280,60)
        
        self.label_processed_by = QLabel(self)
        self.label_processed_by.resize(130, 20)
        self.label_processed_by.move(20, 90)
        self.label_processed_by.setText('Custom Option:')
        
        self.cb_option_type = QComboBox(self)
        self.cb_option_type.resize(230,20)
        self.cb_option_type.move(150,90)
        self.cb_option_type.addItem('')
        self.cb_option_type.addItems(["Default",
                                      "Need extra FROZEN specimens", 
                                     "No FRESH specimens, NO extra FROZEN specimens", 
                                     "No FRESH specimens, ADD extra FROZEN specimens"])
             
        self.label_processed_by = QLabel(self)
        self.label_processed_by.resize(130, 20)
        self.label_processed_by.move(20, 115)
        self.label_processed_by.setText('Processed by')
             
        self.cb_processed_by = QComboBox(self)
        self.cb_processed_by.resize(130,20)
        self.cb_processed_by.move(150, 115)
        self.cb_processed_by.addItem('')
        self.cb_processed_by.addItems(["Sophie", "Regina","Eric"])  
#        self.cb_processed_by.setCurrentIndex(1)
        
        self.btn_get_last_printed = QPushButton('Last Printed', self)
        self.btn_get_last_printed.resize(120,30)
        self.btn_get_last_printed.move(280,110)
                
        self.label_comment = QLabel(self)
        self.label_comment.resize(130, 20)
        self.label_comment.move(20, 135)
        self.label_comment.setText('Comment / Note')
        
        self.plain_comment = QPlainTextEdit(self)
        self.plain_comment.resize(240,80)
        self.plain_comment.move(150, 135)
        
        self.masi_label = QLabel(self)
        self.masi_label.resize(82, 65)
        self.masi_label.move(20, 155)
        pixmap = QPixmap('masi.png')
        self.masi_label.setPixmap(pixmap.scaled(82,65,Qt.KeepAspectRatio))
            
        self.label_new_pack = QLabel(self)
        self.label_new_pack.resize(360, 20)
        self.label_new_pack.move(20, 220)
        self.label_new_pack.setText('--------Print Barcode------------------------------------')
        self.label_new_pack.setFont(myFont)
        
#         self.btn_gen_new_pack = QPushButton('Generate and Print\nnew Barcode Pack', self)
        self.btn_gen_new_pack = QPushButton('Full Pack', self)
        self.btn_gen_new_pack.resize(180,30)
        self.btn_gen_new_pack.move(20,245)
        
        self.btn_print_frozen_only = QPushButton('Extra Frozen only', self)
        self.btn_print_frozen_only.resize(180,30)
        self.btn_print_frozen_only.move(200,245)
        
        self.label_single_barcode = QLabel(self)
        self.label_single_barcode.resize(360, 20)
        self.label_single_barcode.move(20, 280)
        self.label_single_barcode.setText('--------Single Barcode Action------------------------------------')
        self.label_single_barcode.setFont(myFont)
        
        self.label_barcode_id = QLabel(self)
        self.label_barcode_id.resize(130, 20)
        self.label_barcode_id.move(20, 305)
        self.label_barcode_id.setText('Barcode ID')
        
        # Create textbox
        self.textbox_barcode_id = QLineEdit(self)
        self.textbox_barcode_id.resize(170,20)
        self.textbox_barcode_id.move(105, 305)
        
        self.btn_scanned = QPushButton('Webcam', self)
        self.btn_scanned.resize(120,25)
        self.btn_scanned.move(280,300)     
        
        self.label_action_type = QLabel(self)
        self.label_action_type.resize(80, 30)
        self.label_action_type.move(20, 330)
        self.label_action_type.setText('Action List')

        self.cb_action_type = QComboBox(self)
        self.cb_action_type.resize(230,30)
        self.cb_action_type.move(100,330)
        self.cb_action_type.addItem('')
        
        ### Distribution actions are done in the Location App.
#         self.cb_action_type.addItems(['Re-print a missing barcode',
#                                       'Re-print a destroyed barcode',
#                                       'DNA distributed to Vantage', 
#                                       'DNA extracted and banked', 
#                                       'Distributed to Lau',
#                                       'Distributed to TPSR',
#                                       'Paraffin blocks back from TPSR',
#                                       'Distributed to Vantage'])   
        
        self.cb_action_type.addItems(['Re-print a missing barcode',
                                      'Re-print a destroyed barcode'])   
        
        
        self.btn_sent_to = QPushButton('Run', self)
        self.btn_sent_to.resize(70,30)
        self.btn_sent_to.move(330,330)

        self.cam_label = QLabel(self)
        self.cam_label.resize(340, 200)
        self.cam_label.move(35, 365)
        
        pixmap = QPixmap('GCA.png')
        self.cam_label.setPixmap(pixmap)
        
        self.label_single_barcode = QLabel(self)
        self.label_single_barcode.resize(360, 20)
        self.label_single_barcode.move(420, 15)
        self.label_single_barcode.setText('--------Stats Summary------------------------------------')
        self.label_single_barcode.setFont(myFont)
        
        self.label_stats_type = QLabel(self)
        self.label_stats_type.resize(90, 20)
        self.label_stats_type.move(420, 50)
        self.label_stats_type.setText('Stats Type')
        
        self.cb_stats_type = QComboBox(self)
        self.cb_stats_type.resize(90,20)
        self.cb_stats_type.move(510,50)
        self.cb_stats_type.addItem('')
        self.cb_stats_type.addItems(["Project", "Subject", "Barcode"])
        
        self.label_stats_type = QLabel(self)
        self.label_stats_type.resize(90, 20)
        self.label_stats_type.move(710, 45)
        self.label_stats_type.setText('Version 1.0.0')
        
        self.label_contact_us = QLabel(self)
        self.label_contact_us.resize(90, 40)
        self.label_contact_us.move(710, 60)
        self.label_contact_us.setText(" <a href=\"mailto:shunxing.bao@vanderbilt.edu\">Contact us</a>")
        self.label_contact_us.setOpenExternalLinks(True)
        
        self.btn_stats = QPushButton('Print Stats', self)
        self.btn_stats.resize(180,30)
        self.btn_stats.move(420,70)

        self.plain_console = QPlainTextEdit(self)
        self.plain_console.resize(360,465)
        self.plain_console.move(420, 100)
        self.plain_console.setPlainText('--------------Output Log--------------')

        # connect button to on_click functions
        self.btn_get_next_subject.clicked.connect(self.getNextSubject)
        self.btn_gen_new_pack.clicked.connect(self.genPrintNewPack)
        self.btn_get_subject_type.clicked.connect(self.getSubjectType)
        self.btn_get_last_printed.clicked.connect(self.getLastPrinted)
        self.btn_sent_to.clicked.connect(self.setStatusSetAction)
        self.btn_scanned.clicked.connect(self.setStatusScanned)        
        self.btn_stats.clicked.connect(self.getBarcodeStats)
        self.btn_print_frozen_only.clicked.connect(self.printExtraFrozenOnly)

        # return enter event, a barcode scanner always print a barcode with a return event, 
        # when return event is triggered, it will convert ean8 code to the real barcode,
        # users will not see the ean8 code explicitly.
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
        self.custom_option = self.cb_option_type.currentText()
        self.action_comment = self.plain_comment.toPlainText()
        self.barcode_id = self.textbox_barcode_id.text()
        self.action_type = self.cb_action_type.currentText()
        self.stats_type = self.cb_stats_type.currentText()
        
        
    @pyqtSlot()
    def getNextSubject(self):
        """
        The idea is to get next not printed subject id with sequential order. 
        Probably not very useful right now because patient may not show up in order.
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
            QMessageBox.about(self, "WARNING", '-(1)Please create subject %s REDCap form first.\n(2)Please double check the Id in Redcap entry.\nThe Id should be in numeric format (i.e., 17, 20, 99), \nnot in 3-digit format (i.e., 017, 020, 099)\n(3)In Redcap, please check if you choose a category' % str(next_subject_id))
            return
        
        # get next Patient Id to print.
        next_print_subject_id_verified = self.getPatentId(next_subject_id)
        self.textbox_subject_id.setText(next_print_subject_id_verified)
        
        studyType_redcap = record.get('redcap_event_name').values
        if len(studyType_redcap) > 1:
            QMessageBox.about(self, "WARNING", "-Please check subject %s Redcap data entry.\nOnly one category per patient is allowed.\nIf there is only one catogory has been selected" % str(self.subjectId)  )
            return
        
        # get next patient study type
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
        
    def getSubjectType(self):
        """
        Get selected subject id
        """
        self.getGUIFieldValue()
        if self.subjectId == '' or self.subjectId == None:
            QMessageBox.about(self, "WARNING", "Subject id is empty. Get subject %s type failed." % str(self.subjectId)  )
            return
        
        curSubj = self.redcapExec.getInputPatient()
        
        print(curSubj)
        df = pd.DataFrame.from_dict(curSubj)
        record = df.loc[df['record_id_dem_endo'] == str(int(self.subjectId))]

        if len(record) is 0 or None:
            QMessageBox.about(self, "WARNING", '--(1)Please create subject %s form first.\n(2)Please double check the Id in Redcap entry.\nThe Id should be in numeric format (i.e., 17, 20, 99), \nnot in 3-digit format (i.e., 017, 020, 099)\n(3)In Redcap, please check if you choose a category' % str(int(self.subjectId)))
            return
        
        studyType_redcap = record.get('redcap_event_name').values
        if len(studyType_redcap) > 1:
            QMessageBox.about(self, "WARNING", "---Please check subject %s Redcap data entry.\nOnly one category per patient is allowed.\nIf there is only one catogory has been selected" % str(self.subjectId)  )
            return        
        print('nima%s' % studyType_redcap)
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
        Get last printed subject id, a specification that users care. 
        The function is more useful than next subject to print. 
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
            # single pandas query, within the tuple table, find last record whose barcode_action_type is 'printed'
            last_record = df.iloc[-1,:]
            last_record_list = last_record.tolist()
            last_print_subj = last_record_list[2][3:6] # index 2 is 'barcode_sample_id'
            last_processed_by = last_record_list[3] # the last element
                                                    #'action_tuple_table_arm_3',
                                                    #'barcode_sample_id',
                                                    #'barcode_action_type',
                                                    #'barcode_processed_by'
            QMessageBox.about(self, "WARNING", 'Last printed subject: %s\nProcessed by: %s' % (str(last_print_subj),str(last_processed_by)))
    
    @pyqtSlot()
    def printExtraFrozenOnly(self):
        """
        Generate and print new pack of barcodes
        """
        self.getGUIFieldValue()
        if self.subjectId == '' or self.subjectId == None:
            QMessageBox.about(self, "WARNING", "Subject id is empty. Print extra frozen specimen for subject %s failed." % str(self.subjectId)  )
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
        

        
        curSubj = self.redcapExec.getInputPatient()
        df = pd.DataFrame.from_dict(curSubj)
        record = df.loc[df['record_id_dem_endo'] == str(int(self.subjectId))]

        if len(record) is 0 or None:
            QMessageBox.about(self, "WARNING", "---(1)Please create subject %s form first.\n(2)Please double check the Id in Redcap entry.\nThe Id should be in numeric format (i.e., 17, 20, 99), \nnot in 3-digit format (i.e., 017, 020, 099)\n(3)In Redcap, please check if you choose a category" % str(self.subjectId)  )
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

        ###add constraint to restrict one patient can only be one type
        
        self.custom_option = self.redcapExec.getIfFreshNeedOrNot(self.subjectId)
        if self.custom_option =='' or self.custom_option == None:
            QMessageBox.about(self, "WARNING", "Subject %s id not found. Print new pack first" % str(self.subjectId) )
            return
        
        barcodeExec = BarcodeGenerator(self.subjectId,self.studyType)                
        
        #can optimize - done?
        nextAvailActionId = self.redcapExec.getNextAvailActionId()       
        tmp_barcode_list = barcodeExec.get_extra_frozen_barcode_list() # a hack way to get ADD frozen id only  
        
        #set generate action
        for tmp_barcode_id in tmp_barcode_list:
            if tmp_barcode_id == '': # no need to print
                continue 
                
            ean8_code = barcodeExec.recordId_to_ean8(tmp_barcode_id)
            
            # generate ean8 code to make sure it matches our criteria
            if ean8_code is None:
                QMessageBox.about(self, "WARNING", "Something wrong with barcode id %s?" % (tmp_barcode_id))
                return
            
            self.printLabel(tmp_barcode_id, ean8_code)
            # add barcode ean8 code
            self.redcapExec.setPrintedAction(nextAvailActionId, tmp_barcode_id, self.studyType,self.processed_by,self.action_comment,ean8_code,self.custom_option)
            nextAvailActionId += 1
        
            bool_update_redcap_sophie = self.redcapExec.update_REDCAP_SOPHIE_EXTRA_FROZEN(self.studyType,str(int(self.subjectId)),tmp_barcode_list, self.custom_option)
        
        self.plain_comment.clear()
        
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.appendPlainText("\n\n%s\nGenerate Extra Frozen Barcodes IDs for subject %s DONE! Printing may takes time, please be patient.\nTotal barcodes to print: %s" 
                                           % (str(cur_date),str(self.subjectId),str(len(tmp_barcode_list))))
        
        self.cb_option_type.setCurrentIndex(0)
        self.plain_console.repaint()
        self.plain_console.moveCursor(QTextCursor.End)
        
    @pyqtSlot()
    def genPrintNewPack(self):
        """
        Generate and print new full pack of barcodes
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
        
        if self.custom_option =='' or self.custom_option == None:
            QMessageBox.about(self, "WARNING", "Please select custom option for printing." )
            return
        
        ###add constraint to restrict one patient can only be one type
        curSubj = self.redcapExec.getInputPatient()
        df = pd.DataFrame.from_dict(curSubj)
        record = df.loc[df['record_id_dem_endo'] == str(int(self.subjectId))]

        if len(record) is 0 or None:
            QMessageBox.about(self, "WARNING", "--- Please create subject %s form first.\nPlease double check the Id in Redcap entry.\nThe Id should be in numeric format (i.e., 17, 20, 99), \nnot in 3-digit format (i.e., 017, 020, 099)" % str(self.subjectId)  )
            return
            
        studyType_redcap = record.get('redcap_event_name').values
        if len(studyType_redcap) > 1:
            QMessageBox.about(self, "WARNING", "--- Please check subject %s Redcap data entry.\nOnly one category per patient is allowed.\nIf there is only one catogory has been selected" % str(self.subjectId)  )
            return
           
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
        
        # new feature 12/19/2019
        tmp_barcode_list = barcodeExec.get_barcode_list(self.custom_option) # More constraint before Christmas...
           
        
        #set generate action
        for tmp_barcode_id in tmp_barcode_list:
            if tmp_barcode_id == '': # no need to print
                continue 
                
            ean8_code = barcodeExec.recordId_to_ean8(tmp_barcode_id)
            
            # generate ean8 code to make sure it matches our criteria
            if ean8_code is None:
                QMessageBox.about(self, "WARNING", "Something wrong with barcode id %s?" % (tmp_barcode_id))
                return
            
            self.printLabel(tmp_barcode_id, ean8_code)
            # add barcode ean8 code
            self.redcapExec.setPrintedAction(nextAvailActionId, tmp_barcode_id, self.studyType,self.processed_by,self.action_comment,ean8_code,self.custom_option)
            nextAvailActionId += 1
        
            bool_update_redcap_sophie = self.redcapExec.update_REDCAP_SOPHIE(self.studyType,str(int(self.subjectId)),tmp_barcode_list,self.custom_option)
        
        self.plain_comment.clear()
        
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.appendPlainText("\n\n%s\nGenerate new pack for subject %s DONE!\nCustom option:%s\n Printing may takes time, please be patient.\nTotal barcodes to print: %s" 
                                           % (str(cur_date),str(self.subjectId),str(self.custom_option),str(len(tmp_barcode_list))))
        
        self.cb_option_type.setCurrentIndex(0)
        self.plain_console.repaint()
        self.plain_console.moveCursor(QTextCursor.End)
        

    @pyqtSlot()
    def rePrintSingleLabel(self, tmp_ean8_code):
        """
        Reprint label
        """
        self.printLabel(self.barcode_id,tmp_ean8_code)
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
#        self.plain_console.appendPlainText("\n\n%s\nReprint barcode %s DONE!" % (str(cur_date),str(self.barcode_id)))
    
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
        
        if self.studyType == '' or self.studyType == None:
            QMessageBox.about(self, "WARNING", "Study type is empty. Do action for barcode %s failed." % str(self.barcode_id))
            return
        
        if self.processed_by == '' or self.processed_by ==None:
            QMessageBox.about(self, "WARNING", "Please select current user." )
            return
        
        # check barcode exists and return custom option
        self.subjectId = self.barcode_id[3:6] #GCAxxx -> xxx
        tmp_custom_option = self.redcapExec.getSubjectLastestCustomOption(self.barcode_id,self.subjectId)
        if tmp_custom_option is False:
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
        
        # Re-print a missing barcode doesn't need to update Sophie's REDCap form, only update barcode tuple table
        if self.action_type == 'Re-print a missing barcode':
            self.rePrintSingleLabel(ean8_code)
        
        # Re-print a destroyed barcode need to be update Sophie's REDCap form, because the field is empty. 
        if self.action_type == 'Re-print a destroyed barcode':
            self.rePrintSingleLabel(ean8_code)
            # NEED TO WORK ON IT -> bool_update_redcap_sophie = self.redcapExec.update_REDCAP_SOPHIE_SINGLE_BARCODE(self.studyType,str(int(self.subjectId)),self.barcode_id,tmp_custom_option)
            
            
        self.redcapExec.setAction(nextAvailActionId, self.barcode_id, self.studyType,self.processed_by,self.action_type,self.action_comment,ean8_code,tmp_custom_option)

        self.plain_comment.clear()
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.appendPlainText("\n\n%s\nbarcode %s action: %s DONE!" % (str(cur_date),str(self.barcode_id),self.action_type))
        self.plain_console.repaint()
        self.plain_console.moveCursor(QTextCursor.End)
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
        self.getGUIFieldValue()
        if self.processed_by == '' or self.processed_by ==None:
            QMessageBox.about(self, "WARNING", "Please select current user." )
            return
        
        self.set_scanned_id(self.textbox_barcode_id.text())

    @pyqtSlot('QString')
    def set_scanned_id(self, scanned_id):
        """
        Convert ean8 id to real barcode id
        """
        barcodeExec = BarcodeGenerator()

        tmp_barcode_id = ''
        # hacking because location app does not have self.subject field
        if scanned_id[0:3] == 'GCA':
            # in case users manaully type the barcode. No need ean8 conversion.
            self.barcode_id = scanned_id # self.subject is not set in barcode_generator...
        else:
            if barcodeExec.is_valid(str(scanned_id)) is False:
                QtWidgets.QMessageBox.about(Form, "WARNING", "Barcode is not valid(1). Please contact to administrator" )
                self.plain_console.repaint()
                return False

            tmp_barcode_id = barcodeExec.ean8_to_recordId(scanned_id)
            if tmp_barcode_id is None:
                QtWidgets.QMessageBox.about(Form, "WARNING", "Barcode is not valid(2). Please contact to administrator" )
                self.plain_console.repaint()
                return False       
        
            # set GUI
            self.barcode_id = tmp_barcode_id
            
        
        # set GUI
        self.textbox_barcode_id.setText(self.barcode_id)
        self.subjectId = self.barcode_id[3:6]
        tmp_custom_option = self.redcapExec.getSubjectLastestCustomOption(self.barcode_id,self.subjectId)
        if tmp_custom_option is False:
            QMessageBox.about(self, "WARNING", 
                              "Barcode %s is not found \n\n please generate barcode first" % str(self.barcode_id))
            return
        
        tmp_studyType = scanned_id[0:1]
        
        if tmp_studyType == '1':
            self.cb_study_type.setCurrentIndex(1)
        elif tmp_studyType == '2':
            self.cb_study_type.setCurrentIndex(2)
        elif tmp_studyType == '3':
            self.cb_study_type.setCurrentIndex(3)
        elif tmp_studyType == '4':
            self.cb_study_type.setCurrentIndex(4)
        # add a new barcode actoin record
        nextAvailActionId = self.redcapExec.getNextAvailActionId()
        self.redcapExec.setScannedAction(nextAvailActionId, self.barcode_id, self.studyType,self.processed_by,self.action_comment,scanned_id,tmp_custom_option)
        self.plain_comment.clear()
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        self.plain_console.appendPlainText("\n\n%s\nSet barcode %s scanned status DONE!" % (str(cur_date),str(self.barcode_id)))
        self.plain_console.repaint()
        self.plain_console.moveCursor(QTextCursor.End)
                
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
            
            # a hacking here because we don't care if the subject contains extra frozen id or not.
            barcodeExec = BarcodeGenerator(self.subjectId,self.studyType)
            
            barcodeExec.execute()
            tmp_barcode_list = barcodeExec.get_barcode_list(self.custom_option)  
            
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
        self.plain_console.moveCursor(QTextCursor.End)
        
            
    def getPatentId(self,cur_id):
        """
        return a three digit patient Id. 
        """
        int_cur_id = int(cur_id)
        if int_cur_id < 10:
            return '00%s' % str(int_cur_id)
        elif int_cur_id < 100:
            return '0%s' % str(int_cur_id)
        else:
            return '%s' % str(int_cur_id)
    
    def closeEvent(self, event):
            # clean up barcode label tmp directory
        curDir = os.getcwd()
        barcode_tmp_path = curDir + '/tmp'

        if os.path.exists(barcode_tmp_path):
            shutil.rmtree(barcode_tmp_path)
        

if __name__ == '__main__':
    # create tmp directory for barcode label generations
    
    app = QApplication(sys.argv)
    ex = PrinterApp()
    sys.exit(app.exec_())
    

    

