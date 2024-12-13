import redcap
import os
import sys
import argparse
import logging as LOGGER
import warnings
from exceptions import *
from cheatSheetEAN_Converter import CheatSheetEAN_Converter

class BarcodeGenerator:
    def __init__(self, p_id=None, sType=None):
        self._subject_id = p_id
        self._studyType =  sType
        self._barcode_list = []

    """
    Boring but important part to generate all real barcode ids. 
    """    
    def getBiopsiesCDEndoId(self):
        self._barcode_list.append('GCA%sFreshTIA' % self._subject_id)
        self._barcode_list.append('GCA%sFixedTIA' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenTIA' % self._subject_id)
        self._barcode_list.append('GCA%sFreshTIB' % self._subject_id)
        self._barcode_list.append('GCA%sFixedTIB' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenTIB' % self._subject_id)
        self._barcode_list.append('GCA%sFreshACA' % self._subject_id)
        self._barcode_list.append('GCA%sFixedACA' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenACA' % self._subject_id)
        self._barcode_list.append('GCA%sFreshACB' % self._subject_id)
        self._barcode_list.append('GCA%sFixedACB' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenACB' % self._subject_id)

    def getBiopsiesCTLEndoId(self):
        self._barcode_list.append('GCA%sFreshTI' % self._subject_id)
        self._barcode_list.append('GCA%sFixedTI' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenTI' % self._subject_id)
        self._barcode_list.append('GCA%sFreshAC' % self._subject_id)
        self._barcode_list.append('GCA%sFixedAC' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenAC' % self._subject_id)

    def getBiopsiesCDSurgeryId(self):
        self._barcode_list.append('GCA%sFreshTI' % self._subject_id)
        self._barcode_list.append('GCA%sFixedTI' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenTI' % self._subject_id)
        self._barcode_list.append('GCA%sFreshAC' % self._subject_id)
        self._barcode_list.append('GCA%sFixedAC' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenAC' % self._subject_id)

    def getBiopsiesCTLSurgeryId(self):
        self._barcode_list.append('GCA%sFreshTI1' % self._subject_id)
        self._barcode_list.append('GCA%sFixedTI1' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenTI1' % self._subject_id)
        self._barcode_list.append('GCA%sFreshTI2' % self._subject_id)
        self._barcode_list.append('GCA%sFixedTI2' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenTI2' % self._subject_id)
        self._barcode_list.append('GCA%sFreshTI3' % self._subject_id)
        self._barcode_list.append('GCA%sFixedTI3' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenTI3' % self._subject_id)
        self._barcode_list.append('GCA%sFreshAC4' % self._subject_id)
        self._barcode_list.append('GCA%sFixedAC4' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenAC4' % self._subject_id)
        self._barcode_list.append('GCA%sFreshAC5' % self._subject_id)
        self._barcode_list.append('GCA%sFixedAC5' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenAC5' % self._subject_id)
        self._barcode_list.append('GCA%sFreshAC6' % self._subject_id)
        self._barcode_list.append('GCA%sFixedAC6' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenAC6' % self._subject_id)
        self._barcode_list.append('GCA%sFreshAC7' % self._subject_id)
        self._barcode_list.append('GCA%sFixedAC7' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenAC7' % self._subject_id)
        self._barcode_list.append('GCA%sFreshAC8' % self._subject_id)
        self._barcode_list.append('GCA%sFixedAC8' % self._subject_id)
        self._barcode_list.append('GCA%sFrozenAC8' % self._subject_id)

    def getDNAId(self):
        self._barcode_list.append('GCA%sDNA' % self._subject_id)

    def getStoolId(self):
        self._barcode_list.append('GCA%sST1' % self._subject_id) 
        self._barcode_list.append('GCA%sST2' % self._subject_id) 
        self._barcode_list.append('GCA%sST3' % self._subject_id) 
        self._barcode_list.append('GCA%sST4' % self._subject_id) 

    def getSerumId(self):
        self._barcode_list.append('GCA%sSR1' % self._subject_id)
        self._barcode_list.append('GCA%sSR2' % self._subject_id)
        self._barcode_list.append('GCA%sSR3' % self._subject_id) 
        self._barcode_list.append('GCA%sSR4' % self._subject_id) 
        self._barcode_list.append('GCA%sSR5' % self._subject_id)
        self._barcode_list.append('GCA%sSR6' % self._subject_id)
        self._barcode_list.append('GCA%sSR7' % self._subject_id) 
        self._barcode_list.append('GCA%sSR8' % self._subject_id)
        self._barcode_list.append('GCA%sSR9' % self._subject_id)
        self._barcode_list.append('GCA%sSR10' % self._subject_id)
        self._barcode_list.append('GCA%sSR11' % self._subject_id)
        
    def getExtraFrozenId(self):
        self._barcode_list.append('GCA%sADDFrozenTIA' % self._subject_id)
        self._barcode_list.append('GCA%sADDFrozenTIB' % self._subject_id)
        self._barcode_list.append('GCA%sADDFrozenACA' % self._subject_id)
        self._barcode_list.append('GCA%sADDFrozenACB' % self._subject_id)

    def getExtraSerumId(self):
        self._barcode_list.append('GCA%sSR9' % self._subject_id)
        self._barcode_list.append('GCA%sSR10' % self._subject_id)
        self._barcode_list.append('GCA%sSR11' % self._subject_id)
        
    def execute(self):
        """
        generate BarcodeId
        """
        if self._studyType == 'CD_ENDO' or self._studyType == 'CTL_ENDO':
            print ('in %s' % str(self._studyType))
            self.getStoolId()
            self.getSerumId()
            self.getDNAId()
            
            
        if self._studyType == 'CD_ENDO':
            self.getBiopsiesCDEndoId()
        elif self._studyType == 'CTL_ENDO':
            self.getBiopsiesCTLEndoId()
        elif self._studyType == 'CD_Surgery':
            self.getBiopsiesCDSurgeryId()
        elif self._studyType == 'CTL_Surgery':
            self.getBiopsiesCTLSurgeryId()
            
#         # for specific specification to check if ExtraFrozen is needed. 
#         if self._ifExtraFrozen == True:
#        self.getExtraFrozenId() # we still create it, but we don't have to print it.
        
        print ('out%s' % str(self._studyType))
      
   
    def get_extra_serum_barcode_list(self):
        self._barcode_list = []
        self.getExtraSerumId()
        return self._barcode_list
    
    def get_extra_frozen_barcode_list(self):
        self._barcode_list = []
        self.getExtraFrozenId()
        return self._barcode_list
        
    def get_barcode_list(self, custom_option): 
        if custom_option == "Default":
            return self._barcode_list
    
        elif custom_option == "Need extra FROZEN specimens":
            self.getExtraFrozenId()
            return self._barcode_list
        
        elif custom_option == "No FRESH specimens, NO extra FROZEN specimens":
            idx = 0
            while idx < len(self._barcode_list):
                if "Fresh" in self._barcode_list[idx]:
                    self._barcode_list[idx]=''
    
                idx += 1 
            return self._barcode_list
        
        elif custom_option == "No FRESH specimens, ADD extra FROZEN specimens":
            self.getExtraFrozenId()
            idx = 0
            while idx < len(self._barcode_list):
                if "Fresh" in self._barcode_list[idx]:
                    self._barcode_list[idx]=''
    
                idx += 1 
            return self._barcode_list
        
        
#     def get_barcode_extra_frozen_only(self): 
#         """
#         To filter out extra frozen barcode only
#         """
#         # not a possible
# #         if custom_option == "Default":
# #             return self._barcode_list
    
#         if custom_option == "Need extra FROZEN specimens":
#             self.getExtraFrozenId()
#             return self._barcode_list
        
#         elif custom_option == "No FRESH specimens, ADD extra FROZEN specimens":
#             self.getExtraFrozenId()
#             idx = 0
#             while idx < len(self._barcode_list):
#                 if "ADD" not in self._barcode_list[idx]:
#                     self._barcode_list[idx]=''
    
#                 idx += 1 
#             return self._barcode_list
        
#         # Not a possible
# #         elif custom_option == "No FRESH specimens, NO extra FROZEN specimens":
# #             idx = 0
# #             while idx < len(self._barcode_list):
# #                 if "Fresh" in self._barcode_list[idx]:
# #                     self._barcode_list[idx]=''
    
# #                 idx += 1 
# #             return self._barcode_list
        

            
        
    
    def getSpecimenIndex(self,cur_id):
        """
        Make sure the id is two digit - used to convert specimen index in cheatsheet converter
        """
        print('nima%s' % cur_id)
        int_cur_id = int(cur_id)
        if int_cur_id < 10:
            return '0%s' % str(int_cur_id)
        elif int_cur_id < 100:
            return '%s' % str(int_cur_id)
    
    def ean8_to_recordId(self,tmp_ean8_code):
        """
        record id is GCAxxxFrozenSomething, ean8 code is the barcode to generate
        """
        eanConv = CheatSheetEAN_Converter()
        #"CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"
        #ean8_code: type(1 digit)_cheatList(2 digit)_0_patientid(3 digit)_checksum(1 digit)
        tmp_studyType = tmp_ean8_code[0:1]
        
        print('woca %s' % tmp_studyType)
        if tmp_studyType == '1':
            self._studyType = 'CD_ENDO'
        elif tmp_studyType == '2':
            self._studyType = 'CTL_ENDO'
        elif tmp_studyType == '3':        
            self._studyType = 'CD_Surgery'
        elif tmp_studyType == '4':         
            self._studyType = 'CTL_Surgery'
        
        tmp_specimen_Id = int(tmp_ean8_code[1:3])
        print(tmp_specimen_Id)
        
        specimen_real_Id = ''
        if self._studyType == 'CD_ENDO':
            if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CD_ENDO_CHEAT_LIST)-1:
                return None
            
            specimen_real_Id = eanConv.CD_ENDO_CHEAT_LIST[tmp_specimen_Id]
 
        elif self._studyType == 'CTL_ENDO':
            if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CTL_ENDO_CHEAT_LIST)-1:
                return None
            
            specimen_real_Id = eanConv.CTL_ENDO_CHEAT_LIST[tmp_specimen_Id]

        elif self._studyType == 'CD_Surgery':
            if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CD_Surgery_CHEAT_LIST)-1:
                return None
            print('here????')
            specimen_real_Id = eanConv.CD_Surgery_CHEAT_LIST[tmp_specimen_Id]

        elif self._studyType == 'CTL_Surgery':
            if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CTL_Surgery_CHEAT_LIST)-1:
                return None
            
            specimen_real_Id = eanConv.CTL_Surgery_CHEAT_LIST[tmp_specimen_Id]
 
        tmp_barcode_id = 'GCA' + tmp_ean8_code[4:7] + specimen_real_Id
        print('ahahahahha' + tmp_barcode_id)
        return tmp_barcode_id
    
    
    def recordId_to_ean8(self,tmp_barcode_id):
        """
        record id is GCAxxxFrozenSomething, ean8 code is the barcode to generate
        """
        eanConv = CheatSheetEAN_Converter()
        #"CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"
        ean8_code = ''# type(1 digit)_cheatList(2 digit)_0_patientid(3 digit)_checksum(1 digit)
        specimen_Id = tmp_barcode_id[6:len(tmp_barcode_id)]
        
        print(self._studyType)
        idx_specimen = ''
        if self._studyType == 'CD_ENDO':
            ean8_code = '1'
            if specimen_Id in eanConv.CD_ENDO_CHEAT_LIST:
                idx_specimen = eanConv.CD_ENDO_CHEAT_LIST.index(specimen_Id)
            else:
                return None
        elif self._studyType == 'CTL_ENDO':
            ean8_code = '2'
            if specimen_Id in eanConv.CTL_ENDO_CHEAT_LIST:
                idx_specimen = eanConv.CTL_ENDO_CHEAT_LIST.index(specimen_Id)
            else:
                return None
        elif self._studyType == 'CD_Surgery':
            ean8_code = '3'
            if specimen_Id in eanConv.CD_Surgery_CHEAT_LIST:
                idx_specimen = eanConv.CD_Surgery_CHEAT_LIST.index(specimen_Id)
            else:
                return None
        elif self._studyType == 'CTL_Surgery':
            ean8_code = '4'
            if specimen_Id in eanConv.CTL_Surgery_CHEAT_LIST:
                idx_specimen = eanConv.CTL_Surgery_CHEAT_LIST.index(specimen_Id)
            else:
                return None
        
        # hacking for location app since subject id is not needed
#         if self._subject_id is "" or None:
#             self._subject_id = tmp_barcode_id [3:6]
        print('woca???%s' % idx_specimen)    
        ean8_code = ean8_code + self.getSpecimenIndex(idx_specimen) + '0' + self._subject_id 
#        print('ahahahahha' + ean8_code)
        checksum = self.calc_check_digit(ean8_code)
 
        ean8_code = ean8_code + checksum 
        return ean8_code
            
    def calc_check_digit(self,number):
        """
        Get check sum digit. 
        """
        sum_odd = int(number[0]) + int(number[2]) + int(number[4]) + int(number[6])
        print(sum_odd)
        sum_even = int(number[1]) + int(number[3]) + int(number[5])
        print(sum_even)
        check_digit = (10 - (sum_odd * 3 + sum_even) % 10) % 10
        print(check_digit)
        return str(check_digit)

    def validate(self,number):
        """Check if the number provided is a valid EAN-8. This checks the length
        and the check bit but does not check whether a known GS1 Prefix and
        company identifier are referenced."""
    #    number = compact(number)
        if not number.isdigit():
            raise InvalidFormat()
    #    if len(number) not in (14, 13, 12, 8):
        if len(number) is not 8:
            raise InvalidLength()
        if self.calc_check_digit(number[:-1]) != number[-1]:
            raise InvalidChecksum()
        return number


    def is_valid(self,number):
        """Check if the number provided is a valid EAN-13. This checks the length
        and the check bit but does not check whether a known GS1 Prefix and
        company identifier are referenced."""
        try:
            return bool(self.validate(number))
        except ValidationError:
            return False
            
        
    def main():
        print("Hello World!")

    if __name__== "__main__":
        main()
