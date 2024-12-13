import cv2
import numpy as np
#import pyzbar.pyzbar as pyzbar
#from pyzbar.wrapper import ZBarSymbol
from playsound import playsound
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage,QPixmap
import time
import os

class Barcode_reader_imac(QThread):
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
#                    playsound('%s/scanner-beep.wav' % str(curDir))
                    self.found_qr.emit(found_barcode_id)
#                         self.found_barcode_id = self.tmp_found_id
#                         print('found %s' % self.found_barcode_id)
#                         print('tmp %s' % self.tmp_found_id)
#                         time.sleep(2)
# #                        self.tmp_found_id = self.found_barcode_id
            
            # the webcam will only capture one barcode...
            if found_barcode_id is not None:
                break
   
        cap.release()
        self.change_pixmap.emit(QPixmap('/home/masi/Downloads/DymoRedcapIntegration/LocationApp_v1/GCA.png').toImage())
        
#     def exit(self):
# #         self.threadactive = False
#         self.cap.release()
#         self.change_pixmap.emit(QPixmap('GCA.png').toImage())
        
#                 decoded_objects = pyzbar.decode(frame)
#                 for obj in decoded_objects:
#                     cv2.putText(frame, str(obj.data), (50, 50), font, 2, (255, 0, 0), 3)
#                     self.found_qr.emit(obj.data.decode("utf-8"))
                 
                
                 
# #             img1=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# # #            qimg1=QImage(img1.data, img1.shape[1], img1.shape[0], img1.strides[0], QImage.Format_RGB888)
# # #            self.change_pixmap.emit(qimg1)
            
# #             rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #             h, w, ch = rgb_image.shape
# #             bytes_per_line = ch * w
# #             convert_to_qt_format = QImage(
# #                 rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888
# #             )
# #             p = convert_to_qt_format.scaled(221, 181, Qt.KeepAspectRatio)
# #             self.change_pixmap.emit(p.mirrored(True, False))
# #             # cv2.namedWindow("Frame", cv2.WINDOW_GUI_NORMAL)
#             # cv2.imshow("Frame", frame)
#                 key = cv2.waitKey(1)
#                 if key == 27:
#                     cap.release()
#                     # cv2.destroyWindow("Frame")
#                     break                           
            
#             _, frame = cap.read()
#   #          _, frame = self.capture1.read()
#             decodedObjects = pyzbar.decode(frame)
#             for obj in decodedObjects:
#                 found_barcode_id = obj.data
#  #               print("Data", obj.data)
#                 cv2.putText(frame, str(obj.data), (50, 50), font, 2,
#                             (255, 0, 0), 3)
#                 playsound('/Users/obo/Downloads/Scanning-Qr-Code-Opencv-with-Python-master/scanner-beep.wav')
#         #    frame_resize = cv2.resize(frame, (200, 100))

#             scale_width = screen_res[0] / frame.shape[1]
#             scale_height = screen_res[1] / frame.shape[0]
#             scale = min(scale_width, scale_height)
            
#             #resized window width and height
#             window_width = int(frame.shape[1] * scale)
#             window_height = int(frame.shape[0] * scale)


#         #resize the window according to the screen resolution
#             cv2.resizeWindow('Barcode Scanner', window_width, window_height)

#             cv2.moveWindow('Barcode Scanner', 40,30)
#             cv2.imshow('Barcode Scanner', frame)

#             if found_barcode_id is not None:
#                 break
#             key = cv2.waitKey(0) & 0xFF
#             if key == ord("q"):
#                 break
 
#  #       self.changePixmap.emit(found_barcode_id) 
        
#         self.capture1.release()
#         cv2.destroyAllWindows()
# #    def finished(self):
#  #       self.capture1.release()
        
# #        return found_barcode_id.decode("utf-8")
# #        print('oh yeah %s'  % found_barcode_id.decode("utf-8") )
#     def __del__(self):
#         self.wait()

# # x = Barcode_reader()
# # x.getBiopsiesId_ean8()

