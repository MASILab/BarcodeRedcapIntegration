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
        self._tmp_subset = None # for caching one query...
        
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

    def getInputPatient(self):
        """
        Get all patient entries from Sophie's redcap desgin
        """
        
        return self.getRecordFromRedcap(['cd_arm_1','control_arm_1','cd_arm_2','control_arm_2'],['record_id_dem_endo'])
    
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
    
    
    def getBarcodeSubset_StudyType_Action_CustomOption(self):
        """
        Get all records in action_tuple_table_arm_3's barcode sample id field
        """
#        subset = self.project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id'])
#        return self.getRecordFromRedcap(['action_tuple_table_arm_3'],['barcode_sample_id','barcode_custom_option'])
        # add barcode action type to find duplicate
        self._tmp_subset = self.getRecordFromRedcap(['action_tuple_table_arm_3'],['barcode_sample_id','barcode_custom_option','barcode_action_type','barcode_subject_type'])
#         return self._tmp_subset    
    
    def getSubjectLastestActionAndCustomOption(self, barcode_id,subject_id):
        """
        fyi, (1) check if barcode exist,
        (2) if barcode exist, get subject type, action type, custom option
        (3) since the option may change from "Default" to "Need Extra Frozen"
        (4) Skip scanned, otherwise the lateset could always be the 'scanned'...
        """    
#       tmp_subset = self.getBarcodeSubset_StudyType_Action_CustomOption()
#        self.getBarcodeSubset_StudyType_Action_CustomOption()
#        print(tmp_subset)
        if self._tmp_subset is None:
#            print('???')
            return False, False, False
        
        if len(self._tmp_subset) == 0:
#            print('!!!')
            return False, False, False
        
        data = pd.DataFrame.from_dict(self._tmp_subset)
        df = data.loc[data['barcode_sample_id'] == barcode_id]
        if len(df) == 0:
#            print('...')
            return False, False, False
        else:
            # result in 'action_tuple_table_arm_3','barcode_sample_id','barcode_custom_option'
            idx = len(self._tmp_subset)-1
            tmp_subject_type = ''
            tmp_action_type = ''
            tmp_custom_option = ''
            
            
#            print(tmp_subset)
            while idx >= 0:
 #               print('redcap22222 %s' % str(tmp_subset[idx].get('barcode_sample_id')))
                tmp_subj = self._tmp_subset[idx].get('barcode_sample_id')[3:6]
                tmp_barcode = self._tmp_subset[idx].get('barcode_sample_id')
                if tmp_subj == subject_id and tmp_barcode == barcode_id:
                    
                    tmp_subject_type = self._tmp_subset[idx].get('barcode_subject_type')
                    tmp_action_type = self._tmp_subset[idx].get('barcode_action_type')
                    tmp_custom_option = self._tmp_subset[idx].get('barcode_custom_option')
                    
                    
 #                   print('redcap %s' % str(tmp_subset[idx].get('barcode_sample_id')))
 #                   print('redcap %s' % tmp_action_type)
                    if tmp_action_type != 'scanned':
                        break # scanned is a necessary operation, and we don't know what exact operation has been done before or after scanned. 
                idx -= 1
            
            return tmp_subject_type,tmp_action_type, tmp_custom_option
     
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
         
        return custom_option
    
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
         
        return custom_option
            

    
    def getNextAvailActionId(self):
        """
        fyi, get next available action id.
        """
        subset = self.getBarcodeSubset()
        nextAvailActionId = len(subset) + 1
        return nextAvailActionId
    
    def getCurrentTime(self):
        """
        fyi, get current time
        """
        curTime = datetime.now()
        cur_date = curTime.strftime('%Y-%m-%d %H:%M')
        return str(cur_date)
    
    def destroyBarcode(self,actionId,barcode_id,studyType,processed_by,action_type, action_comment,ean8_code,custom_option):
        """
        action_type: 'Barcode destoryed'
        """
        # the only different is action_type...
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
    
    def destroyBarcodeCustomDate(self,actionId,barcode_id,studyType,processed_by,action_type, action_comment,ean8_code,custom_option,custom_date):
        """
        >> Add custom date for adding missing record in arm3
        action_type: 'Barcode destoryed'
        """
        # the only different is action_type...
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
                          'barcode_action_date' : custom_date,
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
                          'barcode_action_date' : custom_date,
                          'barcode_action_type' : action_type,
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        response = self.project.import_records(to_import)
        return True
 

    def execLocationAppSync(self, actionId, barcode_id, studyType,processed_by,action_type,locationTuple,action_comment,ean8_code,custom_option):
        """
        action_type: 'Serum stored in rack',
                     'Stool stored in rack', 
                     'Frozen stored in rack', 
                     'Fresh distributed to Lau',
                     'DNA distributed to Vantage. Relevant DNA field will be filled manually.',
                     'Fixed distributed to TPSR. Relevant Fixed specimen field will be filled manually.'
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
                          'barcode_freezer' : locationTuple[1], 
                          'barcode_rack' : locationTuple[2],
                          'barcode_box_id' : locationTuple[3],
                          'barcode_box_position' : locationTuple[4],
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
                          'barcode_freezer' : locationTuple[1], 
                          'barcode_rack' : locationTuple[2],
                          'barcode_box_id' : locationTuple[3],
                          'barcode_box_position' : locationTuple[4],
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        response = self.project.import_records(to_import)
        return True
    
    def execLocationAppSyncCustomDate(self, actionId, barcode_id, studyType,processed_by,action_type,locationTuple,action_comment,ean8_code,custom_option,custom_date):
        """
        >> Add custom date for adding missing record in arm3
        action_type: 'Serum stored in rack',
                     'Stool stored in rack', 
                     'Frozen stored in rack', 
                     'Fresh distributed to Lau',
                     'DNA distributed to Vantage. Relevant DNA field will be filled manually.',
                     'Fixed distributed to TPSR. Relevant Fixed specimen field will be filled manually.'
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
                          'barcode_action_date' : custom_date,
                          'barcode_action_type' : action_type,
                          'barcode_freezer' : locationTuple[1], 
                          'barcode_rack' : locationTuple[2],
                          'barcode_box_id' : locationTuple[3],
                          'barcode_box_position' : locationTuple[4],
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}]
        else:
            to_import = [{'record_id_dem_endo': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : custom_date,
                          'barcode_action_type' : action_type,
                          'barcode_freezer' : locationTuple[1], 
                          'barcode_rack' : locationTuple[2],
                          'barcode_box_id' : locationTuple[3],
                          'barcode_box_position' : locationTuple[4],
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
    
################# UPDATE SOPHIE's REDCAP
    def destroy_REDCAP_SOPHIE_FROM_LOCATION_APP(self,subject_id,barcode_id, study_type):
        print(subject_id)
        print(barcode_id)
        print(study_type)
        if study_type == 'CD_ENDO':
                self.destroy_CD_END_SOPHIE(subject_id,barcode_id)
        elif study_type == 'CTL_ENDO':
                self.destroy_CTL_END_SOPHIE(subject_id,barcode_id)
        elif study_type == 'CD_Surgery':
                self.destroy_CD_Surgery_SOPHIE(subject_id,barcode_id)
        elif study_type == 'CTL_Surgery':
                self.destroy_CTL_Surgery_SOPHIE(subject_id,barcode_id) 
                
    def destroy_CD_END_SOPHIE(self,subject_id,barcode_id): 
        to_import = []
        if 'SR' in barcode_id:
            if 'SR1' in barcode_id:
                if 'SR10' in barcode_id:
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'cd_arm_1',
                                  'specimen_serum_al_500_6':'',                                  
                                  'specimen_serum_500_6_freezer_3':'',
                                  'specimen_serum_500_6_rack_loc_3':'',
                                  'specimen_serum_500_6_box_4':'',
                                  'specimen_serum_500_6_box_pos_3':''}]
                elif 'SR11' in barcode_id:
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'cd_arm_1',
                                  'specimen_serum_al_500_7':'',
                                  'specimen_serum_500_7_freezer_4':'',
                                  'specimen_serum_500_7_rack_loc_4':'',
                                  'specimen_serum_500_7_box_5':'',
                                  'specimen_serum_500_7_box_pos_4':''}]
                else: # should be SR1
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'cd_arm_1',
                                  'specimen_serum_al_1_100_id':'',              
                                  'specimen_serum_100_1_freezer':'',
                                  'specimen_serum_100_1_rack_loc':'',
                                  'specimen_serum_100_1_box_2':'',
                                  'specimen_serum1_box_pos':''}]
            elif 'SR2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                               'redcap_event_name':'cd_arm_1',
                               'specimen_serum_al_2_100_id':'',                     
                                'specimen_serum_100_2_freezer':'',
                                'specimen_serum_100_2_rack_loc':'',
                                'specimen_serum_100_1_box':'',
                                'specimen_serum_100_1_box_pos':''}]
            elif 'SR3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_serum_al_3_100':'',              
                              'specimen_serum_100_3_freezer_2':'',
                              'specimen_serum_100_3_rack_loc_2':'',
                              'specimen_serum_100_3_box':'',
                              'specimen_serum_100_1_box_pos_3':''}]
            elif 'SR4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_serum_al_250_1':'',              
                              'specimen_serum_250_freezer':'',
                              'specimen_serum_250_rack_loc':'',
                              'specimen_serum_250_box':'',
                              'specimen_serum_250_box_pos':''}]
            elif 'SR5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_serum_al_500_1':'',              
                              'specimen_serum_500_1_freezer':'',
                              'specimen_serum_500_1_rack_loc':'',
                              'specimen_serum_500_1_box':'',
                              'specimen_serum_500_1_box_pos':''}]
            elif 'SR6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_serum_al_500_2':'',              
                              'specimen_serum_500_2_freezer':'',
                              'specimen_serum_500_2_rack_loc':'',
                              'specimen_serum_500_2_box':'',
                              'specimen_serum_500_2_box_pos':''}]
            elif 'SR7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_serum_al_500_3':'',              
                              'specimen_serum_500_3_freezer':'',
                              'specimen_serum_500_3_rack_loc':'',
                              'specimen_serum_500_3_box':'',
                              'specimen_serum_500_3_box_pos':''}]
            elif 'SR8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_serum_al_500_4':'',              
                              'specimen_serum_500_4_freezer':'',
                              'specimen_serum_500_4_rack_loc':'',
                              'specimen_serum_500_3_box_2':'',
                              'specimen_serum_500_4_box_pos':''}]
            elif 'SR9' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_serum_al_500_5':'',              
                              'specimen_serum_500_5_freezer_2':'',
                              'specimen_serum_500_5_rack_loc_2':'',
                              'specimen_serum_500_5_box_3':'',
                              'specimen_serum_500_5_box_pos_2':''}]

                
        elif 'ST' in barcode_id:
            if 'ST1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_stool_id_ali':'',
                              'specimen_stool1_freezer':'',
                              'specimen_stool1_rack':'',
                              'specimen_stool1_box':'',
                              'specimen_stool1_box_pos':''}]
            elif 'ST2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_stool_id_ali_1':'',
                              'specimen_stool2_freezer':'',
                              'specimen_stool2_rack':'',
                              'specimen_stool2_box':'',
                              'specimen_stool2_box_pos':''}]                
            elif 'ST3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_stool_id_ali_2':'',
                              'specimen_stool3_freezer':'',
                              'specimen_stool3_rack':'',
                              'specimen_stool3_box':'',
                              'specimen_stool3_box_pos':''}]                
            elif 'ST4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_stool_id_ali_3':'',
                              'specimen_stool4_freezer':'',
                              'specimen_stool4_rack':'',
                              'specimen_stool4_box':'',
                              'specimen_stool4_box_pos':''}]                

        elif 'Frozen' in barcode_id:
            if 'ADDFrozenTIA' in barcode_id:
                print('......')
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'ti_add_frozen_a_id':'',
                              'cd_endo_add_ti_a_id':'',
                              'cd_endo_add_ti_a_freezer':'',
                              'cd_endo_add_ti_a_rack':'',
                              'cd_endo_add_ti_a_box':'',
                              'cd_endo_add_ti_a_box_position':'',
                              'ti_involved_a_v2___4':'0'}] 
            elif 'ADDFrozenTIB' in barcode_id:
                print('......')
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',   
                              'ti_add_frozen_b_id':'',           
                              'cd_endo_add_ti_b_id':'',
                              'cd_endo_add_ti_b_freezer':'',
                              'cd_endo_add_ti_b_rack':'',
                              'cd_endo_add_ti_b_box':'',
                              'cd_endo_add_ti_b_box_position':'',
                              'ti_non_involved_b_v2___4':'0'}] 
            elif 'ADDFrozenACA' in barcode_id:
                print('......')
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',  
                              'ac_add_frozen_a_id':'',           
                              'cd_endo_add_ac_a_id':'', 
                              'cd_endo_add_ac_a_freezer':'',
                              'cd_endo_add_ac_a_rack':'',
                              'cd_endo_add_ac_a_box':'',
                              'cd_endo_add_ac_a_box_position':'',
                              'ac_involved___4':'0'}] 
            elif 'ADDFrozenACB' in barcode_id:
                print('......')
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'ac_add_frozen_b_id':'',
                              'cd_endo_add_ac_b_id':'',              
                              'cd_endo_add_ac_b_freezer':'',
                              'cd_endo_add_ac_b_rack':'',
                              'cd_endo_add_ac_b_box':'',
                              'cd_endo_add_ac_b_box_position':'',
                              'ac_non_involved___4':'0'}] 
            elif 'FrozenTIA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'cd_endo_ti_a_frozen_id':'',
                              'cd_endo_biopsy_id':'',              
                              'cd_endo_biopsies_freezer':'',
                              'cd_endo_biopsy_rack_location':'',
                              'cd_endo_biopsy_box_2':'',
                              'cd_endo_biopsy_box_position_2':'',
                              'ti_involved_a_v2___3':'0'}] 
            elif 'FrozenTIB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',   
                              'cd_endo_ti_b_frozen_id':'',        
                              'cd_endo_biopsy_id2':'',   
                              'cd_endo_biopsies_freezer_2':'',
                              'cd_endo_biopsy_rack_location_2':'',
                              'cd_endo_biopsy_box_3':'',
                              'cd_endo_biopsy_box_position':'',
                              'ti_non_involved_b_v2___3':'0'}] 
            elif 'FrozenACA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1', 
                              'cd_endo_ac_a_frozen_id':'',
                              'cd_endo_biopsy_id3':'',             
                              'cd_endo_biopsies_freezer_4':'',
                              'cd_endo_biopsy_rack_location_4':'',
                              'cd_endo_biopsy_box':'',
                              'cd_endo_biopsy_box_position_3':'',
                              'ac_involved___3':'0'}] 
            elif 'FrozenACB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'cd_endo_ac_b_frozen_id':'',
                              'cd_endo_biopsy_id4':'',
                              'cd_endo_biopsies_freezer_3':'',
                              'cd_endo_biopsy_rack_location_3':'',
                              'cd_endo_biopsy_box_4':'',
                              'cd_endo_biopsy_box_position_4':'',
                              'ac_non_involved___3':'0'}] 
                
        elif 'Fresh' in barcode_id:
            
            if 'FreshTIA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'cd_endo_ti_a_fresh_id':'',
                              'ti_involved_a_v2___1':'0'}]
            elif 'FreshTIB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'cd_endo_ti_b_fresh_id':'',
                              'ti_non_involved_b_v2___1':'0'}]
            elif 'FreshACA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',  
                              'cd_endo_ac_a_fresh_id':'',            
                              'ac_involved___1':'0'}]
            elif 'FreshACB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1', 
                              'cd_endo_ac_b_fresh_id':'',             
                              'ac_non_involved___1':'0'}]
        elif 'Fixed' in barcode_id:
            if 'FixedTIA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'sc_endo_ti_a_fixed_id':'',
                              'ti_involved_a_v2___2':'0'}]
            elif 'FixedTIB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'cd_endo_ti_b_fixed_id':'',
                              'ti_non_involved_b_v2___2':'0'}]
            elif 'FixedACA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1', 
                              'cd_endo_ac_a_fixed_id':'',             
                              'ac_involved___2':'0'}]
            elif 'FixedACB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'cd_endo_ac_b_fixed_id':'',              
                              'ac_non_involved___2':'0'}]
                              
        elif 'DNA' in barcode_id:
            to_import = [{'record_id_dem_endo':subject_id,
                           'redcap_event_name':'cd_arm_1',
                           'specimen_dna_id':''}]
        
            # doNothing()
        
        response = self.project.import_records(to_import,overwrite='overwrite')
        return True 
    
           
    def destroy_CTL_END_SOPHIE(self,subject_id,barcode_id):
        to_import = []
        if 'SR' in barcode_id:
            if 'SR1' in barcode_id:
                if 'SR10' in barcode_id:
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'control_arm_1',
                                  'specimen_serum_al_500_6':'',
                                  'specimen_serum_500_6_freezer_3':'',
                                  'specimen_serum_500_6_rack_loc_3':'',
                                  'specimen_serum_500_6_box_4':'',
                                  'specimen_serum_500_6_box_pos_3':''}]
                elif 'SR11' in barcode_id:
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'control_arm_1',
                                  'specimen_serum_al_500_7':'',
                                  'specimen_serum_500_7_freezer_4':'',
                                  'specimen_serum_500_7_rack_loc_4':'',
                                  'specimen_serum_500_7_box_5':'',
                                  'specimen_serum_500_7_box_pos_4':''}]
                else: # should be SR1
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'control_arm_1',
                                  'specimen_serum_al_1_100_id':'',              
                                  'specimen_serum_100_1_freezer':'',
                                  'specimen_serum_100_1_rack_loc':'',
                                  'specimen_serum_100_1_box_2':'',
                                  'specimen_serum1_box_pos':''}]
            elif 'SR2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                               'redcap_event_name':'control_arm_1',
                               'specimen_serum_al_2_100_id':'',                     
                                'specimen_serum_100_2_freezer':'',
                                'specimen_serum_100_2_rack_loc':'',
                                'specimen_serum_100_1_box':'',
                                'specimen_serum_100_1_box_pos':''}]
            elif 'SR3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_serum_al_3_100':'',             
                              'specimen_serum_100_3_freezer_2':'',
                              'specimen_serum_100_3_rack_loc_2':'',
                              'specimen_serum_100_3_box':'',
                              'specimen_serum_100_1_box_pos_3':''}]
            elif 'SR4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1', 
                              'specimen_serum_al_250_1':'',             
                              'specimen_serum_250_freezer':'',
                              'specimen_serum_250_rack_loc':'',
                              'specimen_serum_250_box':'',
                              'specimen_serum_250_box_pos':''}]
            elif 'SR5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_serum_al_500_1':'',              
                              'specimen_serum_500_1_freezer':'',
                              'specimen_serum_500_1_rack_loc':'',
                              'specimen_serum_500_1_box':'',
                              'specimen_serum_500_1_box_pos':''}]
            elif 'SR6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_serum_al_500_2':'',              
                              'specimen_serum_500_2_freezer':'',
                              'specimen_serum_500_2_rack_loc':'',
                              'specimen_serum_500_2_box':'',
                              'specimen_serum_500_2_box_pos':''}]
            elif 'SR7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_serum_al_500_3':'',              
                              'specimen_serum_500_3_freezer':'',
                              'specimen_serum_500_3_rack_loc':'',
                              'specimen_serum_500_3_box':'',
                              'specimen_serum_500_3_box_pos':''}]
            elif 'SR8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_serum_al_500_4':'',              
                              'specimen_serum_500_4_freezer':'',
                              'specimen_serum_500_4_rack_loc':'',
                              'specimen_serum_500_3_box_2':'',
                              'specimen_serum_500_4_box_pos':''}]
            elif 'SR9' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_serum_al_500_5':'',              
                              'specimen_serum_500_5_freezer_2':'',
                              'specimen_serum_500_5_rack_loc_2':'',
                              'specimen_serum_500_5_box_3':'',
                              'specimen_serum_500_5_box_pos_2':''}]

                
        elif 'ST' in barcode_id:
            if 'ST1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_stool_id_ali':'',
                              'specimen_stool1_freezer':'',
                              'specimen_stool1_rack':'',
                              'specimen_stool1_box':'',
                              'specimen_stool1_box_pos':''}]
            elif 'ST2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_stool_id_ali_1':'',
                              'specimen_stool2_freezer':'',
                              'specimen_stool2_rack':'',
                              'specimen_stool2_box':'',
                              'specimen_stool2_box_pos':''}]                
            elif 'ST3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_stool_id_ali_2':'',
                              'specimen_stool3_freezer':'',
                              'specimen_stool3_rack':'',
                              'specimen_stool3_box':'',
                              'specimen_stool3_box_pos':''}]                
            elif 'ST4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_stool_id_ali_3':'',
                              'specimen_stool4_freezer':'',
                              'specimen_stool4_rack':'',
                              'specimen_stool4_box':'',
                              'specimen_stool4_box_pos':''}] 

        elif 'Frozen' in barcode_id:
            ###### NOTE: NO check box for add frozen
            if 'ADDFrozenTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_add_ti_id':'',
                              'ctl_endo_biopsy_id_3':'',
                              'ctl_endo_freezer_ti_add':'',
                              'ctl_endo_rack_ti_add':'',
                              'ctl_endo_box_ti_add':'',
                              'ctl_endo_box_pos_ti_add':'',
                              'specimen_bio_ctl_ti___4':'0'}]
            elif 'ADDFrozenAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_add_ac_id':'',
                              'ctl_endo_biopsy_id_4':'',
                              'ctl_endo_freezer_ac_add':'',
                              'ctl_endo_rack_ac_add':'',
                              'ctl_endo_box_ac_add':'',
                              'ctl_endo_box_pos_ac_add':'',
                              'specimen_bio_ctl_ac___4':'0'}]
            elif 'FrozenTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_ti_frozen_id':'',
                              'ctl_endo_biopsy_id_1':'',
                              'ctl_endo_freezer_ti_biopsy':'',
                              'ctl_endo_rack_ti_biopsy':'',
                              'ctl_endo_box_ti_biopsy':'',
                              'ctl_endo_box_pos_ti_biopsy':'',
                              'specimen_bio_ctl_ti___3':'0'}]
            elif 'FrozenAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_ac_frozen_id':'',
                              'ctl_endo_biopsy_id_2':'',
                              'ctl_endo_freezer_ac_biopsy':'',
                              'ctl_endo_rack_ac_biopsy':'',
                              'ctl_endo_box_ac_biopsy':'',
                              'ctl_endo_box_pos_ac_biopsy':'',
                              'specimen_bio_ctl_ac___3':'0'}]
                
        elif 'Fresh' in barcode_id:
            
            if 'FreshTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_ti_fresh_id':'',
                              'specimen_bio_ctl_ti___1':'0'}]
            elif 'FreshAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_ac_fresh_id':'',
                              'specimen_bio_ctl_ac___1':'0'}]
        elif 'Fixed' in barcode_id:
            if 'FixedTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_ti_fixed_id':'',
                              'specimen_bio_ctl_ti___2':'0'}]
            elif 'FixedAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1', 
                              'ctl_endo_ac_fixed_id':'',             
                              'specimen_bio_ctl_ac___2':'0'}]
           
        elif 'DNA' in barcode_id:
            to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_dna_id':''}] 
            # doNothing()
        
        response = self.project.import_records(to_import,overwrite='overwrite')
        return True
    
    def destroy_CD_Surgery_SOPHIE(self,subject_id,barcode_id): 
        to_import = []
        
        if 'Frozen' in barcode_id:
            if 'ADDFrozenTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_sur_ti_add_id':'',
                              'cd_surg_biopsy_id_3':'',
                              'cd_surgery_freezer_ti_add':'',
                              'cd_surgery_rack_loc_ti_add':'',
                              'cd_surgery_box_ti_add':'',
                              'cd_surgery_box_pos_ti_add':'',
                              'cd_sur_bio_ti___4':'0'}]
            elif 'ADDFrozenAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_sur_ac_add_id':'',
                              'cd_surg_biopsy_id_4':'',
                              'cd_surgery_freezer_ac_add':'',
                              'cd_surgery_rack_loc_ti_add_2':'',
                              'cd_surgery_box_ac_add':'',
                              'cd_surgery_box_pos_ac_add':'',
                              'cd_sur_bio_ac___4':'0'}]                             
            elif 'FrozenTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_ti_frozen_id':'',
                              'cd_surg_biopsy_id_1':'',
                              'cd_surgery_freezer_ti_biopsy':'',
                              'cd_surgery_rack_loc_ti_biopsy':'',
                              'cd_surgery_box_ti_biopsy':'',
                              'cd_surgery_box_pos_ti_biopsy':'',
                              'cd_sur_bio_ti___3':'0'}]        
            elif 'FrozenAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_ac_frozen_id':'',
                              'cd_surg_biopsy_id_2':'',
                              'cd_surgery_freezer_ac_biopsy':'',
                              'cd_surgery_rack_loc_ac_biopsy':'',
                              'cd_surgery_box_ac_biopsy':'',
                              'cd_surgery_box_pos_ac_biopsy':'',
                              'cd_sur_bio_ac___3':'0'}]
                
        elif 'Fresh' in barcode_id:
                          
            if 'FreshTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2', 
                              'cd_surgery_ti_fresh_id':'',
                              'cd_sur_bio_ti___1':'0'}]
            elif 'FreshAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_ac_fresh_id':'',
                              'cd_sur_bio_ac___1':'0'}]

        elif 'Fixed' in barcode_id:
            if 'FixedTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_ti_fixed_id':'',
                              'cd_sur_bio_ti___2':'0'}]
            elif 'FixedAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_ac_fixed_id':'',              
                              'cd_sur_bio_ac___2':'0'}]                              
        
       # No DNA elif 'DNA' in barcode_id:
            # doNothing()
        
        response = self.project.import_records(to_import,overwrite='overwrite')
        return True
                              
                              
    def destroy_CTL_Surgery_SOPHIE(self,subject_id,barcode_id):
        to_import = []

        if 'Frozen' in barcode_id:
            if 'ADDFrozenTI1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_ti_1_add_id':'',
                              'ctl_surg_biopsy_1_id_add':'',
                              'ctl_surgery_ti_1_freezer_add':'',
                              'ctl_surgery_ti_1_rack_loc_add':'',
                              'ctl_surgery_ti_1_box_add':'',
                              'ctl_surgery_ti_1_box_pos_add':'',
                              'ctl_sur_bio_ti_1___4':'0'}]
            elif 'ADDFrozenTI2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_ti_2_add_id':'',
                              'ctl_sur_add_bio_id_2':'',
                              'ctl_surgery_ti_2_freezer_add':'',
                              'ctl_surgery_ti_2_rack_loc_add':'',
                              'ctl_surgery_ti_2_box_add':'',
                              'ctl_surgery_ti_2_box_pos_add':'',
                              'ctl_sur_bio_ti_2___4':'0'}]
            elif 'ADDFrozenTI3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_ti_3_add_id':'',
                              'ctl_sur_add_bio_id_3':'',
                              'ctl_surgery_ti_3_freezer_add':'',
                              'ctl_surgery_ti_3_rack_loc_add':'',
                              'cdl_surgery_ti_3_box_add':'',
                              'ctl_surgery_ti_3_box_pos_add':'',
                              'ctl_sur_bio_ti_3___4':'0'}]                              
            elif 'ADDFrozenAC4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_ac_4_add_id':'',
                              'ctl_sur_ac_add_bio_id_4':'',
                              'ctl_surgery_ac_4_freezer_add':'',
                              'ctl_surgery_ac_4_rack_loc_add':'',
                              'cdl_surgery_ac_4_box_add':'',
                              'ctl_surgery_ac_4_box_pos_add':'',
                              'ctl_sur_bio_ac_5___4':'0'}]
            elif 'ADDFrozenAC5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_ac_5_add_id':'',
                              'ctl_sur_add_bio_id_5':'',
                              'ctl_surgery_ac_5_freezer_add':'',
                              'ctl_surgery_ac_5_rack_loc_add':'',
                              'cdl_surgery_ac_5_box_add':'',
                              'ctl_surgery_ac_5_box_pos_add':'',
                              'ctl_sur_bio_ac_5___4':'0'}]
            elif 'ADDFrozenAC6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_ac_6_add_id':'',
                              'ctl_sur_add_bio_id_6':'',
                              'ctl_surgery_ac_6_freezer_add':'',
                              'ctl_surgery_ac_6_rack_loc_add':'',
                              'cdl_surgery_ac_6_box_add':'',
                              'ctl_surgery_ac_6_box_pos_add':'',
                              'ctl_sur_bio_ac_6___4':'0'}]
            elif 'ADDFrozenAC7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_ac_7_add_id':'',
                              'ctl_sur_add_bio_id_7':'',
                              'ctl_surgery_ac_7_freezer_add':'',
                              'ctl_surgery_ac_7_rack_loc_add':'',
                              'cdl_surgery_ac_7_box_add':'',
                              'ctl_surgery_ac_7_box_pos_add':'',
                              'ctl_sur_bio_ac_7___4':'0'}]
            elif 'ADDFrozenAC8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_sur_ac_8_add_id':'',
                              'ctl_sur_add_bio_id_8':'',
                              'ctl_surgery_ac_8_freezer_add':'',
                              'ctl_surgery_ac_8_rack_loc_add':'',
                              'cdl_surgery_ac_8_box_add':'',
                              'ctl_surgery_ac_8_box_pos_add':'',
                              'ctl_sur_bio_ac_8___4':'0'}]
            elif 'FrozenTI1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_1_frozen_id':'',
                              'ctl_surg_biopsy_id_1':'',
                              'ctl_surgery_ti_1_freezer':'',
                              'ctl_surgery_ti_1_rack_loc_2':'',
                              'ctl_surgery_ti_1_box':'',
                              'ctl_surgery_ti_1_box_pos':'',
                              'ctl_sur_bio_ti_1___3':'0'}]
            elif 'FrozenTI2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surg_biopsy_id_2':'',
                              'ctl_surgery_ti_2_frozen_id':'',
                              'ctl_surgery_ti_2_freezer':'',
                              'ctl_surgery_ti_2_rack_loc':'',
                              'ctl_surgery_ti_2_box':'',
                              'ctl_surg_box_position_2':'',
                              'ctl_sur_bio_ti_2___3':'0'}]
            elif 'FrozenTI3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surg_biopsy_id_3':'',
                              'ctl_surgery_ti_3_frozen_id':'',
                              'ctl_surgery_ti_3_freezer':'',
                              'ctl_surgery_ti_3_rack_loc':'',
                              'ctl_surgery_ti_3_box':'',
                              'ctl_surgery_ti_3_box_pos':'',
                              'ctl_sur_bio_ti_3___3':'0'}]
            elif 'FrozenAC4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surg_biopsy_id_4':'',
                              'ctl_surgery_ac_4_frozen_id':'',
                              'ctl_surgery_ac_4_freezer':'',
                              'ctl_surgery_ac_4_rack_loc':'',
                              'ctl_surgery_ac_4_box':'',
                              'ctl_surgery_ac_4_box_pos':'',
                              'ctl_sur_bio_ac_4___3':'0'}]
            elif 'FrozenAC5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_5_frozen_id':'',
                              'ctl_surg_biopsy_id_5':'',
                              'ctl_surgery_ac_5_freezer':'',
                              'ctl_surgery_ac_5_rack_loc':'',
                              'ctl_surgery_ac_5_box':'',
                              'ctl_surgery_ac_5_box_pos':'',
                              'ctl_sur_bio_ac_5___3':'0'}]
            elif 'FrozenAC6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_6_frozen_id':'',
                              'ctl_surg_biopsy_id_6':'',
                              'ctl_surgery_ac_6_freezer':'',
                              'ctl_surgery_ac_6_rack_loc':'',
                              'ctl_surgery_ac_6_box':'',
                              'ctl_surgery_ac_6_box_pos':'',
                              'ctl_sur_bio_ac_6___3':'0'}]
            elif 'FrozenAC7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_7_frozen_id':'',
                              'ctl_surg_biopsy_id_7':'',
                              'ctl_surgery_ac_7_freezer':'',
                              'ctl_surgery_ac_7_rack_loc':'',
                              'ctl_surgery_ac_7_box':'',
                              'ctl_surgery_ac_7_box_pos':'',
                              'ctl_sur_bio_ac_7___3':'0'}]
            elif 'FrozenAC8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_8_frozen_id':'',
                              'ctl_surg_biopsy_id_8':'',
                              'ctl_surgery_ac_8_freezer':'',
                              'ctl_surgery_ac_8_rack_loc':'',
                              'ctl_surgery_ac_8_box':'',
                              'ctl_surgery_ac_8_box_pos':'',
                              'ctl_sur_bio_ac_8___3':'0'}]
            
        elif 'Fresh' in barcode_id:
   
            if 'FreshTI1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_surgery_ti_1_fresh_id':'',
                              'ctl_sur_bio_ti_1___1':'0'}]
            elif 'FreshTI2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_2_fresh_id':'', 
                              'ctl_sur_bio_ti_2___1':'0'}]
            elif 'FreshTI3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_surgery_ti_3_fresh_id':'',
                              'ctl_sur_bio_ti_3___1':'0'}]                              
            elif 'FreshAC4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_4_fresh_id':'', 
                              'ctl_sur_bio_ac_4___1':'0'}]                              
            elif 'FreshAC5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_5_fresh_id':'', 
                              'ctl_sur_bio_ac_5___1':'0'}]                              
            elif 'FreshAC6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_6_fresh_id':'', 
                              'ctl_sur_bio_ac_6___1':'0'}]                              
            elif 'FreshAC7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_7_fresh_id':'',
                              'ctl_sur_bio_ac_7___1':'0'}]                              
            elif 'FreshAC8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_surgery_ac_8_fresh_id':'',
                              'ctl_sur_bio_ac_8___1':'0'}]                              
                              
        elif 'Fixed' in barcode_id:
            if 'FixedTI1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_1_fixed_id':'', 
                              'ctl_sur_bio_ti_1___2':'0'}]                               
            elif 'FixedTI2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_2_fixed_id':'', 
                              'ctl_sur_bio_ti_2___2':'0'}]                               
            elif 'FixedTI3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_3_fixed_id':'', 
                              'ctl_sur_bio_ti_3___2':'0'}]                               
            elif 'FixedAC4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_4_fixed_id':'', 
                              'ctl_sur_bio_ac_4___2':'0'}]                               
            elif 'FixedAC5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_5_fixed_id':'', 
                              'ctl_sur_bio_ac_5___2':'0'}]                               
            elif 'FixedAC6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_6_fixed_id':'',
                              'ctl_sur_bio_ac_6___2':'0'}]                               
            elif 'FixedAC7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_surgery_ac_7_fixed_id':'',
                              'ctl_sur_bio_ac_7___2':'0'}]                               
            elif 'FixedAC8' in barcode_id: 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_8_fixed_id':'',
                              'ctl_sur_bio_ac_8___2':'0'}] 
        response = self.project.import_records(to_import,overwrite='overwrite')
        return True  
                              
    def update_REDCAP_SOPHIE_FROM_LOCATION_APP(self,subject_id,barcode_id, study_type, loc_tuple ):
        if study_type == 'CD_ENDO':
            self.update_CD_END_SOPHIE(subject_id,barcode_id,loc_tuple)
        elif study_type == 'CTL_ENDO':
            self.update_CTL_END_SOPHIE(subject_id,barcode_id,loc_tuple)
        elif study_type == 'CD_Surgery':
            self.update_CD_Surgery_SOPHIE(subject_id,barcode_id,loc_tuple)
        elif study_type == 'CTL_Surgery':
            self.update_CTL_Surgery_SOPHIE(subject_id,barcode_id,loc_tuple)  

    def update_CD_END_SOPHIE(self,subject_id,barcode_id,loc_tuple):
        to_import = []
        if 'SR' in barcode_id:
            if 'SR1' in barcode_id:
                if 'SR10' in barcode_id:
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'cd_arm_1',
                                  'specimen_serum_500_6_freezer_3':loc_tuple[1],
                                  'specimen_serum_500_6_rack_loc_3':loc_tuple[2],
                                  'specimen_serum_500_6_box_4':loc_tuple[3],
                                  'specimen_serum_500_6_box_pos_3':loc_tuple[4]}]
                elif 'SR11' in barcode_id:
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'cd_arm_1',
                                  'specimen_serum_500_7_freezer_4':loc_tuple[1],
                                  'specimen_serum_500_7_rack_loc_4':loc_tuple[2],
                                  'specimen_serum_500_7_box_5':loc_tuple[3],
                                  'specimen_serum_500_7_box_pos_4':loc_tuple[4]}]
                else: # should be SR1
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'cd_arm_1',              
                                  'specimen_serum_100_1_freezer':loc_tuple[1],
                                  'specimen_serum_100_1_rack_loc':loc_tuple[2],
                                  'specimen_serum_100_1_box_2':loc_tuple[3],
                                  'specimen_serum1_box_pos':loc_tuple[4]}]
            elif 'SR2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                               'redcap_event_name':'cd_arm_1',                     
                                'specimen_serum_100_2_freezer':loc_tuple[1],
                                'specimen_serum_100_2_rack_loc':loc_tuple[2],
                                'specimen_serum_100_1_box':loc_tuple[3],
                                'specimen_serum_100_1_box_pos':loc_tuple[4]}]
            elif 'SR3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'specimen_serum_100_3_freezer_2':loc_tuple[1],
                              'specimen_serum_100_3_rack_loc_2':loc_tuple[2],
                              'specimen_serum_100_3_box':loc_tuple[3],
                              'specimen_serum_100_1_box_pos_3':loc_tuple[4]}]
            elif 'SR4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'specimen_serum_250_freezer':loc_tuple[1],
                              'specimen_serum_250_rack_loc':loc_tuple[2],
                              'specimen_serum_250_box':loc_tuple[3],
                              'specimen_serum_250_box_pos':loc_tuple[4]}]
            elif 'SR5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'specimen_serum_500_1_freezer':loc_tuple[1],
                              'specimen_serum_500_1_rack_loc':loc_tuple[2],
                              'specimen_serum_500_1_box':loc_tuple[3],
                              'specimen_serum_500_1_box_pos':loc_tuple[4]}]
            elif 'SR6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'specimen_serum_500_2_freezer':loc_tuple[1],
                              'specimen_serum_500_2_rack_loc':loc_tuple[2],
                              'specimen_serum_500_2_box':loc_tuple[3],
                              'specimen_serum_500_2_box_pos':loc_tuple[4]}]
            elif 'SR7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'specimen_serum_500_3_freezer':loc_tuple[1],
                              'specimen_serum_500_3_rack_loc':loc_tuple[2],
                              'specimen_serum_500_3_box':loc_tuple[3],
                              'specimen_serum_500_3_box_pos':loc_tuple[4]}]
            elif 'SR8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'specimen_serum_500_4_freezer':loc_tuple[1],
                              'specimen_serum_500_4_rack_loc':loc_tuple[2],
                              'specimen_serum_500_3_box_2':loc_tuple[3],
                              'specimen_serum_500_4_box_pos':loc_tuple[4]}]
            elif 'SR9' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'specimen_serum_500_5_freezer_2':loc_tuple[1],
                              'specimen_serum_500_5_rack_loc_2':loc_tuple[2],
                              'specimen_serum_500_5_box_3':loc_tuple[3],
                              'specimen_serum_500_5_box_pos_2':loc_tuple[4]}]

                
        elif 'ST' in barcode_id:
            if 'ST1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_stool1_freezer':loc_tuple[1],
                              'specimen_stool1_rack':loc_tuple[2],
                              'specimen_stool1_box':loc_tuple[3],
                              'specimen_stool1_box_pos':loc_tuple[4]}]
            elif 'ST2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_stool2_freezer':loc_tuple[1],
                              'specimen_stool2_rack':loc_tuple[2],
                              'specimen_stool2_box':loc_tuple[3],
                              'specimen_stool2_box_pos':loc_tuple[4]}]                
            elif 'ST3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_stool3_freezer':loc_tuple[1],
                              'specimen_stool3_rack':loc_tuple[2],
                              'specimen_stool3_box':loc_tuple[3],
                              'specimen_stool3_box_pos':loc_tuple[4]}]                
            elif 'ST4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'specimen_stool4_freezer':loc_tuple[1],
                              'specimen_stool4_rack':loc_tuple[2],
                              'specimen_stool4_box':loc_tuple[3],
                              'specimen_stool4_box_pos':loc_tuple[4]}]                

        elif 'Frozen' in barcode_id:
            if 'ADDFrozenTIA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'cd_endo_add_ti_a_freezer':loc_tuple[1],
                              'cd_endo_add_ti_a_rack':loc_tuple[2],
                              'cd_endo_add_ti_a_box':loc_tuple[3],
                              'cd_endo_add_ti_a_box_position':loc_tuple[4],
                              'ti_involved_a_v2___4':'1'}] 
            elif 'ADDFrozenTIB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'cd_endo_add_ti_b_freezer':loc_tuple[1],
                              'cd_endo_add_ti_b_rack':loc_tuple[2],
                              'cd_endo_add_ti_b_box':loc_tuple[3],
                              'cd_endo_add_ti_b_box_position':loc_tuple[4],
                              'ti_non_involved_b_v2___4':'1'}] 
            elif 'ADDFrozenACA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'cd_endo_add_ac_a_freezer':loc_tuple[1],
                              'cd_endo_add_ac_a_rack':loc_tuple[2],
                              'cd_endo_add_ac_a_box':loc_tuple[3],
                              'cd_endo_add_ac_a_box_position':loc_tuple[4],
                              'ac_involved___4':'1'}] 
            elif 'ADDFrozenACB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'cd_endo_add_ac_b_freezer':loc_tuple[1],
                              'cd_endo_add_ac_b_rack':loc_tuple[2],
                              'cd_endo_add_ac_b_box':loc_tuple[3],
                              'cd_endo_add_ac_b_box_position':loc_tuple[4],
                              'ac_non_involved___4':'1'}] 
            elif 'FrozenTIA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'cd_endo_biopsies_freezer':loc_tuple[1],
                              'cd_endo_biopsy_rack_location':loc_tuple[2],
                              'cd_endo_biopsy_box_2':loc_tuple[3],
                              'cd_endo_biopsy_box_position_2':loc_tuple[4],
                              'ti_involved_a_v2___3':'1'}] 
            elif 'FrozenTIB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'cd_endo_biopsies_freezer_2':loc_tuple[1],
                              'cd_endo_biopsy_rack_location_2':loc_tuple[2],
                              'cd_endo_biopsy_box_3':loc_tuple[3],
                              'cd_endo_biopsy_box_position':loc_tuple[4],
                              'ti_non_involved_b_v2___3':'1'}] 
            elif 'FrozenACA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'cd_endo_biopsies_freezer_4':loc_tuple[1],
                              'cd_endo_biopsy_rack_location_4':loc_tuple[2],
                              'cd_endo_biopsy_box':loc_tuple[3],
                              'cd_endo_biopsy_box_position_3':loc_tuple[4],
                              'ac_involved___3':'0'}] 
            elif 'FrozenACB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'cd_endo_biopsies_freezer_3':loc_tuple[1],
                              'cd_endo_biopsy_rack_location_3':loc_tuple[2],
                              'cd_endo_biopsy_box_4':loc_tuple[3],
                              'cd_endo_biopsy_box_position_4':loc_tuple[4],
                              'ac_non_involved___3':'1'}] 
                
        elif 'Fresh' in barcode_id:
            
            if 'FreshTIA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'ti_involved_a_v2___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
            elif 'FreshTIB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'ti_non_involved_b_v2___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
            elif 'FreshACA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'ac_involved___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
            elif 'FreshACB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'ac_non_involved___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
        elif 'Fixed' in barcode_id:
            if 'FixedTIA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'ti_involved_a_v2___2':'1'}]
            elif 'FixedTIB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',
                              'ti_non_involved_b_v2___2':'1'}]
            elif 'FixedACA' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'ac_involved___2':'1'}]
            elif 'FixedACB' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_1',              
                              'ac_non_involved___2':'1'}]
                              
        #else: DNA
            # doNothing()
        print(to_import)
        response = self.project.import_records(to_import,overwrite='overwrite')
        return True          
    
    def update_CTL_END_SOPHIE(self,subject_id,barcode_id,loc_tuple):   
        to_import = []
        if 'SR' in barcode_id:
            if 'SR1' in barcode_id:
                if 'SR10' in barcode_id:
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'control_arm_1',
                                  'specimen_serum_500_6_freezer_3':loc_tuple[1],
                                  'specimen_serum_500_6_rack_loc_3':loc_tuple[2],
                                  'specimen_serum_500_6_box_4':loc_tuple[3],
                                  'specimen_serum_500_6_box_pos_3':loc_tuple[4]}]
                elif 'SR11' in barcode_id:
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'control_arm_1',
                                  'specimen_serum_500_7_freezer_4':loc_tuple[1],
                                  'specimen_serum_500_7_rack_loc_4':loc_tuple[2],
                                  'specimen_serum_500_7_box_5':loc_tuple[3],
                                  'specimen_serum_500_7_box_pos_4':loc_tuple[4]}]
                else: # should be SR1
                    to_import = [{'record_id_dem_endo':subject_id,
                                  'redcap_event_name':'control_arm_1',              
                                  'specimen_serum_100_1_freezer':loc_tuple[1],
                                  'specimen_serum_100_1_rack_loc':loc_tuple[2],
                                  'specimen_serum_100_1_box_2':loc_tuple[3],
                                  'specimen_serum1_box_pos':loc_tuple[4]}]
            elif 'SR2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                               'redcap_event_name':'control_arm_1',                     
                                'specimen_serum_100_2_freezer':loc_tuple[1],
                                'specimen_serum_100_2_rack_loc':loc_tuple[2],
                                'specimen_serum_100_1_box':loc_tuple[3],
                                'specimen_serum_100_1_box_pos':loc_tuple[4]}]
            elif 'SR3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_serum_100_3_freezer_2':loc_tuple[1],
                              'specimen_serum_100_3_rack_loc_2':loc_tuple[2],
                              'specimen_serum_100_3_box':loc_tuple[3],
                              'specimen_serum_100_1_box_pos_3':loc_tuple[4]}]
            elif 'SR4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_serum_250_freezer':loc_tuple[1],
                              'specimen_serum_250_rack_loc':loc_tuple[2],
                              'specimen_serum_250_box':loc_tuple[3],
                              'specimen_serum_250_box_pos':loc_tuple[4]}]
            elif 'SR5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_serum_500_1_freezer':loc_tuple[1],
                              'specimen_serum_500_1_rack_loc':loc_tuple[2],
                              'specimen_serum_500_1_box':loc_tuple[3],
                              'specimen_serum_500_1_box_pos':loc_tuple[4]}]
            elif 'SR6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_serum_500_2_freezer':loc_tuple[1],
                              'specimen_serum_500_2_rack_loc':loc_tuple[2],
                              'specimen_serum_500_2_box':loc_tuple[3],
                              'specimen_serum_500_2_box_pos':loc_tuple[4]}]
            elif 'SR7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_serum_500_3_freezer':loc_tuple[1],
                              'specimen_serum_500_3_rack_loc':loc_tuple[2],
                              'specimen_serum_500_3_box':loc_tuple[3],
                              'specimen_serum_500_3_box_pos':loc_tuple[4]}]
            elif 'SR8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_serum_500_4_freezer':loc_tuple[1],
                              'specimen_serum_500_4_rack_loc':loc_tuple[2],
                              'specimen_serum_500_3_box_2':loc_tuple[3],
                              'specimen_serum_500_4_box_pos':loc_tuple[4]}]
            elif 'SR9' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_serum_500_5_freezer_2':loc_tuple[1],
                              'specimen_serum_500_5_rack_loc_2':loc_tuple[2],
                              'specimen_serum_500_5_box_3':loc_tuple[3],
                              'specimen_serum_500_5_box_pos_2':loc_tuple[4]}]

                
        elif 'ST' in barcode_id:
            if 'ST1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_stool1_freezer':loc_tuple[1],
                              'specimen_stool1_rack':loc_tuple[2],
                              'specimen_stool1_box':loc_tuple[3],
                              'specimen_stool1_box_pos':loc_tuple[4]}]
            elif 'ST2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_stool2_freezer':loc_tuple[1],
                              'specimen_stool2_rack':loc_tuple[2],
                              'specimen_stool2_box':loc_tuple[3],
                              'specimen_stool2_box_pos':loc_tuple[4]}]                
            elif 'ST3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_stool3_freezer':loc_tuple[1],
                              'specimen_stool3_rack':loc_tuple[2],
                              'specimen_stool3_box':loc_tuple[3],
                              'specimen_stool3_box_pos':loc_tuple[4]}]                
            elif 'ST4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_stool4_freezer':loc_tuple[1],
                              'specimen_stool4_rack':loc_tuple[2],
                              'specimen_stool4_box':loc_tuple[3],
                              'specimen_stool4_box_pos':loc_tuple[4]}] 

        elif 'Frozen' in barcode_id:
            ###### NOTE: NO check box for add frozen
            if 'ADDFrozenTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_freezer_ti_add':loc_tuple[1],
                              'ctl_endo_rack_ti_add':loc_tuple[2],
                              'ctl_endo_box_ti_add':loc_tuple[3],
                              'ctl_endo_box_pos_ti_add':loc_tuple[4],
                              'specimen_bio_ctl_ti___4': '1'}]
            elif 'ADDFrozenAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_freezer_ac_add':loc_tuple[1],
                              'ctl_endo_rack_ac_add':loc_tuple[2],
                              'ctl_endo_box_ac_add':loc_tuple[3],
                              'ctl_endo_box_pos_ac_add':loc_tuple[4],
                              'specimen_bio_ctl_ac___4': '1'}]
            elif 'FrozenTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_freezer_ti_biopsy':loc_tuple[1],
                              'ctl_endo_rack_ti_biopsy':loc_tuple[2],
                              'ctl_endo_box_ti_biopsy':loc_tuple[3],
                              'ctl_endo_box_pos_ti_biopsy':loc_tuple[4],
                              'specimen_bio_ctl_ti___3':'1'}]
            elif 'FrozenAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'ctl_endo_freezer_ac_biopsy':loc_tuple[1],
                              'ctl_endo_rack_ac_biopsy':loc_tuple[2],
                              'ctl_endo_box_ac_biopsy':loc_tuple[3],
                              'ctl_endo_box_pos_ac_biopsy':loc_tuple[4],
                              'specimen_bio_ctl_ac___3':'1'}]
                
        elif 'Fresh' in barcode_id:
            
            if 'FreshTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1', 
                              'specimen_bio_ctl_ti___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
            elif 'FreshAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_bio_ctl_ac___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
        elif 'Fixed' in barcode_id:
            if 'FixedTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',
                              'specimen_bio_ctl_ti___2':'1'}]
            elif 'FixedAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_1',              
                              'specimen_bio_ctl_ac___2':'1'}]
           
        #else: DNA
            # doNothing()
        
        response = self.project.import_records(to_import,overwrite='overwrite')
        return True 
       
#         to_import = [{'record_id_dem_endo':subject_id,
#                         'redcap_event_name':'control_arm_1',
#                         'stool_collected_endo_cd_v2':'1',
#                         'specimen_stool_num_al':'4',
#                         'specimen_stool_id_ali':barcode_id_list[0],
#                         'specimen_stool_id_ali_1':barcode_id_list[1],
#                         'specimen_stool_id_ali_2':barcode_id_list[2],
#                         'specimen_stool_id_ali_3':barcode_id_list[3],
#                         'serum_collected_endo_cd_v2':'1',
#                         'specimen_serum_al_100':'3',
#                         'specimen_serum_al_1_100_id':barcode_id_list[4],
#                         'specimen_serum_al_2_100_id':barcode_id_list[5],
#                         'specimen_serum_al_3_100':barcode_id_list[6],
#                         'specimen_serum_al_250':'1',
#                         'specimen_serum_al_250_1':barcode_id_list[7],
#                         'specimen_serum_al_500':'7',
#                         'specimen_serum_al_500_1':barcode_id_list[8],
#                         'specimen_serum_al_500_2':barcode_id_list[9],
#                         'specimen_serum_al_500_3':barcode_id_list[10],
#                         'specimen_serum_al_500_4':barcode_id_list[11],
#                         'specimen_serum_al_500_5':barcode_id_list[12],
#                         'specimen_serum_al_500_6':barcode_id_list[13],
#                         'specimen_serum_al_500_7':barcode_id_list[14],
#                         'dna_collected_endo_cd_v2':'1',
#                         'specimen_dna_id':barcode_id_list[15],
#                         'ctl_endo_ti_fresh_id':barcode_id_list[16],
#                         'ctl_endo_ti_fixed_id':barcode_id_list[17],
#                         'ctl_endo_ti_frozen_id':barcode_id_list[18],
#                         'ctl_endo_ac_fresh_id':barcode_id_list[19],
#                         'ctl_endo_ac_fixed_id':barcode_id_list[20],
#                         'ctl_endo_ac_frozen_id':barcode_id_list[21],
#                         'ctl_endo_biopsy_id_1':barcode_id_list[18],
#                         'ctl_endo_biopsy_id_2':barcode_id_list[21]}]
#         response = self.project.import_records(to_import)
#         return True  
    
    def update_CD_Surgery_SOPHIE(self,subject_id,barcode_id,loc_tuple): 
        to_import = []
        
        if 'Frozen' in barcode_id:
            if 'ADDFrozenTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_freezer_ti_add':loc_tuple[1],
                              'cd_surgery_rack_loc_ti_add':loc_tuple[2],
                              'cd_surgery_box_ti_add':loc_tuple[3],
                              'cd_surgery_box_pos_ti_add':loc_tuple[4],
                              'cd_sur_bio_ti___4': '1'}]
            elif 'ADDFrozenAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_freezer_ac_add':loc_tuple[1],
                              'cd_surgery_rack_loc_ti_add_2':loc_tuple[2],
                              'cd_surgery_box_ac_add':loc_tuple[3],
                              'cd_surgery_box_pos_ac_add':loc_tuple[4],
                              'cd_sur_bio_ac___4': '1'}]                             
            elif 'FrozenTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_freezer_ti_biopsy':loc_tuple[1],
                              'cd_surgery_rack_loc_ti_biopsy':loc_tuple[2],
                              'cd_surgery_box_ti_biopsy':loc_tuple[3],
                              'cd_surgery_box_pos_ti_biopsy':loc_tuple[4],
                              'cd_sur_bio_ti___3':'1'}]        
            elif 'FrozenAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_surgery_freezer_ac_biopsy':loc_tuple[1],
                              'cd_surgery_rack_loc_ac_biopsy':loc_tuple[2],
                              'cd_surgery_box_ac_biopsy':loc_tuple[3],
                              'cd_surgery_box_pos_ac_biopsy':loc_tuple[4],
                              'cd_sur_bio_ac___3':'1'}]
                
        elif 'Fresh' in barcode_id:
                          
            if 'FreshTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2', 
                              'cd_sur_bio_ti___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
            elif 'FreshAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_sur_bio_ac___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]

        elif 'Fixed' in barcode_id:
            if 'FixedTI' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',
                              'cd_sur_bio_ti___2':'1'}]
            elif 'FixedAC' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'cd_arm_2',              
                              'cd_sur_bio_ac___2':'1'}]                              
                              #else:
            # doNothing()
        
        response = self.project.import_records(to_import,overwrite='overwrite')
        return True 
    
#         to_import = [{'record_id_dem_endo':subject_id,
#                         'redcap_event_name':'cd_arm_2',
#                         'cd_surgery_ti_fresh_id':barcode_id_list[0],
#                         'cd_surgery_ti_fixed_id':barcode_id_list[1],
#                         'cd_surgery_ti_frozen_id':barcode_id_list[2],
#                         'cd_surgery_ac_fresh_id':barcode_id_list[3],
#                         'cd_surgery_ac_fixed_id':barcode_id_list[4],
#                         'cd_surgery_ac_frozen_id':barcode_id_list[5],
#                         'cd_surg_biopsy_id_1':barcode_id_list[2],
#                         'cd_surg_biopsy_id_2':barcode_id_list[5]}]
#         response = self.project.import_records(to_import)
#         return True

    def update_CTL_Surgery_SOPHIE(self,subject_id,barcode_id,loc_tuple):  
        to_import = []

        if 'Frozen' in barcode_id:
            if 'ADDFrozenTI1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_1_freezer_add':loc_tuple[1],
                              'ctl_surgery_ti_1_rack_loc_add':loc_tuple[2],
                              'ctl_surgery_ti_1_box_add':loc_tuple[3],
                              'ctl_surgery_ti_1_box_pos_add':loc_tuple[4],
                              'ctl_sur_bio_ti_1___4': '1'}]
            elif 'ADDFrozenTI2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_2_freezer_add':loc_tuple[1],
                              'ctl_surgery_ti_2_rack_loc_add':loc_tuple[2],
                              'ctl_surgery_ti_2_box_add':loc_tuple[3],
                              'ctl_surgery_ti_2_box_pos_add':loc_tuple[4],
                              'ctl_sur_bio_ti_2___4': '1'}]
            elif 'ADDFrozenTI3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_3_freezer_add':loc_tuple[1],
                              'ctl_surgery_ti_3_rack_loc_add':loc_tuple[2],
                              'cdl_surgery_ti_3_box_add':loc_tuple[3],
                              'ctl_surgery_ti_3_box_pos_add':loc_tuple[4],
                              'ctl_sur_bio_ti_3___4': '1'}]                              
            elif 'ADDFrozenAC4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_4_freezer_add':loc_tuple[1],
                              'ctl_surgery_ac_4_rack_loc_add':loc_tuple[2],
                              'cdl_surgery_ac_4_box_add':loc_tuple[3],
                              'ctl_surgery_ac_4_box_pos_add':loc_tuple[4],
                              'ctl_sur_bio_ac_4___4': '1'}]
            elif 'ADDFrozenAC5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_5_freezer_add':loc_tuple[1],
                              'ctl_surgery_ac_5_rack_loc_add':loc_tuple[2],
                              'cdl_surgery_ac_5_box_add':loc_tuple[3],
                              'ctl_surgery_ac_5_box_pos_add':loc_tuple[4],
                              'ctl_sur_bio_ac_5___4': '1'}]
            elif 'ADDFrozenAC6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_6_freezer_add':loc_tuple[1],
                              'ctl_surgery_ac_6_rack_loc_add':loc_tuple[2],
                              'cdl_surgery_ac_6_box_add':loc_tuple[3],
                              'ctl_surgery_ac_6_box_pos_add':loc_tuple[4],
                              'ctl_sur_bio_ac_6___4': '1'}]
            elif 'ADDFrozenAC7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_7_freezer_add':loc_tuple[1],
                              'ctl_surgery_ac_7_rack_loc_add':loc_tuple[2],
                              'cdl_surgery_ac_7_box_add':loc_tuple[3],
                              'ctl_surgery_ac_7_box_pos_add':loc_tuple[4],
                              'ctl_sur_bio_ac_7___4': '1'}]
            elif 'ADDFrozenAC8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_8_freezer_add':loc_tuple[1],
                              'ctl_surgery_ac_8_rack_loc_add':loc_tuple[2],
                              'cdl_surgery_ac_8_box_add':loc_tuple[3],
                              'ctl_surgery_ac_8_box_pos_add':loc_tuple[4],
                              'ctl_sur_bio_ac_8___4': '1'}]
            elif 'FrozenTI1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_1_freezer':loc_tuple[1],
                              'ctl_surgery_ti_1_rack_loc_2':loc_tuple[2],
                              'ctl_surgery_ti_1_box':loc_tuple[3],
                              'ctl_surgery_ti_1_box_pos':loc_tuple[4],
                              'ctl_sur_bio_ti_1___3':'1'}]
            elif 'FrozenTI2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_2_freezer':loc_tuple[1],
                              'ctl_surgery_ti_2_rack_loc':loc_tuple[2],
                              'ctl_surgery_ti_2_box':loc_tuple[3],
                              'ctl_surg_box_position_2':loc_tuple[4],
                              'ctl_sur_bio_ti_2___3':'1'}]
            elif 'FrozenTI3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ti_3_freezer':loc_tuple[1],
                              'ctl_surgery_ti_3_rack_loc':loc_tuple[2],
                              'ctl_surgery_ti_3_box':loc_tuple[3],
                              'ctl_surgery_ti_3_box_pos':loc_tuple[4],
                              'ctl_sur_bio_ti_3___3':'1'}]
            elif 'FrozenAC4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_4_freezer':loc_tuple[1],
                              'ctl_surgery_ac_4_rack_loc':loc_tuple[2],
                              'ctl_surgery_ac_4_box':loc_tuple[3],
                              'ctl_surgery_ac_4_box_pos':loc_tuple[4],
                              'ctl_sur_bio_ac_4___3':'1'}]
            elif 'FrozenAC5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_5_freezer':loc_tuple[1],
                              'ctl_surgery_ac_5_rack_loc':loc_tuple[2],
                              'ctl_surgery_ac_5_box':loc_tuple[3],
                              'ctl_surgery_ac_5_box_pos':loc_tuple[4],
                              'ctl_sur_bio_ac_5___3':'1'}]
            elif 'FrozenAC6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_6_freezer':loc_tuple[1],
                              'ctl_surgery_ac_6_rack_loc':loc_tuple[2],
                              'ctl_surgery_ac_6_box':loc_tuple[3],
                              'ctl_surgery_ac_6_box_pos':loc_tuple[4],
                              'ctl_sur_bio_ac_6___3':'1'}]
            elif 'FrozenAC7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_7_freezer':loc_tuple[1],
                              'ctl_surgery_ac_7_rack_loc':loc_tuple[2],
                              'ctl_surgery_ac_7_box':loc_tuple[3],
                              'ctl_surgery_ac_7_box_pos':loc_tuple[4],
                              'ctl_sur_bio_ac_7___3':'1'}]
            elif 'FrozenAC8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2',
                              'ctl_surgery_ac_8_freezer':loc_tuple[1],
                              'ctl_surgery_ac_8_rack_loc':loc_tuple[2],
                              'ctl_surgery_ac_8_box':loc_tuple[3],
                              'ctl_surgery_ac_8_box_pos':loc_tuple[4],
                              'ctl_sur_bio_ac_8___3':'1'}]
            
        elif 'Fresh' in barcode_id:
   
            if 'FreshTI1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ti_1___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
            elif 'FreshTI2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ti_2___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]
            elif 'FreshTI3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ti_3___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]                              
            elif 'FreshAC4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_4___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]                              
            elif 'FreshAC5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_5___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]                              
            elif 'FreshAC6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_6___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]                              
            elif 'FreshAC7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_7___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]                              
            elif 'FreshAC8' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_8___1':'1',
                              'distri_lau_yes_no':'1',
                              'distributed_lau_date':self.getCurrentTime()}]                              
                              
        elif 'Fixed' in barcode_id:
            if 'FixedTI1' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ti_1___2':'1'}]                               
            elif 'FixedTI2' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ti_2___2':'1'}]                               
            elif 'FixedTI3' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ti_3___2':'1'}]                               
            elif 'FixedAC4' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_4___2':'1'}]                               
            elif 'FixedAC5' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_5___2':'1'}]                               
            elif 'FixedAC6' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_6___2':'1'}]                               
            elif 'FixedAC7' in barcode_id:
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_7___2':'1'}]                               
            elif 'FixedAC8' in barcode_id: 
                to_import = [{'record_id_dem_endo':subject_id,
                              'redcap_event_name':'control_arm_2', 
                              'ctl_sur_bio_ac_8___2':'1'}]                               
        #else:
            # doNothing()
        
        response = self.project.import_records(to_import,overwrite='overwrite')
        return True 
    
#         to_import = [{'record_id_dem_endo':subject_id,
#                         'redcap_event_name':'control_arm_2',
#                         'ctl_surgery_ti_1_fresh_id':barcode_id_list[0],
#                         'ctl_surgery_ti_1_fixed_id':barcode_id_list[1],
#                         'ctl_surgery_ti_1_frozen_id':barcode_id_list[2],
#                         'ctl_surgery_ti_2_fresh_id':barcode_id_list[3],
#                         'ctl_surgery_ti_2_fixed_id':barcode_id_list[4],
#                         'ctl_surgery_ti_2_frozen_id':barcode_id_list[5],
#                         'ctl_surgery_ti_3_fresh_id':barcode_id_list[6],
#                         'ctl_surgery_ti_3_fixed_id':barcode_id_list[7],
#                         'ctl_surgery_ti_3_frozen_id':barcode_id_list[8],
#                         'ctl_surgery_ac_4_fresh_id':barcode_id_list[9],
#                         'ctl_surgery_ac_4_fixed_id':barcode_id_list[10],
#                         'ctl_surgery_ac_4_frozen_id':barcode_id_list[11],
#                         'ctl_surgery_ac_5_fresh_id':barcode_id_list[12],
#                         'ctl_surgery_ac_5_fixed_id':barcode_id_list[13],
#                         'ctl_surgery_ac_5_frozen_id':barcode_id_list[14],
#                         'ctl_surgery_ac_6_fresh_id':barcode_id_list[15],
#                         'ctl_surgery_ac_6_fixed_id':barcode_id_list[16],
#                         'ctl_surgery_ac_6_frozen_id':barcode_id_list[17],
#                         'ctl_surgery_ac_7_fresh_id':barcode_id_list[18],
#                         'ctl_surgery_ac_7_fixed_id':barcode_id_list[19],
#                         'ctl_surgery_ac_7_frozen_id':barcode_id_list[20],
#                         'ctl_surgery_ac_8_fresh_id':barcode_id_list[21],
#                         'ctl_surgery_ac_8_fixed_id':barcode_id_list[22],
#                         'ctl_surgery_ac_8_frozen_id':barcode_id_list[23],
#                         'ctl_surg_biopsy_id_1':barcode_id_list[2],
#                         'ctl_surg_biopsy_id_2':barcode_id_list[5],
#                         'ctl_surg_biopsy_id_3':barcode_id_list[8],
#                         'ctl_surg_biopsy_id_4':barcode_id_list[11],
#                         'ctl_surg_biopsy_id_5':barcode_id_list[14],
#                         'ctl_surg_biopsy_id_6':barcode_id_list[17],
#                         'ctl_surg_biopsy_id_7':barcode_id_list[20],
#                         'ctl_surg_biopsy_id_8':barcode_id_list[23]}]
#         response = self.project.import_records(to_import)
#         return True
    
    
#     def update_CD_END_SOPHIE_extra_frozen(self,subject_id,barcode_id_list):
#         to_import = [{'record_id_dem_endo':subject_id,
#                           'redcap_event_name':'cd_arm_1',
#                           'stool_collected_endo_cd_v2':'1',
#    #                     'stool_collection_endo_cd_v2':str(cur_date),
#                           'specimen_stool_num_al':'4',
#                           'specimen_stool_id_ali':barcode_id_list[0],
#                           'specimen_stool_id_ali_1':barcode_id_list[1],
#                           'specimen_stool_id_ali_2':barcode_id_list[2],
#                           'specimen_stool_id_ali_3':barcode_id_list[3],
#                           'serum_collected_endo_cd_v2':'1',
#                           'specimen_serum_al_100':'3',
#                           'specimen_serum_al_1_100_id':barcode_id_list[4],
#                           'specimen_serum_al_2_100_id':barcode_id_list[5],
#                           'specimen_serum_al_3_100':barcode_id_list[6],
#                           'specimen_serum_al_250':'1',
#                           'specimen_serum_al_250_1':barcode_id_list[7],
#                           'specimen_serum_al_500':'7',
#                           'specimen_serum_al_500_1':barcode_id_list[8],
#                           'specimen_serum_al_500_2':barcode_id_list[9],
#                           'specimen_serum_al_500_3':barcode_id_list[10],
#                           'specimen_serum_al_500_4':barcode_id_list[11],
#                           'specimen_serum_al_500_5':barcode_id_list[12],
#                           'specimen_serum_al_500_6':barcode_id_list[13],
#                           'specimen_serum_al_500_7':barcode_id_list[14],
#                           'dna_collected_endo_cd_v2':'1',
#                           'specimen_dna_id':barcode_id_list[15],
#     #                    'date_of_biopsies_collect_endo_cd_v2':str(cur_date),
# #                         'ti_involved_a_v2___1':'1',
# #                         'ti_involved_a_v2___2':'1',
# #                         'ti_involved_a_v2___3':'1',
# #                         'ti_non_involved_b_v2___1':'1',
# #                         'ti_non_involved_b_v2___2':'1',
# #                         'ti_non_involved_b_v2___3':'1',
# #                         'ac_involved___1':'1',
# #                         'ac_involved___2':'1',
# #                         'ac_involved___3':'1',
# #                         'ac_non_involved___1':'1',
# #                         'ac_non_involved___2':'1',
# #                         'ac_non_involved___3':'1',
#                           'cd_endo_ti_a_fresh_id':barcode_id_list[16],
#                           'sc_endo_ti_a_fixed_id':barcode_id_list[17],
#                           'cd_endo_ti_a_frozen_id':barcode_id_list[18],
#                           'cd_endo_ti_b_fresh_id':barcode_id_list[19],
#                           'cd_endo_ti_b_fixed_id':barcode_id_list[20],
#                           'cd_endo_ti_b_frozen_id':barcode_id_list[21],
#                           'cd_endo_ac_a_fresh_id':barcode_id_list[22],
#                           'cd_endo_ac_a_fixed_id':barcode_id_list[23],
#                           'cd_endo_ac_a_frozen_id':barcode_id_list[24],
#                           'cd_endo_ac_b_fresh_id':barcode_id_list[25],
#                           'cd_endo_ac_b_fixed_id':barcode_id_list[26],
#                           'cd_endo_ac_b_frozen_id':barcode_id_list[27],
#                           'cd_endo_biopsy_id':barcode_id_list[18],
#                           'cd_endo_biopsy_id2':barcode_id_list[21],
#                           'cd_endo_biopsy_id3':barcode_id_list[24],
#                           'cd_endo_biopsy_id4':barcode_id_list[27],
#                           'second_frozen': '1',
#                           'ti_add_frozen_a_id': barcode_id_list[28],
#                           'ti_add_frozen_b_id': barcode_id_list[29],
#                           'ac_add_frozen_a_id': barcode_id_list[30],
#                           'ac_add_frozen_b_id': barcode_id_list[31],
#                           'cd_endo_add_ti_a_id': barcode_id_list[28],
#                           'cd_endo_add_ti_b_id': barcode_id_list[29],
#                           'cd_endo_add_ac_a_id': barcode_id_list[30],
#                           'cd_endo_add_ac_b_id': barcode_id_list[31]}]
        
#         response = self.project.import_records(to_import)
#         return True  
    
#     def update_CTL_END_SOPHIE_extra_frozen(self,subject_id,barcode_id_list):   
#    #     curTime = datetime.now()
#    #     cur_date = curTime.strftime('%Y-%m-%d %H:%M')
#         to_import = [{'record_id_dem_endo':subject_id,
#                         'redcap_event_name':'control_arm_1',
#                         'stool_collected_endo_cd_v2':'1',
#    #                     'stool_collection_endo_cd_v2':str(cur_date),
#                         'specimen_stool_num_al':'4',
#                         'specimen_stool_id_ali':barcode_id_list[0],
#                         'specimen_stool_id_ali_1':barcode_id_list[1],
#                         'specimen_stool_id_ali_2':barcode_id_list[2],
#                         'specimen_stool_id_ali_3':barcode_id_list[3],
#                         'serum_collected_endo_cd_v2':'1',
#                         'specimen_serum_al_100':'3',
#                         'specimen_serum_al_1_100_id':barcode_id_list[4],
#                         'specimen_serum_al_2_100_id':barcode_id_list[5],
#                         'specimen_serum_al_3_100':barcode_id_list[6],
#                         'specimen_serum_al_250':'1',
#                         'specimen_serum_al_250_1':barcode_id_list[7],
#                         'specimen_serum_al_500':'7',
#                         'specimen_serum_al_500_1':barcode_id_list[8],
#                         'specimen_serum_al_500_2':barcode_id_list[9],
#                         'specimen_serum_al_500_3':barcode_id_list[10],
#                         'specimen_serum_al_500_4':barcode_id_list[11],
#                         'specimen_serum_al_500_5':barcode_id_list[12],
#                         'specimen_serum_al_500_6':barcode_id_list[13],
#                         'specimen_serum_al_500_7':barcode_id_list[14],
#                         'dna_collected_endo_cd_v2':'1',
#                         'specimen_dna_id':barcode_id_list[15],
#  #                     'date_of_biopsies_collect_endo_cd_v2':str(cur_date),
# #                         'specimen_bio_ctl_ti___1':'1',
# #                         'specimen_bio_ctl_ti___2':'1',
# #                         'specimen_bio_ctl_ti___3':'1',
# #                         'specimen_bio_ctl_ac___1':'1',
# #                         'specimen_bio_ctl_ac___2':'1',
# #                         'specimen_bio_ctl_ac___3':'1',
#                         'ctl_endo_ti_fresh_id':barcode_id_list[16],
#                         'ctl_endo_ti_fixed_id':barcode_id_list[17],
#                         'ctl_endo_ti_frozen_id':barcode_id_list[18],
#                         'ctl_endo_ac_fresh_id':barcode_id_list[19],
#                         'ctl_endo_ac_fixed_id':barcode_id_list[20],
#                         'ctl_endo_ac_frozen_id':barcode_id_list[21],
#                         'ctl_endo_biopsy_id_1':barcode_id_list[18],
#                         'ctl_endo_biopsy_id_2':barcode_id_list[21],
#                         'second_frozen': '1',
#                         'ti_add_frozen_a_id': barcode_id_list[22],
#                         'ti_add_frozen_b_id': barcode_id_list[23],
#                         'ac_add_frozen_a_id': barcode_id_list[24],
#                         'ac_add_frozen_b_id': barcode_id_list[25],
#                         'cd_endo_add_ti_a_id': barcode_id_list[22],
#                         'cd_endo_add_ti_b_id': barcode_id_list[23],
#                         'cd_endo_add_ac_a_id': barcode_id_list[24],
#                         'cd_endo_add_ac_b_id': barcode_id_list[25]}]
#         response = self.project.import_records(to_import)
#         return True  
    
#     def update_CD_Surgery_SOPHIE_extra_frozen(self,subject_id,barcode_id_list):  
#  #       curTime = datetime.now()
#  #       cur_date = curTime.strftime('%Y-%m-%d %H:%M')
#         to_import = [{'record_id_dem_endo':subject_id,
#                         'redcap_event_name':'cd_arm_2',
#                         'cd_surgery_ti_fresh_id':barcode_id_list[0],
#                         'cd_surgery_ti_fixed_id':barcode_id_list[1],
#                         'cd_surgery_ti_frozen_id':barcode_id_list[2],
#                         'cd_surgery_ac_fresh_id':barcode_id_list[3],
#                         'cd_surgery_ac_fixed_id':barcode_id_list[4],
#                         'cd_surgery_ac_frozen_id':barcode_id_list[5],
#                         'cd_surg_biopsy_id_1':barcode_id_list[2],
#                         'cd_surg_biopsy_id_2':barcode_id_list[5],
#                         'second_frozen': '1',
#                         'ti_add_frozen_a_id': barcode_id_list[6],
#                         'ti_add_frozen_b_id': barcode_id_list[7],
#                         'ac_add_frozen_a_id': barcode_id_list[8],
#                         'ac_add_frozen_b_id': barcode_id_list[9],
#                         'cd_endo_add_ti_a_id': barcode_id_list[6],
#                         'cd_endo_add_ti_b_id': barcode_id_list[7],
#                         'cd_endo_add_ac_a_id': barcode_id_list[8],
#                         'cd_endo_add_ac_b_id': barcode_id_list[9]}]
#         response = self.project.import_records(to_import)
#         return True

#     def update_CTL_Surgery_SOPHIE_extra_frozen(self,subject_id,barcode_id_list):  
#         to_import = [{'record_id_dem_endo':subject_id,
#                         'redcap_event_name':'control_arm_2',
#                         'ctl_surgery_ti_1_fresh_id':barcode_id_list[0],
#                         'ctl_surgery_ti_1_fixed_id':barcode_id_list[1],
#                         'ctl_surgery_ti_1_frozen_id':barcode_id_list[2],
#                         'ctl_surgery_ti_2_fresh_id':barcode_id_list[3],
#                         'ctl_surgery_ti_2_fixed_id':barcode_id_list[4],
#                         'ctl_surgery_ti_2_frozen_id':barcode_id_list[5],
#                         'ctl_surgery_ti_3_fresh_id':barcode_id_list[6],
#                         'ctl_surgery_ti_3_fixed_id':barcode_id_list[7],
#                         'ctl_surgery_ti_3_frozen_id':barcode_id_list[8],
#                         'ctl_surgery_ac_4_fresh_id':barcode_id_list[9],
#                         'ctl_surgery_ac_4_fixed_id':barcode_id_list[10],
#                         'ctl_surgery_ac_4_frozen_id':barcode_id_list[11],
#                         'ctl_surgery_ac_5_fresh_id':barcode_id_list[12],
#                         'ctl_surgery_ac_5_fixed_id':barcode_id_list[13],
#                         'ctl_surgery_ac_5_frozen_id':barcode_id_list[14],
#                         'ctl_surgery_ac_6_fresh_id':barcode_id_list[15],
#                         'ctl_surgery_ac_6_fixed_id':barcode_id_list[16],
#                         'ctl_surgery_ac_6_frozen_id':barcode_id_list[17],
#                         'ctl_surgery_ac_7_fresh_id':barcode_id_list[18],
#                         'ctl_surgery_ac_7_fixed_id':barcode_id_list[19],
#                         'ctl_surgery_ac_7_frozen_id':barcode_id_list[20],
#                         'ctl_surgery_ac_8_fresh_id':barcode_id_list[21],
#                         'ctl_surgery_ac_8_fixed_id':barcode_id_list[22],
#                         'ctl_surgery_ac_8_frozen_id':barcode_id_list[23],
#                         'ctl_surg_biopsy_id_1':barcode_id_list[2],
#                         'ctl_surg_biopsy_id_2':barcode_id_list[5],
#                         'ctl_surg_biopsy_id_3':barcode_id_list[8],
#                         'ctl_surg_biopsy_id_4':barcode_id_list[11],
#                         'ctl_surg_biopsy_id_5':barcode_id_list[14],
#                         'ctl_surg_biopsy_id_6':barcode_id_list[17],
#                         'ctl_surg_biopsy_id_7':barcode_id_list[20],
#                         'ctl_surg_biopsy_id_8':barcode_id_list[23],
#                         'second_frozen': '1',
#                         'ti_add_frozen_a_id': barcode_id_list[24],
#                         'ti_add_frozen_b_id': barcode_id_list[25],
#                         'ac_add_frozen_a_id': barcode_id_list[26],
#                         'ac_add_frozen_b_id': barcode_id_list[27],
#                         'cd_endo_add_ti_a_id': barcode_id_list[24],
#                         'cd_endo_add_ti_b_id': barcode_id_list[25],
#                         'cd_endo_add_ac_a_id': barcode_id_list[26],
#                         'cd_endo_add_ac_b_id': barcode_id_list[27]}]
#         response = self.project.import_records(to_import)
#         return True
    
#     def update_REDCAP_SOPHIE_EXTRA_FROZEN(self,study_type,subject_id,barcode_id_list, custom_option):
#         # if is not needed actually...
#         # Since sophie use same variables... we only have one function then....once find subject
#         if custom_option == 'Need extra FROZEN specimens' or custom_option == 'No FRESH specimens, ADD extra FROZEN specimens':
#             if study_type == 'CD_ENDO':
#                 to_import = [{'record_id_dem_endo':subject_id,
#                           'redcap_event_name':'cd_arm_1',
#                           'second_frozen': '1',
#                           'ti_add_frozen_a_id': barcode_id_list[0],
#                           'ti_add_frozen_b_id': barcode_id_list[1],
#                           'ac_add_frozen_a_id': barcode_id_list[2],
#                           'ac_add_frozen_b_id': barcode_id_list[3],
#                           'cd_endo_add_ti_a_id': barcode_id_list[0],
#                           'cd_endo_add_ti_b_id': barcode_id_list[1],
#                           'cd_endo_add_ac_a_id': barcode_id_list[2],
#                           'cd_endo_add_ac_b_id': barcode_id_list[3]}]
        
#                 response = self.project.import_records(to_import)
#                 return True
#             elif study_type == 'CTL_ENDO':
#                 to_import = [{'record_id_dem_endo':subject_id,
#                               'redcap_event_name':'control_arm_1',
#                           'second_frozen': '1',
#                           'ti_add_frozen_a_id': barcode_id_list[0],
#                           'ti_add_frozen_b_id': barcode_id_list[1],
#                           'ac_add_frozen_a_id': barcode_id_list[2],
#                           'ac_add_frozen_b_id': barcode_id_list[3],
#                           'cd_endo_add_ti_a_id': barcode_id_list[0],
#                           'cd_endo_add_ti_b_id': barcode_id_list[1],
#                           'cd_endo_add_ac_a_id': barcode_id_list[2],
#                           'cd_endo_add_ac_b_id': barcode_id_list[3]}]
        
#                 response = self.project.import_records(to_import)
#                 return True
#             elif study_type == 'CD_Surgery':
#                 to_import = [{'record_id_dem_endo':subject_id,
#                               'redcap_event_name':'cd_arm_2',
#                           'second_frozen': '1',
#                           'ti_add_frozen_a_id': barcode_id_list[0],
#                           'ti_add_frozen_b_id': barcode_id_list[1],
#                           'ac_add_frozen_a_id': barcode_id_list[2],
#                           'ac_add_frozen_b_id': barcode_id_list[3],
#                           'cd_endo_add_ti_a_id': barcode_id_list[0],
#                           'cd_endo_add_ti_b_id': barcode_id_list[1],
#                           'cd_endo_add_ac_a_id': barcode_id_list[2],
#                           'cd_endo_add_ac_b_id': barcode_id_list[3]}]
        
#                 response = self.project.import_records(to_import)
#                 return True
#             elif study_type == 'CTL_Surgery':
#                 to_import = [{'record_id_dem_endo':subject_id,
#                               'redcap_event_name':'control_arm_2',
#                           'second_frozen': '1',
#                           'ti_add_frozen_a_id': barcode_id_list[0],
#                           'ti_add_frozen_b_id': barcode_id_list[1],
#                           'ac_add_frozen_a_id': barcode_id_list[2],
#                           'ac_add_frozen_b_id': barcode_id_list[3],
#                           'cd_endo_add_ti_a_id': barcode_id_list[0],
#                           'cd_endo_add_ti_b_id': barcode_id_list[1],
#                           'cd_endo_add_ac_a_id': barcode_id_list[2],
#                           'cd_endo_add_ac_b_id': barcode_id_list[3]}]
        
#                 response = self.project.import_records(to_import)
#                 return True
            
#         return False         
        
#     def update_REDCAP_SOPHIE_EXTRA_SERUM(self,study_type,subject_id,barcode_id_list, custom_option):
#         # if is not needed actually...
#         # Since sophie use same variables... we only have one function then....once find subject
#         if study_type == 'CD_ENDO' :
#             to_import = [{'record_id_dem_endo':subject_id,
#                           'redcap_event_name':'cd_arm_1',
#                           'specimen_serum_al_500':'7',
#                           'specimen_serum_al_500_5':barcode_id_list[0],
#                           'specimen_serum_al_500_6':barcode_id_list[1],
#                           'specimen_serum_al_500_7':barcode_id_list[2],}] 
        
#             response = self.project.import_records(to_import)
#             return True
#         elif study_type == 'CTL_ENDO':
#             to_import = [{'record_id_dem_endo':subject_id,
#                           'redcap_event_name':'control_arm_1',
#                           'specimen_serum_al_500':'7',
#                           'specimen_serum_al_500_5':barcode_id_list[0],
#                           'specimen_serum_al_500_6':barcode_id_list[1],
#                           'specimen_serum_al_500_7':barcode_id_list[2],}] 
        
#             response = self.project.import_records(to_import)
#             return True
        
          
              