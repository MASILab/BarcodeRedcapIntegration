import redcap
import os
import sys
import argparse
import logging as LOGGER
import warnings
from exceptions import *
from cheatSheetEAN_Converter import CheatSheetEAN_Converter
""" 
    Modified on Mar 17, 2020,
    Add more different Frozen ID for CTL_ENDO, CD_Surgery, CTL_Surgery
"""

class BarcodeGenerator:
    def __init__(self, p_id=None, sType=None):
        self._subject_id = p_id
        self._studyType =  sType
        self._barcode_list = []

    """
    Boring but important part to generate all real barcode ids. 
    """
    def getBiopsiesId(self):
        self._barcode_list.append('CMA_%s_Fresh' % self._subject_id)
        self._barcode_list.append('CMA_%s_Fixed' % self._subject_id)
        self._barcode_list.append('CMA_%s_Frozen_1' % self._subject_id)
        self._barcode_list.append('CMA_%s_Frozen_2' % self._subject_id)
        self._barcode_list.append('CMA_%s_Frozen_3' % self._subject_id)
        self._barcode_list.append('CMA_%s_Frozen_4' % self._subject_id)
        self._barcode_list.append('CMA_%s_Frozen_5' % self._subject_id)
        self._barcode_list.append('CMA_%s_Frozen_6' % self._subject_id)
        self._barcode_list.append('CMA_%s_Frozen_7' % self._subject_id)
        #self._barcode_list.append('CMA_%s_Frozen_8' % self._subject_id)
        # self._barcode_list.append('CMA_%s_Frozen_9' % self._subject_id)
        # self._barcode_list.append('CMA_%s_Frozen_10' % self._subject_id)
        # self._barcode_list.append('CMA_%s_Frozen_11' % self._subject_id)
        
# #         for surgery patients:
#         self._barcode_list.append('DoD_%s_NDFresh' % self._subject_id)
#         self._barcode_list.append('DoD_%s_NDFixed' % self._subject_id)
#         self._barcode_list.append('DoD_%s_NDFrozen_1' % self._subject_id)
#         self._barcode_list.append('DoD_%s_NDFrozen_2' % self._subject_id)
#         self._barcode_list.append('DoD_%s_NDFrozen_3' % self._subject_id)

    def getDNAId(self):
        self._barcode_list.append('CMA_%s_DNA' % self._subject_id)

    def getStoolId(self):
        self._barcode_list.append('CMA_%s_ST_1' % self._subject_id)
        self._barcode_list.append('CMA_%s_ST_2' % self._subject_id)
        self._barcode_list.append('CMA_%s_ST_3' % self._subject_id)
        self._barcode_list.append('CMA_%s_ST_4' % self._subject_id)

    

    def getSerumId(self):
        self._barcode_list.append('CMA_%s_SR_1' % self._subject_id)
        self._barcode_list.append('CMA_%s_SR_2' % self._subject_id)
        self._barcode_list.append('CMA_%s_SR_3' % self._subject_id) 
        self._barcode_list.append('CMA_%s_SR_4' % self._subject_id) 
        self._barcode_list.append('CMA_%s_SR_5' % self._subject_id)
        self._barcode_list.append('CMA_%s_SR_6' % self._subject_id)
        self._barcode_list.append('CMA_%s_SR_7' % self._subject_id) 
        self._barcode_list.append('CMA_%s_SR_8' % self._subject_id)
        self._barcode_list.append('CMA_%s_SR_9' % self._subject_id)
        self._barcode_list.append('CMA_%s_SR_10' % self._subject_id)
        self._barcode_list.append('CMA_%s_SR_11' % self._subject_id)
        
    #Refine extra ids for CTL_ENDO, CD_Surgery, and CTL_Surgery
    # def getExtraFrozenId(self):
    #     self._barcode_list.append('DoD_%s_AddFrozen' % self._subject_id)    
    #     self._barcode_list.append('DoD_%s_NDAddFrozen' % self._subject_id)

    def getExtraTIId(self):
        self._barcode_list.append('CMA_%s_Fresh_TI' % self._subject_id)    
        self._barcode_list.append('CMA_%s_Fixed_TI' % self._subject_id)
        self._barcode_list.append('CMA_%s_Frozen_TI' % self._subject_id)

    # def getExtraSerumId(self):
    #     self._barcode_list.append('DoD_%s_SR9' % self._subject_id)
    #     self._barcode_list.append('DoD_%s_SR10' % self._subject_id)
    #     self._barcode_list.append('DoD_%s_SR11' % self._subject_id)
        
    def execute(self):
        """
        generate BarcodeId
        """
        #for now I only know all six tabs have same barcode
        self.getStoolId()
        self.getSerumId()
        # self.getDNAId()
        self.getBiopsiesId()
        
#         tmp_study_type = self._studyType
#         if tmp_study_type == 'UC_Surgery' or tmp_study_type == 'CD_Surgery' or tmp_study_type == 'CTL_Surgery':
            
        print ('out%s' % str(self._studyType))
                     
#         DoD_000_NDAddFrozen
        
        
    # def get_extra_serum_barcode_list(self):
    #     self._barcode_list = []
    #     self.getExtraSerumId()
    #     return self._barcode_list
    
    # def get_extra_frozen_barcode_list(self):
    #     self._barcode_list = []
    #     self.getExtraFrozenId()
    #     return self._barcode_list
    
    def get_extra_TI_barcode_list(self):
        self._barcode_list = []
        self.getExtraTIId()
        return self._barcode_list
        
    def get_barcode_list(self, custom_option):
        tmp_study_type = self._studyType


        # seems no use for CMA project
        # if tmp_study_type == 'UC_Surgery' or tmp_study_type == 'CD_Surgery' or tmp_study_type == 'CTL_Surgery' or tmp_study_type == 'Cancer_Surgery':
        #     idx = 0
        #     while idx < len(self._barcode_list):
        #         if "SR" in self._barcode_list[idx]:
        #             self._barcode_list[idx]=''
    
        #         idx += 1 
        # else: # not surgery patients, we don't need ND specimen
        #     idx = 0
        #     while idx < len(self._barcode_list):
        #         if "ND" in self._barcode_list[idx]:
        #             self._barcode_list[idx]=''
    
        #         idx += 1 
        #         #HACKING to make all SR to empty for surgery patient.
            
        if custom_option == "Default":
            return self._barcode_list
    
        elif custom_option == "Need extra biopsies from TI":
            # self.getExtraFrozenId()
            self.getExtraTIId()
            # to remove Frozen
            idx = 0
            while idx < len(self._barcode_list):
                if "Frozen_8" in self._barcode_list[idx] or "Frozen_9" in self._barcode_list[idx] or "Frozen_10" in self._barcode_list[idx]:
                    self._barcode_list[idx]=''
    
                idx += 1
        
            return self._barcode_list
        
        # elif custom_option == "No FRESH specimens, NO extra FROZEN specimens":
        #     idx = 0
        #     while idx < len(self._barcode_list):
        #         if "Fresh" in self._barcode_list[idx]:
        #             self._barcode_list[idx]=''
    
        #         idx += 1 
        #     return self._barcode_list
        
        # elif custom_option == "No FRESH specimens, ADD extra FROZEN specimens":
        #     self.getExtraFrozenId()
        #     idx = 0
        #     while idx < len(self._barcode_list):
        #         if "Fresh" in self._barcode_list[idx]:
        #             self._barcode_list[idx]=''
    
        #         idx += 1 
        #     return self._barcode_list
    
    def getSpecimenIndex(self,cur_id):
        """
        Make sure the id is two digit - used to convert specimen index in cheatsheet converter
        """
        int_cur_id = int(cur_id)
        if int_cur_id < 10:
            return '0%s' % str(int_cur_id)
        elif int_cur_id < 100:
            return '%s' % str(int_cur_id)
    
    def ean8_to_recordId(self,tmp_ean8_code):
        """
        record id is DoD_xxx_Frozen_123, ean8 code is the barcode to generate
        """
        eanConv = CheatSheetEAN_Converter()
        #"CD_ENDO", "CTL_ENDO", "CD_Surgery","CTL_Surgery"
        #ean8_code: type(1 digit)_cheatList(2 digit)_0_patientid(3 digit)_checksum(1 digit)
        tmp_studyType = tmp_ean8_code[0:1]
        
        print('woca %s' % tmp_studyType)
        if tmp_studyType == '1':
            self._studyType = 'CMA_PTSD'
        # if tmp_studyType == '1':
        #     self._studyType = 'UC_ENDO'
        # elif tmp_studyType == '2':
        #     self._studyType = 'CD_ENDO'
        # elif tmp_studyType == '3':        
        #     self._studyType = 'CTL_ENDO'
        # elif tmp_studyType == '4':         
        #     self._studyType = 'UC_Surgery'
        # elif tmp_studyType == '5':         
        #     self._studyType = 'CD_Surgery'
        # elif tmp_studyType == '6':         
        #     self._studyType = 'CTL_Surgery'
        # elif tmp_studyType == '7':         
        #     self._studyType = 'Cancer_Surgery'
        
        tmp_specimen_Id = int(tmp_ean8_code[1:3])
        print(tmp_specimen_Id)
        
        specimen_real_Id = ''
        
                  
#SHUNXING COMMENT DOD START                  
#         if self._studyType == 'CD_ENDO':
#             if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CD_ENDO_CHEAT_LIST)-1:
#                 return None
            
#             specimen_real_Id = eanConv.CD_ENDO_CHEAT_LIST[tmp_specimen_Id]
 
#         elif self._studyType == 'CTL_ENDO':
#             if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CTL_ENDO_CHEAT_LIST)-1:
#                 return None
            
#             specimen_real_Id = eanConv.CTL_ENDO_CHEAT_LIST[tmp_specimen_Id]

#         elif self._studyType == 'CD_Surgery':
#             if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CD_Surgery_CHEAT_LIST)-1:
#                 return None
#             print('here????')
#             specimen_real_Id = eanConv.CD_Surgery_CHEAT_LIST[tmp_specimen_Id]

#         elif self._studyType == 'CTL_Surgery':
#             if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CTL_Surgery_CHEAT_LIST)-1:
#                 return None
#             specimen_real_Id = eanConv.CTL_Surgery_CHEAT_LIST[tmp_specimen_Id]
#SHUNXING COMMENT DOD STOP

        # if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.DoD_Barcode_CHEAT_LIST)-1:
        if tmp_specimen_Id  < 0 or tmp_specimen_Id > len(eanConv.CMA_Barcode_CHEAT_LIST)-1:
            return None
            
        # specimen_real_Id = eanConv.DoD_Barcode_CHEAT_LIST[tmp_specimen_Id]
        # specimen_real_Id = eanConv.DoD_Barcode_CHEAT_LIST[tmp_specimen_Id]
        specimen_real_Id = eanConv.CMA_Barcode_CHEAT_LIST[tmp_specimen_Id]
 
        # tmp_barcode_id = 'DoD_' + tmp_ean8_code[4:7] + "_" + specimen_real_Id
        tmp_barcode_id = 'CMA_' + tmp_ean8_code[4:7] + "_" + specimen_real_Id
        print('ahahahahha' + tmp_barcode_id)
        return tmp_barcode_id
    
    
    def recordId_to_ean8(self,tmp_barcode_id):
        """
        record id is GCAxxxFrozenSomething, ean8 code is the barcode to generate
        """
        eanConv = CheatSheetEAN_Converter()
        #"UC_ENDO", "CD_ENDO", "CTL_ENDO", "UC_Surgery","CD_Surgery","CTL_Surgery" 
        
        ean8_code = ''# type(1 digit)_cheatList(2 digit)_0_patientid(3 digit)_checksum(1 digit)
#SHUNXING COMMENT DOD START
#         specimen_Id = tmp_barcode_id[6:len(tmp_barcode_id)]
#SHUNXING COMMENT DOD STOP
        # 6->8 is b/c change GCAxxx to DoD_xxx_
        specimen_Id = tmp_barcode_id[8:len(tmp_barcode_id)]
        
        print('#######################')
        print(specimen_Id)
        print('#######################')
        
        idx_specimen = ''
        
        if self._studyType == 'CMA_PTSD':
            ean8_code = '1'

        # if self._studyType == 'UC_ENDO':
        #     ean8_code = '1'
        # elif self._studyType == 'CD_ENDO':
        #     ean8_code = '2'
        # elif self._studyType == 'CTL_ENDO':
        #     ean8_code = '3'
        # elif self._studyType == 'UC_Surgery':
        #     ean8_code = '4'
        # elif self._studyType == 'CD_Surgery':
        #     ean8_code = '5'
        # elif self._studyType == 'CTL_Surgery':
        #     ean8_code = '6'
        # elif self._studyType == 'Cancer_Surgery':
        #     ean8_code = '7'
        
        # if specimen_Id in eanConv.DoD_Barcode_CHEAT_LIST:
        #     idx_specimen = eanConv.DoD_Barcode_CHEAT_LIST.index(specimen_Id)
        # else:
        #     return None
        print(eanConv.CMA_Barcode_CHEAT_LIST)
        
        if specimen_Id in eanConv.CMA_Barcode_CHEAT_LIST:
            idx_specimen = eanConv.CMA_Barcode_CHEAT_LIST.index(specimen_Id)
        else:
            return None
        
#SHUNXING COMMENT DOD START
#         ean8_code = ''# type(1 digit)_cheatList(2 digit)_0_patientid(3 digit)_checksum(1 digit)
#         specimen_Id = tmp_barcode_id[6:len(tmp_barcode_id)]
#         idx_specimen = ''
#         if self._studyType == 'CD_ENDO':
#             ean8_code = '1'
#             if specimen_Id in eanConv.CD_ENDO_CHEAT_LIST:
#                 idx_specimen = eanConv.CD_ENDO_CHEAT_LIST.index(specimen_Id)
#             else:
#                 return None
#         elif self._studyType == 'CTL_ENDO':
#             ean8_code = '2'
#             if specimen_Id in eanConv.CTL_ENDO_CHEAT_LIST:
#                 idx_specimen = eanConv.CTL_ENDO_CHEAT_LIST.index(specimen_Id)
#             else:
#                 return None
#         elif self._studyType == 'CD_Surgery':
#             ean8_code = '3'
#             if specimen_Id in eanConv.CD_Surgery_CHEAT_LIST:
#                 idx_specimen = eanConv.CD_Surgery_CHEAT_LIST.index(specimen_Id)
#             else:
#                 return None
#         elif self._studyType == 'CTL_Surgery':
#             ean8_code = '4'
#             if specimen_Id in eanConv.CTL_Surgery_CHEAT_LIST:
#                 idx_specimen = eanConv.CTL_Surgery_CHEAT_LIST.index(specimen_Id)
#             else:
#                 return None
#SHUNXING COMMENT DOD STOP

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
        
# COMMENT FOR GCA
#     def getBiopsiesCDEndoId(self):
#         self._barcode_list.append('DoD_%s_FreshTIA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTIA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTIA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshTIB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTIB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTIB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshACA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedACA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenACA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshACB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedACB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenACB' % self._subject_id)
        
#     def getBiopsiesCDEndoId(self):
#         self._barcode_list.append('DoD_%s_FreshTIA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTIA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTIA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshTIB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTIB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTIB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshACA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedACA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenACA' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshACB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedACB' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenACB' % self._subject_id)

#     def getBiopsiesCTLEndoId(self):
#         self._barcode_list.append('DoD_%s_FreshTI' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTI' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTI' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshAC' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedAC' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenAC' % self._subject_id)

#     def getBiopsiesCDSurgeryId(self):
#         self._barcode_list.append('DoD_%s_FreshTI' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTI' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTI' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshAC' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedAC' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenAC' % self._subject_id)

#     def getBiopsiesCTLSurgeryId(self):
#         self._barcode_list.append('DoD_%s_FreshTI1' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTI1' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTI1' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshTI2' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTI2' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTI2' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshTI3' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedTI3' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenTI3' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshAC4' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedAC4' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenAC4' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshAC5' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedAC5' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenAC5' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshAC6' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedAC6' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenAC6' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshAC7' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedAC7' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenAC7' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FreshAC8' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FixedAC8' % self._subject_id)
#         self._barcode_list.append('DoD_%s_FrozenAC8' % self._subject_id)
# Comment for GCA
#     def getStoolId(self):
#         self._barcode_list.append('DoD_%s_ST1' % self._subject_id) 
#         self._barcode_list.append('DoD_%s_ST2' % self._subject_id) 
#         self._barcode_list.append('DoD_%s_ST3' % self._subject_id) 
#         self._barcode_list.append('DoD_%s_ST4' % self._subject_id) 
            
        
    def main():
        print("Hello World!")

    if __name__== "__main__":
        main()
