import treepoem
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import cv2
import barcode
from barcode.writer import ImageWriter

class LabelPrintHelper_mac:
    """
    Class for a simple workflow, generate ean8 code -> geneate label to print -> print label
    """
    def __init__(self, uId, tmp_ean8_code):
        self.uId = uId
        self.ean8_code = tmp_ean8_code
        curDir = os.getcwd()
        self.barcode_tmp_path = curDir + '/tmp'

    def genBarcode(self):
        """
        generate ean8 image to print
        """
#        print(self.uId)
        
        #print(barcode.PROVIDED_BARCODES)
#        print('test test test')
#        EAN = barcode.get_barcode_class('ean8')
#        ean8_image = EAN(u'%s' % self.ean8_code,writer=ImageWriter()) # to generate a png for later editing

#        ean8_path = "%s/%s_barcode" % (self.barcode_tmp_path,self.uId)
#        ean8_image.save(ean8_path)
        



	#### Data Martix
	


        ean8_path = "%s/%s_barcode" % (self.barcode_tmp_path,self.uId)
#         ean8_image.save(ean8_path)
        
        print('wocaoa %s ' % self.ean8_code )
        nimabudongle = '%s' % self.ean8_code
        ean8_image = treepoem.generate_barcode(
        barcode_type='datamatrix',  # One of the supported codes.
            data=nimabudongle, 
        ) 
        ean8_image.convert('1').save(ean8_path + '.png')

    def genLabel(self):

        """
        Create and edit a label to print   
        """
        # Well tuned ... Spent a lot of labels...
        page_width = 182
        page_height = 100

        # create the canvas Load ean8 png image, crop to fit size and paste to blank canvas.
        # Well tuned ... Spent a lot of labels...
        source_img = Image.new('RGBA', (page_width,page_height), "white")
        ean8_png_path = "%s/%s_barcode.png" % (self.barcode_tmp_path,self.uId)
        barcode_image = Image.open(ean8_png_path)

        barcode_image_cropped=barcode_image#.crop((0, 0, barcode_image.size[0], 120))
        source_img.paste(barcode_image_cropped, (75, 25))


        # add real barcode id to the label
        # text="GCA9999FrozenTIB" -> sample Real id
        font = ImageFont.truetype("/app/v2/PrinterApp_v2/Arialn.ttf")

        textBox_size = (200,100)
        text_img = Image.new('RGBA', textBox_size, "white")
        # put text on label
        text_draw = ImageDraw.Draw(text_img)
        font = ImageFont.truetype("/app/v2/PrinterApp_v2/Arialn.ttf", 15) # 40 is font size
        text_draw.text((0, 0), self.uId, font=font,fill=(0,0,0,255))
        
        source_img.paste(text_img, (55,75))
        # label_path = "/tmp/%s_label.png" % self.uId
        label_path = "%s/%s_label.png" % (self.barcode_tmp_path,self.uId)
        source_img.save(label_path, "PNG")

        # for mac users. Need to rotate 180 degree...
        rotated_img = source_img.rotate(180)
        rotated_img.save(label_path, "PNG")
        

    def printLabel(self):
        """
        Use system command 'lpr' to print the label
        Use 
            lpoptions -d DYMO_LabelWriter_450
        to setup default printer
        """
        
        cmd = "lpr -o PageSize=Custom.23x30mm   %s/%s_label.png" % (self.barcode_tmp_path,self.uId) #barcode_image_cropped
        print(cmd)
        os.system(cmd)

    def execute(self):
        """
        A simple workflow, generate ean8 code -> geneate label to print -> print label
        """
        self.genBarcode()
        self.genLabel()
        self.printLabel()
        
    def main():
        print("Hello World!")

    if __name__== "__main__":
        main()
        