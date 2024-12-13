import redcap
import pandas as pd
from collections import Counter

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from graphviz import Digraph
from datetime import datetime


class RedcapHelper:
    """
    Class for all redcap form import / export operations. 
    """
    
    def __init__(self, API_KEY):
        self.project = self.redcap_project_access(API_KEY)
        self.fieldsBarcode = ['barcode_sample_id',
                 'barcode_subject_type',
                 'barcode_aliquot_id',
                 'barcode_processed_by',
                 'barcode_action_date',
                 'barcode_action_type',
                 'barcode_freezer',
                 'barcode_rack',
                 'barcode_box_id',
                 'barcode_box_position',
                 'barcode_comment_note',
                 'barcode_ean8_code',
                 'barcode_custom_option'] # newly added for hacking simplified barcode 
        
    def redcap_project_access(self,API_KEY):
        """
        Access point to REDCap form
        :param API_KEY:string with REDCap database API_KEY
        :return: redcap Project Object
        """
        try:
            proj = redcap.Project('https://redcap.vanderbilt.edu/api/', API_KEY)
        except:
            LOGGER.error('ERROR: Could not access redcap. Either wrong API_URL/API_KEY or redcap down.')
            sys.exit(1)
        return proj
    
    def getRecordFromRedcap(self,events_arr, fields_arr):
        """
        Template to export record from redcap
        """
        record = self.project.export_records(events=events_arr,fields=fields_arr)
        return record
    
    def getBarcodeSubset(self):
        """
        Get all records in action_tuple_table_arm_3's barcode sample id field
        """
#        subset = self.project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id'])
        return self.getRecordFromRedcap(['action_tuple_table_arm_3'],['barcode_sample_id'])

#     def getInputPatient(self): # SHUNXING back up to get Input Patient, filed of 'record_id_dem_endo' is not very consistent
#         """
#         Get all patient entries from Sophie's redcap desgin
#         """
        
#         return self.getRecordFromRedcap(['cd_arm_1','control_arm_1','cd_arm_2','control_arm_2'],['record_id_dem_endo'])
    
    def getInputPatient(self):
        """
        Get all patient entries from Sophie's redcap desgin, remove field because sometimes it is very weird that recode_id_dem_endo is not fully shown.....
        """
        # remove fileds...
        return self.project.export_records(events=['cd_arm_1','control_arm_1','cd_arm_2','control_arm_2'])
        #return self.getRecordFromRedcap(['cd_arm_1','control_arm_1','cd_arm_2','control_arm_2'],['record_id_dem_endo'])
    
    def ifBarcodeExist(self, barcode_id):
        """
        fyi, if barcode exist
        """
        tmp_subset = self.getBarcodeSubset()
        if len(tmp_subset) == 0:
            return False
        
        data = pd.DataFrame.from_dict(tmp_subset)
        df = data.loc[data['barcode_sample_id'] == barcode_id]
        if len(df) == 0:
            return False
        else:
            return True
    
    def getBarcodeSubsetAndCustomOption(self):
        """
        Get all records in action_tuple_table_arm_3's barcode sample id field
        """
#        subset = self.project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id'])
        return self.getRecordFromRedcap(['action_tuple_table_arm_3'],['barcode_sample_id','barcode_custom_option'])
    
    
    
    def getSubjectLastestCustomOption(self, barcode_id,subject_id):
        """
        fyi, (1) check if barcode exist,
        (2) if barcode exist, get custom option
        (3) since the option may change from "Default" to "Need Extra Frozen"
        """    
        tmp_subset = self.getBarcodeSubsetAndCustomOption()
        if len(tmp_subset) == 0:
            return False
        
        data = pd.DataFrame.from_dict(tmp_subset)
        df = data.loc[data['barcode_sample_id'] == barcode_id]
        if len(df) == 0:
            return False
        else:
            # result in 'action_tuple_table_arm_3','barcode_sample_id','barcode_custom_option'
            idx = len(tmp_subset)-1
            tmp_custom_option = ''
            while idx >= 0:
                tmp_subj = tmp_subset[idx].get('barcode_sample_id')[3:6]
                if tmp_subj == subject_id:
                    tmp_custom_option = tmp_subset[idx].get('barcode_custom_option')
                    break
                idx -= 1
            
            return tmp_custom_option
     
    # for print Extra Frozen only
    def getCustomOptionOnly(self):
        """
        Get all records in action_tuple_table_arm_3's barcode sample id field
        """
#        subset = self.project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id'])
        return self.getRecordFromRedcap(['action_tuple_table_arm_3'],['barcode_sample_id','barcode_custom_option'])
       
    def getIfFreshNeedOrNot(self,subject_id):
        """
        fyi, (1) get custom option
        (3) since the option may change from "Default" to "Need Extra Frozen"
        """    
        tmp_subset = self.getCustomOptionOnly()
        if len(tmp_subset) == 0:
            return False
        
            # result in 'action_tuple_table_arm_3','barcode_sample_id','barcode_custom_option'
        idx = len(tmp_subset)-1
        tmp_custom_option = ''
        while idx >= 0:
            tmp_subj = tmp_subset[idx].get('barcode_sample_id')[3:6]
            if tmp_subj == subject_id:
                tmp_custom_option = tmp_subset[idx].get('barcode_custom_option')
                if tmp_custom_option == 'Default' or tmp_custom_option == '' or tmp_custom_option =='Need extra FROZEN specimens':
                    return 'Need extra FROZEN specimens'
                elif tmp_custom_option == 'No FRESH specimens, NO extra FROZEN specimens' or tmp_custom_option == 'No FRESH specimens, ADD extra FROZEN specimens':
                    return 'No FRESH specimens, ADD extra FROZEN specimens'    # for sake of re-print as well  
            idx -= 1
         
        return tmp_custom_option
    
    def delGetSubjectLastestCustomOption(self,subject_id):
        """
        fyi, (1) get custom option
        (3) since the option may change from "Default" to "Need Extra Frozen"
        """    
        tmp_subset = self.getCustomOptionOnly()
        if len(tmp_subset) == 0:
            return False
        
            # result in 'action_tuple_table_arm_3','barcode_sample_id','barcode_custom_option'
        idx = len(tmp_subset)-1
        tmp_custom_option = ''
        while idx >= 0:
            tmp_subj = tmp_subset[idx].get('barcode_sample_id')[3:6]
            if tmp_subj == subject_id:
                return tmp_subset[idx].get('barcode_custom_option') 
            idx -= 1
         
        return tmp_custom_option
            
    def getNextAvailActionId(self):
        """
        fyi, get next available action id.
        """
        subset = self.getBarcodeSubset()
        if len(subset) <= 1 or subset is None: # first action Id.
            curId = 0
        else:
            print('######################')
            print(subset)
            print('######################')
            print(subset[len(subset)-1].get('record_id_dem_endo'))
            print('######################')
            print(subset[len(subset)-1].get('record_id_dem_endo')[6:])
            print('######################')
            curId = int(subset[len(subset)-1].get('record_id_dem_endo')[6:]) # remove action from actionxxxx
        nextAvailActionId = curId + 1
        return nextAvailActionId
    
    def getCurrentTime(self):
        """
        fyi, get current time
        """
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        return str(cur_date)
    
#     def setGeneratedAction(self, actionId, barcode_id, studyType,processed_by,action_comment,ean8_code):
#         """
#         Set action: generated
#         If the barcode is serum, we need to set aliquot_id redcap field
#         """
#         aliquot_id = ''
#         if 'SR' in barcode_id: 
#             aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8
            
#         if action_comment == '':
#             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
#                           'redcap_event_name': 'action_tuple_table_arm_3',
#                           'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_aliquot_id' : aliquot_id,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_action_type' : 'generated',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]
#         else:
#             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
#                           'redcap_event_name': 'action_tuple_table_arm_3',
#                           'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_aliquot_id' : aliquot_id,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_action_type' : 'generated',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]
#         response = self.project.import_records(to_import)
#         return True

    def setPrintedAction(self, actionId, barcode_id, studyType,processed_by,action_comment,ean8_code,custom_option):
        """
        Set action: generated
        If the barcode is serum, we need to set aliquot_id redcap field
        """
        if barcode_id == '':
            return False
        
        aliquot_id = ''
        if 'SR' in barcode_id: 
            aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8
            
 #       if action_comment == '':
            to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_aliquot_id' : aliquot_id,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : 'printed',
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        else:
            to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : 'printed',
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        response = self.project.import_records(to_import)
        return True
    
#    def setReprintedAction(self, actionId, barcode_id, studyType,processed_by,action_type,action_comment,ean8_code):
    def setAction(self, actionId, barcode_id, studyType,processed_by,action_type,action_comment,ean8_code,custom_option):
        """
        action_type: 're-print',
                     'DNA distributed to Vantage', 
                     'DNA extracted and banked', 
                     'Distributed to Lau',
                     'Distributed to TPSR',
                     'Paraffin blocks back from TPSR',
                     'Distributed to Vantage'
        """
        aliquot_id = ''
        if 'SR' in barcode_id: 
            aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8
            
#        if action_comment == '':
            to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_aliquot_id' : aliquot_id,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : action_type,
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        else:
            to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : action_type,
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        response = self.project.import_records(to_import)
        return True
    

    
    
    def setScannedAction(self, actionId, barcode_id,studyType,processed_by,action_comment,ean8_code,custom_option):
        """
        Set action: scanned
        If the barcode is serum, we need to set aliquot_id redcap field
        """
            
        aliquot_id = ''
        if 'SR' in barcode_id: 
            aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8

#        if action_comment == '':
            to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_aliquot_id' : aliquot_id,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : 'scanned',
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        else:
            to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : 'scanned',
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        response = self.project.import_records(to_import)
        return True        
    
    def getProjectStats(self):
        """
        Get project stats, simply stats based on barcode_action_type.
        """
        dataset = self.project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_action_type'])
        data_proj = pd.DataFrame.from_dict(dataset)
        return str(data_proj['barcode_action_type'].value_counts())
     
    def getSubjectStats(self,barcode_list):
        """
        Get Subject stats, simply stats based on barcode_action_type.
        """
        dataset = self.project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id','barcode_action_type'])
        
        data_subj = pd.DataFrame.from_dict(dataset)
        
        df_filtered = data_subj[data_subj.barcode_sample_id.isin(barcode_list)]
        return str(df_filtered['barcode_action_type'].value_counts())
    
    def getBarcodeStats(self,barcode_id):
        """
        Get barcode stats, print all actions (ugly for now..)
        """
        dataset = self.project.export_records(events=['action_tuple_table_arm_3'],fields=self.fieldsBarcode)
        
        data_barcode = pd.DataFrame.from_dict(dataset)
        df_filtered = data_barcode[(data_barcode.barcode_sample_id == barcode_id)]
        
        return str(df_filtered)
#         cur_time = self.getCurrentTime()
#         csvFilepath = '%s_%s.csv' %(barcode_id, str(cur_time))
#         export_csv = df_filtered.to_csv (csvFilepath, index = None, header=True)
        
#        return csvFilepath

    
################# UPDATE SOPHIE's REDCAP
    def update_REDCAP_SOPHIE(self,study_type,subject_id,barcode_id_list,custom_option):
        # fresh is '' so no need to worry if it is empty... hacking fun
        if custom_option == 'Default' or custom_option == 'No FRESH specimens, NO extra FROZEN specimens':
            if study_type == 'CD_ENDO':
                self.update_CD_END_SOPHIE(subject_id,barcode_id_list)
            elif study_type == 'CTL_ENDO':
                self.update_CTL_END_SOPHIE(subject_id,barcode_id_list)
            elif study_type == 'CD_Surgery':
                self.update_CD_Surgery_SOPHIE(subject_id,barcode_id_list)
            elif study_type == 'CTL_Surgery':
                self.update_CTL_Surgery_SOPHIE(subject_id,barcode_id_list)  
    
        # fresh is '' so no need to worry if it is empty... hacking fun
        elif custom_option == 'Need extra FROZEN specimens' or custom_option == 'No FRESH specimens, ADD extra FROZEN specimens':
            if study_type == 'CD_ENDO':
                self.update_CD_END_SOPHIE_extra_frozen(subject_id,barcode_id_list)
            elif study_type == 'CTL_ENDO':
                self.update_CTL_END_SOPHIE_extra_frozen(subject_id,barcode_id_list)
            elif study_type == 'CD_Surgery':
                self.update_CD_Surgery_SOPHIE_extra_frozen(subject_id,barcode_id_list)
            elif study_type == 'CTL_Surgery':
                self.update_CTL_Surgery_SOPHIE_extra_frozen(subject_id,barcode_id_list) 
        
            
            
#     def update_REDCAP_SOPHIE(self,study_type,subject_id,barcode_id_list, if_Extra_Frozen):
#         if if_Extra_Frozen:
#             if study_type == 'CD_ENDO':
#                 self.update_CD_END_SOPHIE_extra_frozen(subject_id,barcode_id_list)
#             elif study_type == 'CTL_ENDO':
#                 self.update_CTL_END_SOPHIE_extra_frozen(subject_id,barcode_id_list)
#             elif study_type == 'CD_Surgery':
#                 self.update_CD_Surgery_SOPHIE_extra_frozen(subject_id,barcode_id_list)
#             elif study_type == 'CTL_Surgery':
#                 self.update_CTL_Surgery_SOPHIE_extra_frozen(subject_id,barcode_id_list) 
#         else:
#             if study_type == 'CD_ENDO':
#                 self.update_CD_END_SOPHIE(subject_id,barcode_id_list)
#             elif study_type == 'CTL_ENDO':
#                 self.update_CTL_END_SOPHIE(subject_id,barcode_id_list)
#             elif study_type == 'CD_Surgery':
#                 self.update_CD_Surgery_SOPHIE(subject_id,barcode_id_list)
#             elif study_type == 'CTL_Surgery':
#                 self.update_CTL_Surgery_SOPHIE(subject_id,barcode_id_list)      
        
    def update_CD_END_SOPHIE(self,subject_id,barcode_id_list):
   #     curTime = datetime.now()
   #     cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        to_import = [{'record_id_dem_endo':subject_id,
                        'redcap_event_name':'cd_arm_1',
                        'stool_collected_endo_cd_v2':'1',
                        'specimen_stool_num_al':'4',
                        'specimen_stool_id_ali':barcode_id_list[0],
                        'specimen_stool_id_ali_1':barcode_id_list[1],
                        'specimen_stool_id_ali_2':barcode_id_list[2],
                        'specimen_stool_id_ali_3':barcode_id_list[3],
                        'serum_collected_endo_cd_v2':'1',
                        'specimen_serum_al_100':'3',
                        'specimen_serum_al_1_100_id':barcode_id_list[4],
                        'specimen_serum_al_2_100_id':barcode_id_list[5],
                        'specimen_serum_al_3_100':barcode_id_list[6],
                        'specimen_serum_al_250':'1',
                        'specimen_serum_al_250_1':barcode_id_list[7],
                        'specimen_serum_al_500':'7',
                        'specimen_serum_al_500_1':barcode_id_list[8],
                        'specimen_serum_al_500_2':barcode_id_list[9],
                        'specimen_serum_al_500_3':barcode_id_list[10],
                        'specimen_serum_al_500_4':barcode_id_list[11],
                        'specimen_serum_al_500_5':barcode_id_list[12],
                        'specimen_serum_al_500_6':barcode_id_list[13],
                        'specimen_serum_al_500_7':barcode_id_list[14],
                        'dna_collected_endo_cd_v2':'1',
                        'specimen_dna_id':barcode_id_list[15],
                        'cd_endo_ti_a_fresh_id':barcode_id_list[16],
                        'sc_endo_ti_a_fixed_id':barcode_id_list[17],
                        'cd_endo_ti_a_frozen_id':barcode_id_list[18],
                        'cd_endo_ti_b_fresh_id':barcode_id_list[19],
                        'cd_endo_ti_b_fixed_id':barcode_id_list[20],
                        'cd_endo_ti_b_frozen_id':barcode_id_list[21],
                        'cd_endo_ac_a_fresh_id':barcode_id_list[22],
                        'cd_endo_ac_a_fixed_id':barcode_id_list[23],
                        'cd_endo_ac_a_frozen_id':barcode_id_list[24],
                        'cd_endo_ac_b_fresh_id':barcode_id_list[25],
                        'cd_endo_ac_b_fixed_id':barcode_id_list[26],
                        'cd_endo_ac_b_frozen_id':barcode_id_list[27],
                        'cd_endo_biopsy_id':barcode_id_list[18],
                        'cd_endo_biopsy_id2':barcode_id_list[21],
                        'cd_endo_biopsy_id3':barcode_id_list[24],
                        'cd_endo_biopsy_id4':barcode_id_list[27]}]
        response = self.project.import_records(to_import)
        return True  
    
    def update_CTL_END_SOPHIE(self,subject_id,barcode_id_list):   
   #     curTime = datetime.now()
   #     cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        to_import = [{'record_id_dem_endo':subject_id,
                        'redcap_event_name':'control_arm_1',
                        'stool_collected_endo_cd_v2':'1',
                        'specimen_stool_num_al':'4',
                        'specimen_stool_id_ali':barcode_id_list[0],
                        'specimen_stool_id_ali_1':barcode_id_list[1],
                        'specimen_stool_id_ali_2':barcode_id_list[2],
                        'specimen_stool_id_ali_3':barcode_id_list[3],
                        'serum_collected_endo_cd_v2':'1',
                        'specimen_serum_al_100':'3',
                        'specimen_serum_al_1_100_id':barcode_id_list[4],
                        'specimen_serum_al_2_100_id':barcode_id_list[5],
                        'specimen_serum_al_3_100':barcode_id_list[6],
                        'specimen_serum_al_250':'1',
                        'specimen_serum_al_250_1':barcode_id_list[7],
                        'specimen_serum_al_500':'7',
                        'specimen_serum_al_500_1':barcode_id_list[8],
                        'specimen_serum_al_500_2':barcode_id_list[9],
                        'specimen_serum_al_500_3':barcode_id_list[10],
                        'specimen_serum_al_500_4':barcode_id_list[11],
                        'specimen_serum_al_500_5':barcode_id_list[12],
                        'specimen_serum_al_500_6':barcode_id_list[13],
                        'specimen_serum_al_500_7':barcode_id_list[14],
                        'dna_collected_endo_cd_v2':'1',
                        'specimen_dna_id':barcode_id_list[15],
                        'ctl_endo_ti_fresh_id':barcode_id_list[16],
                        'ctl_endo_ti_fixed_id':barcode_id_list[17],
                        'ctl_endo_ti_frozen_id':barcode_id_list[18],
                        'ctl_endo_ac_fresh_id':barcode_id_list[19],
                        'ctl_endo_ac_fixed_id':barcode_id_list[20],
                        'ctl_endo_ac_frozen_id':barcode_id_list[21],
                        'ctl_endo_biopsy_id_1':barcode_id_list[18],
                        'ctl_endo_biopsy_id_2':barcode_id_list[21]}]
        response = self.project.import_records(to_import)
        return True  
    
    def update_CD_Surgery_SOPHIE(self,subject_id,barcode_id_list):  
 #       curTime = datetime.now()
 #       cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        to_import = [{'record_id_dem_endo':subject_id,
                        'redcap_event_name':'cd_arm_2',
                        'cd_surgery_ti_fresh_id':barcode_id_list[0],
                        'cd_surgery_ti_fixed_id':barcode_id_list[1],
                        'cd_surgery_ti_frozen_id':barcode_id_list[2],
                        'cd_surgery_ac_fresh_id':barcode_id_list[3],
                        'cd_surgery_ac_fixed_id':barcode_id_list[4],
                        'cd_surgery_ac_frozen_id':barcode_id_list[5],
                        'cd_surg_biopsy_id_1':barcode_id_list[2],
                        'cd_surg_biopsy_id_2':barcode_id_list[5]}]
        response = self.project.import_records(to_import)
        return True

    def update_CTL_Surgery_SOPHIE(self,subject_id,barcode_id_list):  
#       curTime = datetime.now()
#        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        to_import = [{'record_id_dem_endo':subject_id,
                        'redcap_event_name':'control_arm_2',
                        'ctl_surgery_ti_1_fresh_id':barcode_id_list[0],
                        'ctl_surgery_ti_1_fixed_id':barcode_id_list[1],
                        'ctl_surgery_ti_1_frozen_id':barcode_id_list[2],
                        'ctl_surgery_ti_2_fresh_id':barcode_id_list[3],
                        'ctl_surgery_ti_2_fixed_id':barcode_id_list[4],
                        'ctl_surgery_ti_2_frozen_id':barcode_id_list[5],
                        'ctl_surgery_ti_3_fresh_id':barcode_id_list[6],
                        'ctl_surgery_ti_3_fixed_id':barcode_id_list[7],
                        'ctl_surgery_ti_3_frozen_id':barcode_id_list[8],
                        'ctl_surgery_ac_4_fresh_id':barcode_id_list[9],
                        'ctl_surgery_ac_4_fixed_id':barcode_id_list[10],
                        'ctl_surgery_ac_4_frozen_id':barcode_id_list[11],
                        'ctl_surgery_ac_5_fresh_id':barcode_id_list[12],
                        'ctl_surgery_ac_5_fixed_id':barcode_id_list[13],
                        'ctl_surgery_ac_5_frozen_id':barcode_id_list[14],
                        'ctl_surgery_ac_6_fresh_id':barcode_id_list[15],
                        'ctl_surgery_ac_6_fixed_id':barcode_id_list[16],
                        'ctl_surgery_ac_6_frozen_id':barcode_id_list[17],
                        'ctl_surgery_ac_7_fresh_id':barcode_id_list[18],
                        'ctl_surgery_ac_7_fixed_id':barcode_id_list[19],
                        'ctl_surgery_ac_7_frozen_id':barcode_id_list[20],
                        'ctl_surgery_ac_8_fresh_id':barcode_id_list[21],
                        'ctl_surgery_ac_8_fixed_id':barcode_id_list[22],
                        'ctl_surgery_ac_8_frozen_id':barcode_id_list[23],
                        'ctl_surg_biopsy_id_1':barcode_id_list[2],
                        'ctl_surg_biopsy_id_2':barcode_id_list[5],
                        'ctl_surg_biopsy_id_3':barcode_id_list[8],
                        'ctl_surg_biopsy_id_4':barcode_id_list[11],
                        'ctl_surg_biopsy_id_5':barcode_id_list[14],
                        'ctl_surg_biopsy_id_6':barcode_id_list[17],
                        'ctl_surg_biopsy_id_7':barcode_id_list[20],
                        'ctl_surg_biopsy_id_8':barcode_id_list[23]}]
        response = self.project.import_records(to_import)
        return True
    
    
    def update_CD_END_SOPHIE_extra_frozen(self,subject_id,barcode_id_list):
        to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'stool_collected_endo_cd_v2':'1',
   #                     'stool_collection_endo_cd_v2':str(cur_date),
                          'specimen_stool_num_al':'4',
                          'specimen_stool_id_ali':barcode_id_list[0],
                          'specimen_stool_id_ali_1':barcode_id_list[1],
                          'specimen_stool_id_ali_2':barcode_id_list[2],
                          'specimen_stool_id_ali_3':barcode_id_list[3],
                          'serum_collected_endo_cd_v2':'1',
                          'specimen_serum_al_100':'3',
                          'specimen_serum_al_1_100_id':barcode_id_list[4],
                          'specimen_serum_al_2_100_id':barcode_id_list[5],
                          'specimen_serum_al_3_100':barcode_id_list[6],
                          'specimen_serum_al_250':'1',
                          'specimen_serum_al_250_1':barcode_id_list[7],
                          'specimen_serum_al_500':'7',
                          'specimen_serum_al_500_1':barcode_id_list[8],
                          'specimen_serum_al_500_2':barcode_id_list[9],
                          'specimen_serum_al_500_3':barcode_id_list[10],
                          'specimen_serum_al_500_4':barcode_id_list[11],
                          'specimen_serum_al_500_5':barcode_id_list[12],
                          'specimen_serum_al_500_6':barcode_id_list[13],
                          'specimen_serum_al_500_7':barcode_id_list[14],
                          'dna_collected_endo_cd_v2':'1',
                          'specimen_dna_id':barcode_id_list[15],
                          'cd_endo_ti_a_fresh_id':barcode_id_list[16],
                          'sc_endo_ti_a_fixed_id':barcode_id_list[17],
                          'cd_endo_ti_a_frozen_id':barcode_id_list[18],
                          'cd_endo_ti_b_fresh_id':barcode_id_list[19],
                          'cd_endo_ti_b_fixed_id':barcode_id_list[20],
                          'cd_endo_ti_b_frozen_id':barcode_id_list[21],
                          'cd_endo_ac_a_fresh_id':barcode_id_list[22],
                          'cd_endo_ac_a_fixed_id':barcode_id_list[23],
                          'cd_endo_ac_a_frozen_id':barcode_id_list[24],
                          'cd_endo_ac_b_fresh_id':barcode_id_list[25],
                          'cd_endo_ac_b_fixed_id':barcode_id_list[26],
                          'cd_endo_ac_b_frozen_id':barcode_id_list[27],
                          'cd_endo_biopsy_id':barcode_id_list[18],
                          'cd_endo_biopsy_id2':barcode_id_list[21],
                          'cd_endo_biopsy_id3':barcode_id_list[24],
                          'cd_endo_biopsy_id4':barcode_id_list[27],
                          'second_frozen': '1',
                          'ti_add_frozen_a_id': barcode_id_list[28],
                          'ti_add_frozen_b_id': barcode_id_list[29],
                          'ac_add_frozen_a_id': barcode_id_list[30],
                          'ac_add_frozen_b_id': barcode_id_list[31],
                          'cd_endo_add_ti_a_id': barcode_id_list[28],
                          'cd_endo_add_ti_b_id': barcode_id_list[29],
                          'cd_endo_add_ac_a_id': barcode_id_list[30],
                          'cd_endo_add_ac_b_id': barcode_id_list[31]}]
        
        response = self.project.import_records(to_import)
        return True  
    
    def update_CTL_END_SOPHIE_extra_frozen(self,subject_id,barcode_id_list):   
   #     curTime = datetime.now()
   #     cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        to_import = [{'record_id_dem_endo':subject_id,
                        'redcap_event_name':'control_arm_1',
                        'stool_collected_endo_cd_v2':'1',
                        'specimen_stool_num_al':'4',
                        'specimen_stool_id_ali':barcode_id_list[0],
                        'specimen_stool_id_ali_1':barcode_id_list[1],
                        'specimen_stool_id_ali_2':barcode_id_list[2],
                        'specimen_stool_id_ali_3':barcode_id_list[3],
                        'serum_collected_endo_cd_v2':'1',
                        'specimen_serum_al_100':'3',
                        'specimen_serum_al_1_100_id':barcode_id_list[4],
                        'specimen_serum_al_2_100_id':barcode_id_list[5],
                        'specimen_serum_al_3_100':barcode_id_list[6],
                        'specimen_serum_al_250':'1',
                        'specimen_serum_al_250_1':barcode_id_list[7],
                        'specimen_serum_al_500':'7',
                        'specimen_serum_al_500_1':barcode_id_list[8],
                        'specimen_serum_al_500_2':barcode_id_list[9],
                        'specimen_serum_al_500_3':barcode_id_list[10],
                        'specimen_serum_al_500_4':barcode_id_list[11],
                        'specimen_serum_al_500_5':barcode_id_list[12],
                        'specimen_serum_al_500_6':barcode_id_list[13],
                        'specimen_serum_al_500_7':barcode_id_list[14],
                        'dna_collected_endo_cd_v2':'1',
                        'specimen_dna_id':barcode_id_list[15],
                        'ctl_endo_ti_fresh_id':barcode_id_list[16],
                        'ctl_endo_ti_fixed_id':barcode_id_list[17],
                        'ctl_endo_ti_frozen_id':barcode_id_list[18],
                        'ctl_endo_ac_fresh_id':barcode_id_list[19],
                        'ctl_endo_ac_fixed_id':barcode_id_list[20],
                        'ctl_endo_ac_frozen_id':barcode_id_list[21],
                        'ctl_endo_biopsy_id_1':barcode_id_list[18],
                        'ctl_endo_biopsy_id_2':barcode_id_list[21],
                        'ctl_endo_second_frozen': '1',
                        'ctl_endo_add_ti_id': barcode_id_list[22],
                        'ctl_endo_add_ac_id': barcode_id_list[23],
                        'ctl_endo_biopsy_id_3': barcode_id_list[22],
                        'ctl_endo_biopsy_id_4': barcode_id_list[23]}]
                  
        response = self.project.import_records(to_import)
        return True  
    
    def update_CD_Surgery_SOPHIE_extra_frozen(self,subject_id,barcode_id_list):  
 #       curTime = datetime.now()
 #       cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        to_import = [{'record_id_dem_endo':subject_id,
                        'redcap_event_name':'cd_arm_2',
#                         'date_of_biopsies_collect_endo_cd_v2':str(cur_date),
#                         'cd_sur_bio_ti___1':'1',
#                         'cd_sur_bio_ti___2':'1',
#                         'cd_sur_bio_ti___3':'1',
#                         'cd_sur_bio_ac___1':'1',
#                         'cd_sur_bio_ac___2':'1',
#                         'cd_sur_bio_ac___3':'1',
                        'cd_surgery_ti_fresh_id':barcode_id_list[0],
                        'cd_surgery_ti_fixed_id':barcode_id_list[1],
                        'cd_surgery_ti_frozen_id':barcode_id_list[2],
                        'cd_surgery_ac_fresh_id':barcode_id_list[3],
                        'cd_surgery_ac_fixed_id':barcode_id_list[4],
                        'cd_surgery_ac_frozen_id':barcode_id_list[5],
                        'cd_surg_biopsy_id_1':barcode_id_list[2],
                        'cd_surg_biopsy_id_2':barcode_id_list[5],
                        'cd_sur_add_biopsies': '1',
                        'cd_sur_ti_add_id': barcode_id_list[6],
                        'cd_sur_ac_add_id': barcode_id_list[7],
                        'cd_surg_biopsy_id_3': barcode_id_list[6],
                        'cd_surg_biopsy_id_4': barcode_id_list[7]}]
        response = self.project.import_records(to_import)
        return True

    def update_CTL_Surgery_SOPHIE_extra_frozen(self,subject_id,barcode_id_list):  
        to_import = [{'record_id_dem_endo':subject_id,
                        'redcap_event_name':'control_arm_2',
                        'ctl_surgery_ti_1_fresh_id':barcode_id_list[0],
                        'ctl_surgery_ti_1_fixed_id':barcode_id_list[1],
                        'ctl_surgery_ti_1_frozen_id':barcode_id_list[2],
                        'ctl_surgery_ti_2_fresh_id':barcode_id_list[3],
                        'ctl_surgery_ti_2_fixed_id':barcode_id_list[4],
                        'ctl_surgery_ti_2_frozen_id':barcode_id_list[5],
                        'ctl_surgery_ti_3_fresh_id':barcode_id_list[6],
                        'ctl_surgery_ti_3_fixed_id':barcode_id_list[7],
                        'ctl_surgery_ti_3_frozen_id':barcode_id_list[8],
                        'ctl_surgery_ac_4_fresh_id':barcode_id_list[9],
                        'ctl_surgery_ac_4_fixed_id':barcode_id_list[10],
                        'ctl_surgery_ac_4_frozen_id':barcode_id_list[11],
                        'ctl_surgery_ac_5_fresh_id':barcode_id_list[12],
                        'ctl_surgery_ac_5_fixed_id':barcode_id_list[13],
                        'ctl_surgery_ac_5_frozen_id':barcode_id_list[14],
                        'ctl_surgery_ac_6_fresh_id':barcode_id_list[15],
                        'ctl_surgery_ac_6_fixed_id':barcode_id_list[16],
                        'ctl_surgery_ac_6_frozen_id':barcode_id_list[17],
                        'ctl_surgery_ac_7_fresh_id':barcode_id_list[18],
                        'ctl_surgery_ac_7_fixed_id':barcode_id_list[19],
                        'ctl_surgery_ac_7_frozen_id':barcode_id_list[20],
                        'ctl_surgery_ac_8_fresh_id':barcode_id_list[21],
                        'ctl_surgery_ac_8_fixed_id':barcode_id_list[22],
                        'ctl_surgery_ac_8_frozen_id':barcode_id_list[23],
                        'ctl_surg_biopsy_id_1':barcode_id_list[2],
                        'ctl_surg_biopsy_id_2':barcode_id_list[5],
                        'ctl_surg_biopsy_id_3':barcode_id_list[8],
                        'ctl_surg_biopsy_id_4':barcode_id_list[11],
                        'ctl_surg_biopsy_id_5':barcode_id_list[14],
                        'ctl_surg_biopsy_id_6':barcode_id_list[17],
                        'ctl_surg_biopsy_id_7':barcode_id_list[20],
                        'ctl_surg_biopsy_id_8':barcode_id_list[23],
                        'ctl_sur_add_collec': '1',
                        'ctl_sur_ti_1_add_id': barcode_id_list[24],
                        'ctl_sur_ti_2_add_id': barcode_id_list[25],
                        'ctl_sur_ti_3_add_id': barcode_id_list[26],
                        'ctl_sur_ac_4_add_id': barcode_id_list[27],
                        'ctl_sur_ac_5_add_id': barcode_id_list[28],
                        'ctl_sur_ac_6_add_id': barcode_id_list[29],
                        'ctl_sur_ac_7_add_id': barcode_id_list[30],
                        'ctl_sur_ac_8_add_id': barcode_id_list[31],
                        'ctl_surg_biopsy_1_id_add': barcode_id_list[24],
                        'ctl_sur_add_bio_id_2': barcode_id_list[25],
                        'ctl_sur_add_bio_id_3': barcode_id_list[26],
                        'ctl_sur_ac_add_bio_id_4': barcode_id_list[27],
                        'ctl_sur_add_bio_id_5': barcode_id_list[28],
                        'ctl_sur_add_bio_id_6': barcode_id_list[29],
                        'ctl_sur_add_bio_id_7': barcode_id_list[30],
                        'ctl_sur_add_bio_id_8': barcode_id_list[31]}]
        response = self.project.import_records(to_import)
        return True
    
    # Modified to add more add frozen specimen...
    def update_REDCAP_SOPHIE_EXTRA_FROZEN(self,study_type,subject_id,barcode_id_list, custom_option):
        # if is not needed actually...
        # Since sophie use same variables... we only have one function then....once find subject
        if custom_option == 'Need extra FROZEN specimens' or custom_option == 'No FRESH specimens, ADD extra FROZEN specimens':
            if study_type == 'CD_ENDO':
                to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'second_frozen': '1',
                          'ti_add_frozen_a_id': barcode_id_list[0],
                          'ti_add_frozen_b_id': barcode_id_list[1],
                          'ac_add_frozen_a_id': barcode_id_list[2],
                          'ac_add_frozen_b_id': barcode_id_list[3],
                          'cd_endo_add_ti_a_id': barcode_id_list[0],
                          'cd_endo_add_ti_b_id': barcode_id_list[1],
                          'cd_endo_add_ac_a_id': barcode_id_list[2],
                          'cd_endo_add_ac_b_id': barcode_id_list[3]}]
        
                response = self.project.import_records(to_import)
                return True
            elif study_type == 'CTL_ENDO':
                to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_1',
                          'ctl_endo_second_frozen': '1',
                          'ctl_endo_add_ti_id': barcode_id_list[0],
                          'ctl_endo_add_ac_id': barcode_id_list[1],
                          'ctl_endo_biopsy_id_3': barcode_id_list[0],
                          'ctl_endo_biopsy_id_4': barcode_id_list[1]}]
        
                response = self.project.import_records(to_import)
                return True
            elif study_type == 'CD_Surgery':
                to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_2',
                          'cd_sur_add_biopsies': '1',
                          'cd_sur_ti_add_id': barcode_id_list[0],
                          'cd_sur_ac_add_id': barcode_id_list[1],
                          'cd_surg_biopsy_id_3': barcode_id_list[0],
                          'cd_surg_biopsy_id_4': barcode_id_list[1]}]
        
                response = self.project.import_records(to_import)
                return True
            elif study_type == 'CTL_Surgery':
                to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_sur_add_collec': '1',
                          'ctl_sur_ti_1_add_id': barcode_id_list[0],
                          'ctl_sur_ti_2_add_id': barcode_id_list[1],
                          'ctl_sur_ti_3_add_id': barcode_id_list[2],
                          'ctl_sur_ac_4_add_id': barcode_id_list[3],
                          'ctl_sur_ac_5_add_id': barcode_id_list[4],
                          'ctl_sur_ac_6_add_id': barcode_id_list[5],
                          'ctl_sur_ac_7_add_id': barcode_id_list[6],
                          'ctl_sur_ac_8_add_id': barcode_id_list[7],
                          'ctl_surg_biopsy_1_id_add': barcode_id_list[0],
                          'ctl_sur_add_bio_id_2': barcode_id_list[1],
                          'ctl_sur_add_bio_id_3': barcode_id_list[2],
                          'ctl_sur_ac_add_bio_id_4': barcode_id_list[3],
                          'ctl_sur_add_bio_id_5': barcode_id_list[4],
                          'ctl_sur_add_bio_id_6': barcode_id_list[5],
                          'ctl_sur_add_bio_id_7': barcode_id_list[6],
                          'ctl_sur_add_bio_id_8': barcode_id_list[7]}]
        
                response = self.project.import_records(to_import)
                return True
            
        return False         
        
    def update_REDCAP_SOPHIE_EXTRA_SERUM(self,study_type,subject_id,barcode_id_list):
        # if is not needed actually...
        # Since sophie use same variables... we only have one function then....once find subject
        if study_type == 'CD_ENDO' :
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'specimen_serum_al_500':'7',
                          'specimen_serum_al_500_5':barcode_id_list[0],
                          'specimen_serum_al_500_6':barcode_id_list[1],
                          'specimen_serum_al_500_7':barcode_id_list[2],}] 
        
            response = self.project.import_records(to_import)
            return True
        elif study_type == 'CTL_ENDO':
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_1',
                          'specimen_serum_al_500':'7',
                          'specimen_serum_al_500_5':barcode_id_list[0],
                          'specimen_serum_al_500_6':barcode_id_list[1],
                          'specimen_serum_al_500_7':barcode_id_list[2],}] 
        
            response = self.project.import_records(to_import)
            return True
        
          
               
#    def addBarcodePackToRedcap_CD_ENDO(self,subject_id):
#        to_import = [{'record_id_dem_endo': '%s' % str(int(subject_id)),
#                        'redcap_event_name': 'action_tuple_table_arm_3',
#                        'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_freezer' : freezer,
#                           'barcode_rack' : rack,
#                           'barcode_box_id' : box_id,
#                           'barcode_box_position' : box_position,
#                           'barcode_action_type' : 'scanned',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]

# def setScannedAction(self, actionId, barcode_id,studyType,processed_by,action_comment,freezer,rack,box_id,box_position,ean8_code):
#         aliquot_id = ''
#         if 'SR' in barcode_id: 
#             aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8

# #        if action_comment == '':
#             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
#                           'redcap_event_name': 'action_tuple_table_arm_3',
#                           'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_aliquot_id' : aliquot_id,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_freezer' : freezer,
#                           'barcode_rack' : rack,
#                           'barcode_box_id' : box_id,
#                           'barcode_box_position' : box_position,
#                           'barcode_action_type' : 'scanned',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]
#         else:
#             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
#                           'redcap_event_name': 'action_tuple_table_arm_3',
#                           'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_freezer' : freezer,
#                           'barcode_rack' : rack,
#                           'barcode_box_id' : box_id,
#                           'barcode_box_position' : box_position,
#                           'barcode_action_type' : 'scanned',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]
#         response = self.project.import_records(to_import)
#         return True 


    def update_REDCAP_SOPHIE_SINGLE_BARCODE(self,study_type,subject_id,barcode_id,custom_option):
        # fresh is '' so no need to worry if it is empty... hacking fun
        if custom_option == 'Default' or custom_option == 'No FRESH specimens, NO extra FROZEN specimens':
            if study_type == 'CD_ENDO':
                self.update_CD_END_SOPHIE_SINGLE_BARCODE(subject_id,barcode_id)
            elif study_type == 'CTL_ENDO':
                self.update_CTL_END_SOPHIE_SINGLE_BARCODE(subject_id,barcode_id)
            elif study_type == 'CD_Surgery':
                self.update_CD_Surgery_SOPHIE_SINGLE_BARCODE(subject_id,barcode_id)
            elif study_type == 'CTL_Surgery':
                self.update_CTL_Surgery_SOPHIE_SINGLE_BARCODE(subject_id,barcode_id)  
    
        # fresh is '' so no need to worry if it is empty... hacking fun
        elif custom_option == 'Need extra FROZEN specimens' or custom_option == 'No FRESH specimens, ADD extra FROZEN specimens':
            if study_type == 'CD_ENDO':
                self.update_CD_END_SOPHIE_extra_frozen_SINGLE_BARCODE(subject_id,barcode_id)
            elif study_type == 'CTL_ENDO':
                self.update_CTL_END_SOPHIE_extra_frozen_SINGLE_BARCODE(subject_id,barcode_id)
            elif study_type == 'CD_Surgery':
                self.update_CD_Surgery_SOPHIE_extra_frozen_SINGLE_BARCODE(subject_id,barcode_id)
            elif study_type == 'CTL_Surgery':
                self.update_CTL_Surgery_SOPHIE_extra_frozen_SINGLE_BARCODE(subject_id,barcode_id) 
                
    def update_CD_END_SOPHIE_SINGLE_BARCODE(self,subject_id,barcode_id):
        if barcode_id[-3:]=='ST1':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'stool_collected_endo_cd_v2':'1',
                            'specimen_stool_num_al':'4',
                            'specimen_stool_id_ali':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')

        elif barcode_id[-3:]=='ST2':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'stool_collected_endo_cd_v2':'1',
                            'specimen_stool_num_al':'4',
                            'specimen_stool_id_ali_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
  
        elif barcode_id[-3:]=='ST3':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'stool_collected_endo_cd_v2':'1',
                            'specimen_stool_num_al':'4',
                            'specimen_stool_id_ali_2':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
        
        elif barcode_id[-3:]=='ST4':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'stool_collected_endo_cd_v2':'1',
                            'specimen_stool_num_al':'4',
                            'specimen_stool_id_ali_3':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-3:]=='SR1':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_100':'3',
                            'specimen_serum_al_1_100_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
        
        elif barcode_id[-3:]=='SR2': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_100':'3',
                            'specimen_serum_al_2_100_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 
            
        elif barcode_id[-3:]=='SR3': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_100':'3',
                            'specimen_serum_al_3_100':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')

        elif barcode_id[-3:]=='SR4': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_250':'1',
                            'specimen_serum_al_250_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-3:]=='SR5': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_250_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-3:]=='SR6': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_2':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-3:]=='SR7': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_3':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-3:]=='SR8': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_4':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-3:]=='SR9': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_5':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-4:]=='SR10': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_6':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-4:]=='SR11': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_7':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-3:]=='DNA': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'dna_collected_endo_cd_v2':'1',
                            'specimen_dna_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
        
        elif barcode_id[-8:]=='FreshTIA': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'cd_endo_ti_a_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTIA': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'sc_endo_ti_a_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-9:]=='FrozenTIA': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'cd_endo_ti_a_frozen_id':barcode_id,
                          'cd_endo_biopsy_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FreshTIB': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'cd_endo_ti_b_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTIB': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'cd_endo_ti_b_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-9:]=='FrozenTIB': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'cd_endo_ti_b_frozen_id':barcode_id,
                          'cd_endo_biopsy_id2':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-8:]=='FreshACA': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'cd_endo_ac_a_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedACA': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'cd_endo_ac_a_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-9:]=='FrozenACA': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'cd_endo_ac_a_frozen_id':barcode_id,
                          'cd_endo_biopsy_id3':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')

        elif barcode_id[-8:]=='FreshACB': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'cd_endo_ac_b_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedACB': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'cd_endo_ac_b_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-9:]=='FrozenACB': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'cd_endo_ac_b_frozen_id':barcode_id,
                          'cd_endo_biopsy_id4':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        return True                  
                
    def update_CTL_END_SOPHIE_SINGLE_BARCODE(self,subject_id,barcode_id):   
        if barcode_id[-3:]=='ST1':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'stool_collected_endo_cd_v2':'1',
                            'specimen_stool_num_al':'4',
                            'specimen_stool_id_ali':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')

        elif barcode_id[-3:]=='ST2':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'stool_collected_endo_cd_v2':'1',
                            'specimen_stool_num_al':'4',
                            'specimen_stool_id_ali_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
  
        elif barcode_id[-3:]=='ST3':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'stool_collected_endo_cd_v2':'1',
                            'specimen_stool_num_al':'4',
                            'specimen_stool_id_ali_2':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
        
        elif barcode_id[-3:]=='ST4':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'stool_collected_endo_cd_v2':'1',
                            'specimen_stool_num_al':'4',
                            'specimen_stool_id_ali_3':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-3:]=='SR1':
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_100':'3',
                            'specimen_serum_al_1_100_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
        
        elif barcode_id[-3:]=='SR2': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_100':'3',
                            'specimen_serum_al_2_100_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 
            
        elif barcode_id[-3:]=='SR3': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_100':'3',
                            'specimen_serum_al_3_100':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')

        elif barcode_id[-3:]=='SR4': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_250':'1',
                            'specimen_serum_al_250_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-3:]=='SR5': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_250_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-3:]=='SR6': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_2':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-3:]=='SR7': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_3':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-3:]=='SR8': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_4':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-3:]=='SR9': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_5':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-4:]=='SR10': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_6':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-4:]=='SR11': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'serum_collected_endo_cd_v2':'1',
                            'specimen_serum_al_500':'7',
                            'specimen_serum_al_500_7':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-3:]=='DNA': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_1',
                            'dna_collected_endo_cd_v2':'1',
                            'specimen_dna_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')

        elif barcode_id[-7:]=='FreshTI': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'ctl_endo_ti_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-7:]=='FixedTI': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'ctl_endo_ti_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-8:]=='FrozenTI': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'ctl_endo_ti_frozen_id':barcode_id,
                          'ctl_endo_biopsy_id_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')           

        elif barcode_id[-7:]=='FreshAC': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_1',
                            'ctl_endo_ac_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-7:]=='FixedAC': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'ctl_endo_ac_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-8:]=='FrozenAC': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_1',
                          'ctl_endo_ac_frozen_id':barcode_id,
                          'ctl_endo_biopsy_id_2':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
       
        return True                

    def update_CD_Surgery_SOPHIE_SINGLE_BARCODE(self,subject_id,barcode_id):  
        if barcode_id[-7:]=='FreshTI':
            print('NIMANIMANIMA')
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_2',
                            'cd_surgery_ti_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-7:]=='FixedTI': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_2',
                          'cd_surgery_ti_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-8:]=='FrozenTI': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_2',
                          'cd_surgery_ti_frozen_id':barcode_id,
                          'cd_surg_biopsy_id_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')           

        elif barcode_id[-7:]=='FreshAC': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'cd_arm_2',
                            'cd_surgery_ac_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-7:]=='FixedAC': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_2',
                          'cd_surgery_ac_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        elif barcode_id[-8:]=='FrozenAC': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'cd_arm_2',
                          'cd_surgery_ac_frozen_id':barcode_id,
                          'cd_surg_biopsy_id_2':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')

        return True
    
    def update_CTL_Surgery_SOPHIE_SINGLE_BARCODE(self,subject_id,barcode_id):  

        if barcode_id[-8:]=='FreshTI1': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_2',
                            'ctl_surgery_ti_1_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTI1': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ti_1_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 

        elif barcode_id[-9:]=='FrozenTI1': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ti_1_frozen_id':barcode_id,
                          'ctl_surg_biopsy_id_1':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FreshTI2': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_2',
                            'ctl_surgery_ti_2_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTI2': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ti_2_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 

        elif barcode_id[-9:]=='FrozenTI2': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ti_2_frozen_id':barcode_id,
                          'ctl_surg_biopsy_id_2':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FreshTI3': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_2',
                            'ctl_surgery_ti_3_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTI3': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ti_3_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 

        elif barcode_id[-9:]=='FrozenTI3': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ti_3_frozen_id':barcode_id,
                          'ctl_surg_biopsy_id_3':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FreshTI4': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_2',
                            'ctl_surgery_ac_4_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTI4': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_4_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 

        elif barcode_id[-9:]=='FrozenTI4': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_4_frozen_id':barcode_id,
                          'ctl_surg_biopsy_id_4':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')

        elif barcode_id[-8:]=='FreshTI5': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_2',
                            'ctl_surgery_ac_5_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTI5': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_5_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 

        elif barcode_id[-9:]=='FrozenTI5': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_5_frozen_id':barcode_id,
                          'ctl_surg_biopsy_id_5':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            
            
        elif barcode_id[-8:]=='FreshTI6': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_2',
                            'ctl_surgery_ac_6_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTI6': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_6_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 

        elif barcode_id[-9:]=='FrozenTI6': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_6_frozen_id':barcode_id,
                          'ctl_surg_biopsy_id_6':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')             

        elif barcode_id[-8:]=='FreshTI7': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_2',
                            'ctl_surgery_ac_7_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTI7': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_7_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 

        elif barcode_id[-9:]=='FrozenTI7': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_7_frozen_id':barcode_id,
                          'ctl_surg_biopsy_id_7':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FreshTI8': 
            to_import = [{'record_id_dem_endo':subject_id,
                            'redcap_event_name':'control_arm_2',
                            'ctl_surgery_ac_8_fresh_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')
            
        elif barcode_id[-8:]=='FixedTI8': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_8_fixed_id':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite') 

        elif barcode_id[-9:]=='FrozenTI8': 
            to_import = [{'record_id_dem_endo':subject_id,
                          'redcap_event_name':'control_arm_2',
                          'ctl_surgery_ac_8_frozen_id':barcode_id,
                          'ctl_surg_biopsy_id_8':barcode_id}]
            response = self.project.import_records(to_import,overwrite='overwrite')            

        return True
    
    def update_CD_END_SOPHIE_extra_frozen_SINGLE_BARCODE(self,subject_id,barcode_id):
        if 'ADD' in barcode_id:
            if barcode_id[-12:]=='ADDFrozenTIA': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'second_frozen': '1',
                              'ti_add_frozen_a_id':barcode_id,
                              'cd_endo_add_ti_a_id':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
            elif barcode_id[-12:]=='ADDFrozenTIB': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'second_frozen': '1',
                              'ti_add_frozen_b_id':barcode_id,
                              'cd_endo_add_ti_b_id':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
            elif barcode_id[-12:]=='ADDFrozenACA': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'second_frozen': '1',
                              'ac_add_frozen_a_id':barcode_id,
                              'cd_endo_add_ac_a_id':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')                
 
            elif barcode_id[-12:]=='ADDFrozenACB': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'second_frozen': '1',
                              'ac_add_frozen_b_id':barcode_id,
                              'cd_endo_add_ac_b_id':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite') 
        else:
            self.update_CD_END_SOPHIE_SINGLE_BARCODE(subject_id,barcode_id)
        
        return True  


    def update_CTL_END_SOPHIE_extra_frozen_SINGLE_BARCODE(self,subject_id,barcode_id):
        if 'ADD' in barcode_id:
            if barcode_id[-11:]=='ADDFrozenTI': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_second_frozen': '1',
                              'ctl_endo_add_ti_id':barcode_id,
                              'ctl_endo_biopsy_id_3':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
            elif barcode_id[-11:]=='ADDFrozenAC': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_second_frozen': '1',
                              'ctl_endo_add_ac_id':barcode_id,
                              'ctl_endo_biopsy_id_4':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
        else:
            self.update_CTL_END_SOPHIE_extra_frozen_SINGLE_BARCODE(subject_id,barcode_id)
        
        return True

    def update_CD_Surgery_SOPHIE_extra_frozen_SINGLE_BARCODE(self,subject_id,barcode_id):
        if 'ADD' in barcode_id:
            if barcode_id[-11:]=='ADDFrozenTI': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_sur_add_biopsies': '1',
                              'cd_sur_ti_add_id':barcode_id,
                              'cd_surg_biopsy_id_3':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
            elif barcode_id[-11:]=='ADDFrozenAC': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_sur_add_biopsies': '1',
                              'cd_sur_ac_add_id':barcode_id,
                              'cd_surg_biopsy_id_4':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
        else:
            self.update_CD_Surgery_SOPHIE_SINGLE_BARCODE(subject_id,barcode_id)
        
        return True
    
           
    def update_CTL_Surgery_SOPHIE_SINGLE_BARCODE(self,subject_id,barcode_id):
        if 'ADD' in barcode_id:
            if barcode_id[-12:]=='ADDFrozenTI1': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_add_collec': '1',
                              'ctl_sur_ti_1_add_id':barcode_id,
                              'ctl_surg_biopsy_1_id_add':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
            elif barcode_id[-12:]=='ADDFrozenTI2': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_add_collec': '1',
                              'ctl_sur_ti_2_add_id':barcode_id,
                              'ctl_sur_add_bio_id_2':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
            elif barcode_id[-12:]=='ADDFrozenTI3': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_add_collec': '1',
                              'ctl_sur_ti_3_add_id':barcode_id,
                              'ctl_sur_add_bio_id_3':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
            elif barcode_id[-12:]=='ADDFrozenAC4': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_add_collec': '1',
                              'ctl_sur_ac_4_add_id':barcode_id,
                              'ctl_sur_ac_add_bio_id_4':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
            elif barcode_id[-12:]=='ADDFrozenAC5': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_add_collec': '1',
                              'ctl_sur_ac_5_add_id':barcode_id,
                              'ctl_sur_add_bio_id_5':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
 
            elif barcode_id[-12:]=='ADDFrozenAC6': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_add_collec': '1',
                              'ctl_sur_ac_6_add_id':barcode_id,
                              'ctl_sur_add_bio_id_6':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
            elif barcode_id[-12:]=='ADDFrozenAC7': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_add_collec': '1',
                              'ctl_sur_ac_7_add_id':barcode_id,
                              'ctl_sur_add_bio_id_7':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
                
            elif barcode_id[-12:]=='ADDFrozenAC8': 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_add_collec': '1',
                              'ctl_sur_ac_8_add_id':barcode_id,
                              'ctl_sur_add_bio_id_8':barcode_id}]
                response = self.project.import_records(to_import,overwrite='overwrite')
        else:
            self.update_CTL_Surgery_SOPHIE_SINGLE_BARCODE(subject_id,barcode_id)
        
        return True       
            
                

########### def setMailedAction(self, actionId, barcode_id, studyType,processed_by,action_comment,ean8_code):
# #         if action_comment == '':
# #             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
# #                           'redcap_event_name': 'action_tuple_table_arm_3',
# #                           'barcode_sample_id': barcode_id,
# #                           'barcode_subject_type':studyType,
# #                           'barcode_processed_by': processed_by,
# #                           'barcode_action_date' : self.getCurrentTime(),
# #                           'barcode_action_type' : 'barcode mailed'}]
# #         else:
#         # action_comment cannot be empty...
#         aliquot_id = ''
#         if 'SR' in barcode_id: 
#             aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8
            
#             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
#                           'redcap_event_name': 'action_tuple_table_arm_3',
#                           'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_aliquot_id' : aliquot_id,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_action_type' : 'mailed',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]
            
#         else:
#             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
#                           'redcap_event_name': 'action_tuple_table_arm_3',
#                           'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_action_type' : 'mailed',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]            
            
#         response = self.project.import_records(to_import)
#         return True

#     def setSentAction(self, actionId, barcode_id, studyType,processed_by,action_comment,ean8_code):
# #         if action_comment == '':
# #             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
# #                           'redcap_event_name': 'action_tuple_table_arm_3',
# #                           'barcode_sample_id': barcode_id,
# #                           'barcode_subject_type':studyType,
# #                           'barcode_processed_by': processed_by,
# #                           'barcode_action_date' : self.getCurrentTime(),
# #                           'barcode_action_type' : 'barcode mailed'}]
# #         else:
#         # action_comment cannot be empty...
#         aliquot_id = ''
#         if 'SR' in barcode_id: 
#             aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8
            
#             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
#                           'redcap_event_name': 'action_tuple_table_arm_3',
#                           'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_aliquot_id' : aliquot_id,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_action_type' : 'sent',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]
#         else:
#             to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
#                           'redcap_event_name': 'action_tuple_table_arm_3',
#                           'barcode_sample_id': barcode_id,
#                           'barcode_subject_type':studyType,
#                           'barcode_processed_by': processed_by,
#                           'barcode_action_date' : self.getCurrentTime(),
#                           'barcode_action_type' : 'sent',
#                           'barcode_comment_note': action_comment,
#                           'barcode_ean8_code': ean8_code}]            
#         response = self.project.import_records(to_import)
#         return True
