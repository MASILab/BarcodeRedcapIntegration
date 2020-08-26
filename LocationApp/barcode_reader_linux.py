import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from pyzbar.wrapper import ZBarSymbol
from playsound import playsound
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage,QPixmap
import time
import os

class Barcode_reader_linux(QThread):
    """
    Use webcam to read barcode. 
    --- time most spent on which barcode can be read, webcam issues and pyqt5's QThread issue.
    """
    change_pixmap = pyqtSignal(QImage)
    found_qr = pyqtSignal("QString")

#     def __init__(self,parent=None):
#         super(Barcode_reader, self).__init__(parent)
#         self.cap = None
        
    def run(self):
        cap = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_PLAIN
        found_barcode_id = None

        while True:
            ret, frame = cap.read()
            
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #p = QPixmap.fromImage(rgbImage)    
                #p = p.scaled(640, 480, Qt.KeepAspectRatio)
                convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                p = convertToQtFormat.scaled(480, 240, Qt.KeepAspectRatio)
                self.change_pixmap.emit(p)
                
                decodedObjects = pyzbar.decode(frame)
                for obj in decodedObjects:
                    found_barcode_id = obj.data.decode("utf-8")
#                    if self.tmp_found_id != self.found_barcode_id:
                    curDir = os.getcwd()
                    # just don't play scanner sound...
#                    playsound('%s/scanner-beep.wav' % str(curDir))
                    self.found_qr.emit(found_barcode_id)
            
            # the webcam will only capture one barcode...
            if found_barcode_id is not None:
                break
   
        cap.release()
        self.change_pixmap.emit(QPixmap('GCA.png').toImage())
        
