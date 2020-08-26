import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from pyzbar.wrapper import ZBarSymbol
from playsound import playsound
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage,QPixmap
import time
import os

class Barcode_reader(QThread):
    """
    Use the webcam to detect barcode. 
    """
    change_pixmap = pyqtSignal(QImage)
    found_qr = pyqtSignal("QString")

        
    def run(self):
        cap = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_PLAIN
        found_barcode_id = None # barcode detect from the webcam

        while True:
            
            ret, frame = cap.read()
            
            #load ret from the webcam
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                p = convertToQtFormat.scaled(320, 240, Qt.KeepAspectRatio)
                
                # create a video window
                self.change_pixmap.emit(p)
                
                decodedObjects = pyzbar.decode(frame)
                for obj in decodedObjects:
                    
                    found_barcode_id = obj.data.decode("utf-8")
                    
                    # load scanner liked sound from current directory.
                    curDir = os.getcwd()
                    playsound('%s/scanner-beep.wav' % str(curDir))
                    self.found_qr.emit(found_barcode_id)

            
            # the webcam can only capture one barcode.
            if found_barcode_id is not None:
                break
   
        cap.release()
        
        # set back the video window to the GCA.
        self.change_pixmap.emit(QPixmap('GCA.png').toImage())
        

