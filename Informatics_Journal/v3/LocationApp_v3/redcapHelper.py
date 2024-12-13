import redcap
import pandas as pd
from collections import Counter

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from graphviz import Digraph
from datetime import datetime
import sys


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
        self.to_import_list = []
        self.to_import_list_overwrite = []
        print('?????1%s' % len(self.to_import_list_overwrite))
    
    def merge_two_dicts(self, dict1, dict2):
        return (dict2.update(dict1))
    
    def get_unique_import(self, to_import):
        
        tmpList = {}
        for elem in to_import:
            tmpKey = elem.get('record_id')
            if tmpKey in tmpList:
                tmpDict = tmpList.get(tmpKey)
                self.merge_two_dicts(elem, tmpDict) # python dict pointer behaviour
            else:
            # create a new dict
                tmpList[tmpKey] = elem

        final_to_import = []
        for key in tmpList:
            final_to_import.append(tmpList[key])

        return final_to_import

    # FOR CMA
    def redcap_import_records(self):
        # remove empty to_import....
        self.to_import_list = list(filter(None, self.to_import_list)) 
        self.to_import_list_overwrite = list(filter(None, self.to_import_list_overwrite)) 
        
        if len(self.to_import_list) > 0:
            for i in self.to_import_list:
                print(i)
            tmp_to_import_list = self.get_unique_import(self.to_import_list)
            response = self.project.import_records(tmp_to_import_list)
        if len(self.to_import_list_overwrite) > 0:
            print('?????2%s' % len(self.to_import_list_overwrite))
            for i in self.to_import_list_overwrite:
                print(i)
            tmp_to_import_list_overwrite = self.get_unique_import(self.to_import_list_overwrite)
            response_overwrite = self.project.import_records(tmp_to_import_list_overwrite,overwrite='overwrite')
        self.to_import_list = []
        self.to_import_list_overwrite = []
        
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
        return self.getRecordFromRedcap(['bccma_arm_1'],['record_id'])
        # return self.getRecordFromRedcap(['cd_arm_1','control_arm_1','cd_arm_2','control_arm_2','cancer_arm_2'],['record_id'])
    
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

    def getSubjectTypeViaLastestAction(self, barcode_id,subject_id):
        """
        fyi, (1) check if barcode exist,
        (2) if barcode exist, get subject type
        (3) since the option may change from "Default" to "Need Extra Frozen"
        (4) Skip scanned, otherwise the lateset could always be the 'scanned'...
        """    
        if self._tmp_subset is None:
            return False
        
        if len(self._tmp_subset) == 0:
#            print('!!!')
            return False
        
        data = pd.DataFrame.from_dict(self._tmp_subset)
        df = data.loc[data['barcode_sample_id'] == barcode_id]
        if len(df) == 0:
#            print('...')
            return False
        else:
            # result in 'action_tuple_table_arm_3','barcode_sample_id','barcode_custom_option'
            idx = len(self._tmp_subset)-1
            tmp_subject_type = ''
            tmp_action_type = ''
            while idx >= 0:
 #               print('redcap22222 %s' % str(tmp_subset[idx].get('barcode_sample_id')))
                tmp_subj = self._tmp_subset[idx].get('barcode_sample_id')[4:7] # CMA_xxx
                tmp_barcode = self._tmp_subset[idx].get('barcode_sample_id')
                if tmp_subj == subject_id and tmp_barcode == barcode_id:
                    
                    tmp_subject_type = self._tmp_subset[idx].get('barcode_subject_type')
                    tmp_action_type = self._tmp_subset[idx].get('barcode_action_type')
                    if tmp_action_type != 'scanned':
                        break # scanned is a necessary operation, and we don't know what exact operation has been done before or after scanned. 
                idx -= 1
            
            return tmp_subject_type
        




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
                tmp_subj = self._tmp_subset[idx].get('barcode_sample_id')[4:7] # CMA_xxx
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
            tmp_subj = tmp_subset[idx].get('barcode_sample_id')[4:7] 
            if tmp_subj == subject_id:
                tmp_custom_option = tmp_subset[idx].get('barcode_custom_option')
                if tmp_custom_option == 'Default' or tmp_custom_option == '':# or tmp_custom_option =='Need extra biopsies from TI':
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
            tmp_subj = tmp_subset[idx].get('barcode_sample_id')[4:7]
            if tmp_subj == subject_id:
                return tmp_subset[idx].get('barcode_custom_option') 
            idx -= 1
         
        return custom_option
            
    def getCurrentActionId(self):
        """
        fyi, get next available action id.
        """
        subset = self.getBarcodeSubset()
        print('######%s' % len(subset))
        if len(subset) > 0:
            curId = int(subset[len(subset)-1].get('record_id')[6:]) # remove action from actionxxxx
        else:
            curId = 0
        return curId
    
    def getNextAvailActionId(self):
        """
        fyi, get next available action id.
        """
        subset = self.getBarcodeSubset()
        curId = int(subset[len(subset)-1].get('record_id')[6:]) # remove action from actionxxxx
        nextAvailActionId = curId + 1
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
        to_import = {}
        if 'SR' in barcode_id: 
            aliquot_id = barcode_id[10:] #CMA_xxx_SR_1-11 xxxxx SR1, SR2, SR3, ... SR8
            
#        if action_comment == '':
            to_import = {'record_id': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_aliquot_id' : aliquot_id,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : action_type,
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}
        else:
            to_import = {'record_id': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : action_type,
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}
        #response = self.project.import_records(to_import)
        self.to_import_list.append(to_import)
        return True
    
    def destroyBarcodeCustomDate(self,actionId,barcode_id,studyType,processed_by,action_type, action_comment,ean8_code,custom_option,custom_date):
        """
        >> Add custom date for adding missing record in arm3
        action_type: 'Barcode destoryed'
        """
        # the only different is action_type...
        aliquot_id = ''
        to_import = {}
        if 'SR' in barcode_id: 
            aliquot_id = barcode_id[10:] # CMA_xxx_SR_1-11 #####SR1, SR2, SR3, ... SR8
            
#        if action_comment == '':
            to_import = {'record_id': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_aliquot_id' : aliquot_id,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : custom_date,
                          'barcode_action_type' : action_type,
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}
        else:
            to_import = {'record_id': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : custom_date,
                          'barcode_action_type' : action_type,
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}
#         response = self.project.import_records(to_import)
        self.to_import_list.append(to_import)
        return True
 

    def execLocationAppSync(self, actionId, barcode_id, studyType,processed_by,action_type,locationTuple,action_comment,ean8_code,custom_option,biopsies_type):
        """
        action_type: 'Serum stored in rack',
                     'Stool stored in rack', 
                     'Frozen stored in rack', 
                     'Fresh distributed to Lau',
                     'DNA distributed to Vantage. Relevant DNA field will be filled manually.',
                     'Fixed distributed to TPSR. Relevant Fixed specimen field will be filled manually.'
        """
        to_import = {}
        aliquot_id = ''
        if 'SR' in barcode_id: 
            # if 'SR10' in barcode_id or 'SR11' in barcode_id:
            #     aliquot_id = barcode_id[-2:] # SR10, SR11
            # else:
            #     aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8,SR9,
            aliquot_id = barcode_id[10:] # CMA_xxx_SR_1-11
            
#        if action_comment == '':
            to_import = {'record_id': 'action%s' % str(actionId),
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
                          'barcode_custom_option':custom_option}
        else:
            to_import = {'record_id': 'action%s' % str(actionId),
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
                          'barcode_custom_option':custom_option,
                          'barcode_frozen_type':biopsies_type}
#         response = self.project.import_records(to_import)
        self.to_import_list.append(to_import)
        return True
    
    # Looks like a customized function
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
        to_import = {}
        if 'SR' in barcode_id: 
            aliquot_id = barcode_id[10:] # CMA_xxx_SR_1-11 # SR1, SR2, SR3, ... SR8
            
#        if action_comment == '':
            to_import = {'record_id': 'action%s' % str(actionId),
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
                          'barcode_custom_option':custom_option}
        else:
            to_import = {'record_id': 'action%s' % str(actionId),
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
                          'barcode_custom_option':custom_option}
#         response = self.project.import_records(to_import)
        self.to_import_list.append(to_import)
        return True
      
    
    def setScannedAction(self, actionId, barcode_id,studyType,processed_by,action_comment,ean8_code,custom_option):
        """
        Set action: scanned
        If the barcode is serum, we need to set aliquot_id redcap field
        """
            
        aliquot_id = ''
        to_import = {}
        if 'SR' in barcode_id: 
            aliquot_id = barcode_id[10:] # CMA_xxx_SR_1-11 #### # SR1, SR2, SR3, ... SR8

#        if action_comment == '':
            to_import = {'record_id': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_aliquot_id' : aliquot_id,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : 'scanned',
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}
        else:
            to_import = {'record_id': 'action%s' % str(actionId),
                          'redcap_event_name': 'action_tuple_table_arm_3',
                          'barcode_sample_id': barcode_id,
                          'barcode_subject_type':studyType,
                          'barcode_processed_by': processed_by,
                          'barcode_action_date' : self.getCurrentTime(),
                          'barcode_action_type' : 'scanned',
                          'barcode_comment_note': action_comment,
                          'barcode_ean8_code': ean8_code,
                          'barcode_custom_option':custom_option}
#         response = self.project.import_records(to_import)
        self.to_import_list.append(to_import)
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
        
        # all six category share same design
        tmp_redcap_event_name = ''
        if study_type == 'CMA_PTSD':
            tmp_redcap_event_name = 'bccma_arm_1'
         
        to_import = {}
        if 'SR' in barcode_id:
            if 'SR_1' in barcode_id:
                if 'SR_10' in barcode_id:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'aliquot10_500ul_serum_10':'',                                  
                                    'freezer_serum_10':'',
                                    'rack_serum_10':'',
                                    'box_serum_10':'',
                                    'box_pos_serum_10':''}
                elif 'SR_11' in barcode_id:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'aliquot11_500ul_serum_11':'', 
                                    'freezer_serum_11':'',
                                    'rack_serum_11':'',
                                    'box_serum_11':'',
                                    'box_pos_serum_11':''}
                else: # should be SR1
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'aliquot1_100ul_serum_1':'',
                                    'freezer_serum_1':'',
                                    'rack_serum_1':'',
                                    'box_serum_1':'',
                                    'box_pos_serum_1':''}
            elif 'SR_2' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot2_100ul_serum_2':'',   
                                'freezer_serum_2':'',
                                'rack_serum_2':'',
                                'box_serum_2':'',
                                'box_pos_serum_2':''}
            elif 'SR_3' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot3_100ul_serum_3':'',   
                                'freezer_serum_3':'',
                                'rack_serum_3':'',
                                'box_serum_3':'',
                                'box_pos_serum_3':''}
            elif 'SR_4' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot4_100ul_serum_4':'',   
                                'freezer_serum_4':'',
                                'rack_serum_4':'',
                                'box_serum_4':'',
                                'box_pos_serum_4':''}

            elif 'SR_5' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot5_250ul_serum_5':'',   
                                'freezer_serum_5':'',
                                'rack_serum_5':'',
                                'box_serum_5':'',
                                'box_pos_serum_5':''}
            elif 'SR_6' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot6_250ul_serum_6':'',   
                                'freezer_serum_6':'',
                                'rack_serum_6':'',
                                'box_serum_6':'',
                                'box_pos_serum_6':''}
            elif 'SR_7' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot7_250ul_serum_7':'',   
                                'freezer_serum_7':'',
                                'rack_serum_7':'',
                                'box_serum_7':'',
                                'box_pos_serum_7':''}
            elif 'SR_8' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot8_250ul_serum_8':'',   
                                'freezer_serum_8':'',
                                'rack_serum_8':'',
                                'box_serum_8':'',
                                'box_pos_serum_8':''}
            elif 'SR_9' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot9_500ul_serum_9':'',   
                                'freezer_serum_9':'',
                                'rack_serum_9':'',
                                'box_serum_9':'',
                                'box_pos_serum_9':''}
        elif 'ST' in barcode_id:
            if 'ST_1' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'id_stool_1':'',   
                                'freezer_stool_1':'',
                                'rack_stool_1':'',
                                'box_stool_1':'',
                                'box_pos_stool_1':''}
            elif 'ST_2' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'id_stool_2':'',   
                                'freezer_stool_2':'',
                                'rack_stool_2':'',
                                'box_stool_2':'',
                                'box_pos_stool_2':''}
            elif 'ST_3' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'id_stool_3':'',   
                                'freezer_stool_3':'',
                                'rack_stool_3':'',
                                'box_stool_3':'',
                                'box_pos_stool_3':''}
            elif 'ST_4' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'id_stool_4':'',   
                                'freezer_stool_4':'',
                                'rack_stool_4':'',
                                'box_stool_4':'',
                                'box_pos_stool_4':''}
        elif 'Fresh' in barcode_id: 
            # for fresh biopsies, we don't know what is collected beforehand. so nothing information is recorded. We just need to mark a not collected.
            if 'Fresh_TI' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biop_fresh_ti___1':'0',
                                'biop_fresh_ti___2':'0',
                                'biop_fresh_ti___3':'0',
                                'biop_fresh_ti___4':'0',
                                'biop_fresh_ti___5':'0',
                                'biop_fresh_ti___6':'0',
                                'biop_fresh_ti___7':'0'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,   
            else: # it should be just Fresh
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biop_fresh___1':'0',
                                'biop_fresh___2':'0',
                                'biop_fresh___3':'0',
                                'biop_fresh___4':'0',
                                'biop_fresh___5':'0',
                                'biop_fresh___6':'0',
                                'biop_fresh___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,   
        elif 'Fixed' in barcode_id: 
            # for fresh biopsies, we don't know what is collected beforehand. so nothing information is recorded. We just need to mark a not collected.
            if 'Fixed_TI' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biop_fixed_ti___1':'0',
                                'biop_fixed_ti___2':'0',
                                'biop_fixed_ti___3':'0',
                                'biop_fixed_ti___4':'0',
                                'biop_fixed_ti___5':'0',
                                'biop_fixed_ti___6':'0',
                                'biop_fixed_ti___7':'0'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,   
            else: # it should be just Fixed
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biop_fixed___1':'0',
                                'biop_fixed___2':'0',
                                'biop_fixed___3':'0',
                                'biop_fixed___4':'0',
                                'biop_fixed___5':'0',
                                'biop_fixed___6':'0',
                                'biop_fixed___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
        elif 'Frozen' in barcode_id: 
            # for fresh biopsies, we don't know what is collected beforehand. so nothing information is recorded. We just need to mark a not collected.
            if 'Frozen_TI' in barcode_id:
                                    
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_addfrozen_ti': '',
                                'biopsy_id_frozen_ti': '',
                                'freezer_frozen_ti':'',
                                'box_frozen_ti':'',
                                'rack_frozen_ti': '',
                                'box_pos_frozen_ti':'',
                                'biop_frz_ti___1':'0',
                                'biop_frz_ti___2':'0',
                                'biop_frz_ti___3':'0',
                                'biop_frz_ti___4':'0',
                                'biop_frz_ti___5':'0',
                                'biop_frz_ti___6':'0',
                                'biop_frz_ti___7':'0'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,  
            elif 'Frozen_1' in  barcode_id:
                if 'Frozen_10'  in  barcode_id:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_10_id_ti': '',
                                'biopsy_frozen_10_id_rc': '',
                                'biopsy_frozen_10_id_tc': '',
                                'biopsy_frozen_10_id_lc': '',
                                'biopsy_frozen_10_id_sc': '',
                                'biopsy_frozen_10_id_r': '',
                                'biopsy_id_frozen_10': '',
                                'freezer_frozen_10':'',
                                'box_frozen_10':'',
                                'rack_frozen_10': '',
                                'box_pos_frozen_10':'',
                                'biop_frz_10___1':'0',
                                'biop_frz_10___2':'0',
                                'biop_frz_10___3':'0',
                                'biop_frz_10___4':'0',
                                'biop_frz_10___5':'0',
                                'biop_frz_10___6':'0',
                                'biop_frz_10___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected, 
                else: # it should be Frozen_1 then.
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_1_id_ti': '',
                                'biopsy_frozen_1_id_rc': '',
                                'biopsy_frozen_1_id_tc': '',
                                'biopsy_frozen_1_id_lc': '',
                                'biopsy_frozen_1_id_sc': '',
                                'biopsy_frozen_1_id_r': '',
                                'biopsy_id_frozen_1': '',
                                'freezer_frozen_1':'',
                                'box_frozen_1':'',
                                'rack_frozen_1': '',
                                'box_pos_frozen_1':'',
                                'biop_frz_1___1':'0',
                                'biop_frz_1___2':'0',
                                'biop_frz_1___3':'0',
                                'biop_frz_1___4':'0',
                                'biop_frz_1___5':'0',
                                'biop_frz_1___6':'0',
                                'biop_frz_1___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected, 
            elif 'Frozen_2' in  barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_2_id_ti': '',
                                'biopsy_frozen_2_id_rc': '',
                                'biopsy_frozen_2_id_tc': '',
                                'biopsy_frozen_2_id_lc': '',
                                'biopsy_frozen_2_id_sc': '',
                                'biopsy_frozen_2_id_r': '',
                                'biopsy_id_frozen_2': '',
                                'freezer_frozen_2':'',
                                'box_frozen_2':'',
                                'rack_frozen_2': '',
                                'box_pos_frozen_2':'',
                                'biop_frz_2___1':'0',
                                'biop_frz_2___2':'0',
                                'biop_frz_2___3':'0',
                                'biop_frz_2___4':'0',
                                'biop_frz_2___5':'0',
                                'biop_frz_2___6':'0',
                                'biop_frz_2___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
            elif 'Frozen_3' in  barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_3_id_ti': '',
                                'biopsy_frozen_3_id_rc': '',
                                'biopsy_frozen_3_id_tc': '',
                                'biopsy_frozen_3_id_lc': '',
                                'biopsy_frozen_3_id_sc': '',
                                'biopsy_frozen_3_id_r': '',
                                'biopsy_id_frozen_3': '',
                                'freezer_frozen_3':'',
                                'box_frozen_3':'',
                                'rack_frozen_3': '',
                                'box_pos_frozen_3':'',
                                'biop_frz_3___1':'0',
                                'biop_frz_3___2':'0',
                                'biop_frz_3___3':'0',
                                'biop_frz_3___4':'0',
                                'biop_frz_3___5':'0',
                                'biop_frz_3___6':'0',
                                'biop_frz_3___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,  
            elif 'Frozen_4' in  barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_4_id_ti': '',
                                'biopsy_frozen_4_id_rc': '',
                                'biopsy_frozen_4_id_tc': '',
                                'biopsy_frozen_4_id_lc': '',
                                'biopsy_frozen_4_id_sc': '',
                                'biopsy_frozen_4_id_r': '',
                                'biopsy_id_frozen_4': '',
                                'freezer_frozen_4':'',
                                'box_frozen_4':'',
                                'rack_frozen_4': '',
                                'box_pos_frozen_4':'',
                                'biop_frz_4___1':'0',
                                'biop_frz_4___2':'0',
                                'biop_frz_4___3':'0',
                                'biop_frz_4___4':'0',
                                'biop_frz_4___5':'0',
                                'biop_frz_4___6':'0',
                                'biop_frz_4___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
            elif 'Frozen_5' in  barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_5_id_ti': '',
                                'biopsy_frozen_5_id_rc': '',
                                'biopsy_frozen_5_id_tc': '',
                                'biopsy_frozen_5_id_lc': '',
                                'biopsy_frozen_5_id_sc': '',
                                'biopsy_frozen_5_id_r': '',
                                'biopsy_id_frozen_5': '',
                                'freezer_frozen_5':'',
                                'box_frozen_5':'',
                                'rack_frozen_5': '',
                                'box_pos_frozen_5':'',
                                'biop_frz_5___1':'0',
                                'biop_frz_5___2':'0',
                                'biop_frz_5___3':'0',
                                'biop_frz_5___4':'0',
                                'biop_frz_5___5':'0',
                                'biop_frz_5___6':'0',
                                'biop_frz_5___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
            elif 'Frozen_6' in  barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_6_id_ti': '',
                                'biopsy_frozen_6_id_rc': '',
                                'biopsy_frozen_6_id_tc': '',
                                'biopsy_frozen_6_id_lc': '',
                                'biopsy_frozen_6_id_sc': '',
                                'biopsy_frozen_6_id_r': '',
                                'biopsy_id_frozen_6': '',
                                'freezer_frozen_6':'',
                                'box_frozen_6':'',
                                'rack_frozen_6': '',
                                'box_pos_frozen_6':'',
                                'biop_frz_6___1':'0',
                                'biop_frz_6___2':'0',
                                'biop_frz_6___3':'0',
                                'biop_frz_6___4':'0',
                                'biop_frz_6___5':'0',
                                'biop_frz_6___6':'0',
                                'biop_frz_6___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
            elif 'Frozen_7' in  barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_7_id_ti': '',
                                'biopsy_frozen_7_id_rc': '',
                                'biopsy_frozen_7_id_tc': '',
                                'biopsy_frozen_7_id_lc': '',
                                'biopsy_frozen_7_id_sc': '',
                                'biopsy_frozen_7_id_r': '',
                                'biopsy_id_frozen_7': '',
                                'freezer_frozen_7':'',
                                'box_frozen_7':'',
                                'rack_frozen_7': '',
                                'box_pos_frozen_7':'',
                                'biop_frz_7___1':'0',
                                'biop_frz_7___2':'0',
                                'biop_frz_7___3':'0',
                                'biop_frz_7___4':'0',
                                'biop_frz_7___5':'0',
                                'biop_frz_7___6':'0',
                                'biop_frz_7___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,  
            elif 'Frozen_8' in  barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_8_id_ti': '',
                                'biopsy_frozen_8_id_rc': '',
                                'biopsy_frozen_8_id_tc': '',
                                'biopsy_frozen_8_id_lc': '',
                                'biopsy_frozen_8_id_sc': '',
                                'biopsy_frozen_8_id_r': '',
                                'biopsy_id_frozen_8': '',
                                'freezer_frozen_8':'',
                                'box_frozen_8':'',
                                'rack_frozen_8': '',
                                'box_pos_frozen_8':'',
                                'biop_frz_8___1':'0',
                                'biop_frz_8___2':'0',
                                'biop_frz_8___3':'0',
                                'biop_frz_8___4':'0',
                                'biop_frz_8___5':'0',
                                'biop_frz_8___6':'0',
                                'biop_frz_8___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
            elif 'Frozen_9' in  barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_9_id_ti': '',
                                'biopsy_frozen_9_id_rc': '',
                                'biopsy_frozen_9_id_tc': '',
                                'biopsy_frozen_9_id_lc': '',
                                'biopsy_frozen_9_id_sc': '',
                                'biopsy_frozen_9_id_r': '',
                                'biopsy_id_frozen_9': '',
                                'freezer_frozen_9':'',
                                'box_frozen_9':'',
                                'rack_frozen_9': '',
                                'box_pos_frozen_9':'',
                                'biop_frz_9___1':'0',
                                'biop_frz_9___2':'0',
                                'biop_frz_9___3':'0',
                                'biop_frz_9___4':'0',
                                'biop_frz_9___5':'0',
                                'biop_frz_9___6':'0',
                                'biop_frz_9___7':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,  
#         response = self.project.import_records(to_import,overwrite='overwrite')
        self.to_import_list_overwrite.append(to_import)
        print('?????3%s' % len(self.to_import_list_overwrite))
        return True 
    
# 
                              
    def update_REDCAP_SOPHIE_FROM_LOCATION_APP(self,subject_id,barcode_id, study_type, loc_tuple, biopsies_type):
        tmp_redcap_event_name = ''
        if study_type == 'CMA_PTSD':
            tmp_redcap_event_name = 'bccma_arm_1'
        # if study_type == 'UC_ENDO':
        #     tmp_redcap_event_name = 'uc_arm_1'
        # elif study_type == 'CD_ENDO':
        #     tmp_redcap_event_name = 'cd_arm_1'
        # elif study_type == 'CTL_ENDO':
        #     tmp_redcap_event_name = 'control_arm_1'
        # elif study_type == 'UC_Surgery':
        #     tmp_redcap_event_name = 'uc_arm_2'
        # elif study_type == 'CD_Surgery':
        #     tmp_redcap_event_name = 'cd_arm_2'
        # elif study_type == 'CTL_Surgery':
        #     tmp_redcap_event_name = 'control_arm_2'
        # elif study_type == 'Cancer_Surgery':
        #     tmp_redcap_event_name = 'cancer_arm_2'
           
        to_import = {}
        if 'SR' in barcode_id:
            if 'SR_1' in barcode_id:
                if 'SR_10' in barcode_id:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'aliquot10_500ul_serum_10':barcode_id,                                  
                                    'freezer_serum_10':loc_tuple[1],
                                    'rack_serum_10':loc_tuple[2],
                                    'box_serum_10':loc_tuple[3],
                                    'box_pos_serum_10':loc_tuple[4]}
                elif 'SR_11' in barcode_id:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'aliquot11_500ul_serum_11':barcode_id, 
                                    'freezer_serum_11':loc_tuple[1],
                                    'rack_serum_11':loc_tuple[2],
                                    'box_serum_11':loc_tuple[3],
                                    'box_pos_serum_11':loc_tuple[4]}
                else: # should be SR1
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'aliquot1_100ul_serum_1':barcode_id,
                                    'freezer_serum_1':loc_tuple[1],
                                    'rack_serum_1':loc_tuple[2],
                                    'box_serum_1':loc_tuple[3],
                                    'box_pos_serum_1':loc_tuple[4]}
            elif 'SR_2' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot2_100ul_serum_2':barcode_id,   
                                'freezer_serum_2':loc_tuple[1],
                                'rack_serum_2':loc_tuple[2],
                                'box_serum_2':loc_tuple[3],
                                'box_pos_serum_2':loc_tuple[4]}
            elif 'SR_3' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot3_100ul_serum_3':barcode_id,   
                                'freezer_serum_3':loc_tuple[1],
                                'rack_serum_3':loc_tuple[2],
                                'box_serum_3':loc_tuple[3],
                                'box_pos_serum_3':loc_tuple[4]}
            elif 'SR_4' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot4_100ul_serum_4':barcode_id,   
                                'freezer_serum_4':loc_tuple[1],
                                'rack_serum_4':loc_tuple[2],
                                'box_serum_4':loc_tuple[3],
                                'box_pos_serum_4':loc_tuple[4]}

            elif 'SR_5' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot5_250ul_serum_5':barcode_id,   
                                'freezer_serum_5':loc_tuple[1],
                                'rack_serum_5':loc_tuple[2],
                                'box_serum_5':loc_tuple[3],
                                'box_pos_serum_5':loc_tuple[4]}
            elif 'SR_6' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot6_250ul_serum_6':barcode_id,   
                                'freezer_serum_6':loc_tuple[1],
                                'rack_serum_6':loc_tuple[2],
                                'box_serum_6':loc_tuple[3],
                                'box_pos_serum_6':loc_tuple[4]}
            elif 'SR_7' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot7_250ul_serum_7':barcode_id,   
                                'freezer_serum_7':loc_tuple[1],
                                'rack_serum_7':loc_tuple[2],
                                'box_serum_7':loc_tuple[3],
                                'box_pos_serum_7':loc_tuple[4]}
            elif 'SR_8' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot8_250ul_serum_8':barcode_id,   
                                'freezer_serum_8':loc_tuple[1],
                                'rack_serum_8':loc_tuple[2],
                                'box_serum_8':loc_tuple[3],
                                'box_pos_serum_8':loc_tuple[4]}
            elif 'SR_9' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'aliquot9_500ul_serum_9':barcode_id,   
                                'freezer_serum_9':loc_tuple[1],
                                'rack_serum_9':loc_tuple[2],
                                'box_serum_9':loc_tuple[3],
                                'box_pos_serum_9':loc_tuple[4]}
        elif 'ST' in barcode_id:
            if 'ST_1' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'id_stool_1':barcode_id,   
                                'freezer_stool_1':loc_tuple[1],
                                'rack_stool_1':loc_tuple[2],
                                'box_stool_1':loc_tuple[3],
                                'box_pos_stool_1':loc_tuple[4]}
            elif 'ST_2' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'id_stool_2':barcode_id,   
                                'freezer_stool_2':loc_tuple[1],
                                'rack_stool_2':loc_tuple[2],
                                'box_stool_2':loc_tuple[3],
                                'box_pos_stool_2':loc_tuple[4]}
            elif 'ST_3' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'id_stool_3':barcode_id,   
                                'freezer_stool_3':loc_tuple[1],
                                'rack_stool_3':loc_tuple[2],
                                'box_stool_3':loc_tuple[3],
                                'box_pos_stool_3':loc_tuple[4]}
            elif 'ST_4' in barcode_id:
                to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'id_stool_4':barcode_id,   
                                'freezer_stool_4':loc_tuple[1],
                                'rack_stool_4':loc_tuple[2],
                                'box_stool_4':loc_tuple[3],
                                'box_pos_stool_4':loc_tuple[4]}
        elif 'Fresh' in barcode_id: 
            # for fresh biopsies, we don't know what is collected beforehand. so nothing information is recorded. We just need to mark a not collected.
            if 'Fresh_TI' in barcode_id:
                #"Terminal ileum - TI", 
                # #"Right colon - RC", 
                # #'Transverse colon - TC', 
                # #'Left colon - LC', 
                # #'Sigmoid colon - SC', 
                # #'Rectum - R'
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfresh_ti': barcode_id,
                                    'biop_fresh_ti___1':'1',
                                    'biop_fresh_ti___2':'0',
                                    'biop_fresh_ti___3':'0',
                                    'biop_fresh_ti___4':'0',
                                    'biop_fresh_ti___5':'0',
                                    'biop_fresh_ti___6':'0',
                                    'biop_fresh_ti___7':'0',
                                    'biop_ti_yn':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfresh_ti': barcode_id,
                                    'biop_fresh_ti___1':'0',
                                    'biop_fresh_ti___2':'1',
                                    'biop_fresh_ti___3':'0',
                                    'biop_fresh_ti___4':'0',
                                    'biop_fresh_ti___5':'0',
                                    'biop_fresh_ti___6':'0',
                                    'biop_fresh_ti___7':'0',
                                    'biop_ti_yn':'1'}
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfresh_ti': barcode_id,
                                    'biop_fresh_ti___1':'0',
                                    'biop_fresh_ti___2':'0',
                                    'biop_fresh_ti___3':'1',
                                    'biop_fresh_ti___4':'0',
                                    'biop_fresh_ti___5':'0',
                                    'biop_fresh_ti___6':'0',
                                    'biop_fresh_ti___7':'0',
                                    'biop_ti_yn':'1'}
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfresh_ti': barcode_id,
                                    'biop_fresh_ti___1':'0',
                                    'biop_fresh_ti___2':'0',
                                    'biop_fresh_ti___3':'0',
                                    'biop_fresh_ti___4':'1',
                                    'biop_fresh_ti___5':'0',
                                    'biop_fresh_ti___6':'0',
                                    'biop_fresh_ti___7':'0',
                                    'biop_ti_yn':'1'}
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfresh_ti': barcode_id,
                                    'biop_fresh_ti___1':'0',
                                    'biop_fresh_ti___2':'0',
                                    'biop_fresh_ti___3':'0',
                                    'biop_fresh_ti___4':'0',
                                    'biop_fresh_ti___5':'1',
                                    'biop_fresh_ti___6':'0',
                                    'biop_fresh_ti___7':'0',
                                    'biop_ti_yn':'1'}
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfresh_ti': barcode_id,
                                    'biop_fresh_ti___1':'0',
                                    'biop_fresh_ti___2':'0',
                                    'biop_fresh_ti___3':'0',
                                    'biop_fresh_ti___4':'0',
                                    'biop_fresh_ti___5':'0',
                                    'biop_fresh_ti___6':'1',
                                    'biop_fresh_ti___7':'0',
                                    'biop_ti_yn':'1'}   
            else: # it should be just Fresh
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fresh_id_ti': barcode_id,
                                    'biop_fresh___1':'1',
                                    'biop_fresh___2':'0',
                                    'biop_fresh___3':'0',
                                    'biop_fresh___4':'0',
                                    'biop_fresh___5':'0',
                                    'biop_fresh___6':'0',
                                    'biop_fresh___7':'0',
                                    } # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fresh_id_rc': barcode_id,
                                    'biop_fresh___1':'0',
                                    'biop_fresh___2':'1',
                                    'biop_fresh___3':'0',
                                    'biop_fresh___4':'0',
                                    'biop_fresh___5':'0',
                                    'biop_fresh___6':'0',
                                    'biop_fresh___7':'0'}
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fresh_tc': barcode_id,
                                    'biop_fresh___1':'0',
                                    'biop_fresh___2':'0',
                                    'biop_fresh___3':'1',
                                    'biop_fresh___4':'0',
                                    'biop_fresh___5':'0',
                                    'biop_fresh___6':'0',
                                    'biop_fresh___7':'0'}
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fresh_id_lc': barcode_id,
                                    'biop_fresh___1':'0',
                                    'biop_fresh___2':'0',
                                    'biop_fresh___3':'0',
                                    'biop_fresh___4':'1',
                                    'biop_fresh___5':'0',
                                    'biop_fresh___6':'0',
                                    'biop_fresh___7':'0'}
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fresh_id_sc': barcode_id,
                                    'biop_fresh___1':'0',
                                    'biop_fresh___2':'0',
                                    'biop_fresh___3':'0',
                                    'biop_fresh___4':'0',
                                    'biop_fresh___5':'1',
                                    'biop_fresh___6':'0',
                                    'biop_fresh___7':'0'}
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fresh_id_r': barcode_id,
                                    'biop_fresh___1':'0',
                                    'biop_fresh___2':'0',
                                    'biop_fresh___3':'0',
                                    'biop_fresh___4':'0',
                                    'biop_fresh___5':'0',
                                    'biop_fresh___6':'1',
                                    'biop_fresh___7':'0'}
        elif 'Fixed' in barcode_id: 
            # for fixed biopsies, we don't know what is collected beforehand. so nothing information is recorded. We just need to mark a not collected.
            if 'Fixed_TI' in barcode_id:
                #"Terminal ileum - TI", 
                # #"Right colon - RC", 
                # #'Transverse colon - TC', 
                # #'Left colon - LC', 
                # #'Sigmoid colon - SC', 
                # #'Rectum - R'
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfixed_ti': barcode_id,
                                    'biop_fixed_ti___1':'1',
                                    'biop_fixed_ti___2':'0',
                                    'biop_fixed_ti___3':'0',
                                    'biop_fixed_ti___4':'0',
                                    'biop_fixed_ti___5':'0',
                                    'biop_fixed_ti___6':'0',
                                    'biop_fixed_ti___7':'0',
                                    'biop_ti_yn':'1'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfixed_ti': barcode_id,
                                    'biop_fixed_ti___1':'0',
                                    'biop_fixed_ti___2':'1',
                                    'biop_fixed_ti___3':'0',
                                    'biop_fixed_ti___4':'0',
                                    'biop_fixed_ti___5':'0',
                                    'biop_fixed_ti___6':'0',
                                    'biop_fixed_ti___7':'0',
                                    'biop_ti_yn':'1'}
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfixed_ti': barcode_id,
                                    'biop_fixed_ti___1':'0',
                                    'biop_fixed_ti___2':'0',
                                    'biop_fixed_ti___3':'1',
                                    'biop_fixed_ti___4':'0',
                                    'biop_fixed_ti___5':'0',
                                    'biop_fixed_ti___6':'0',
                                    'biop_fixed_ti___7':'0',
                                    'biop_ti_yn':'1'}
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfixed_ti': barcode_id,
                                    'biop_fixed_ti___1':'0',
                                    'biop_fixed_ti___2':'0',
                                    'biop_fixed_ti___3':'0',
                                    'biop_fixed_ti___4':'1',
                                    'biop_fixed_ti___5':'0',
                                    'biop_fixed_ti___6':'0',
                                    'biop_fixed_ti___7':'0',
                                    'biop_ti_yn':'1'}
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfixed_ti': barcode_id,
                                    'biop_fixed_ti___1':'0',
                                    'biop_fixed_ti___2':'0',
                                    'biop_fixed_ti___3':'0',
                                    'biop_fixed_ti___4':'0',
                                    'biop_fixed_ti___5':'1',
                                    'biop_fixed_ti___6':'0',
                                    'biop_fixed_ti___7':'0',
                                    'biop_ti_yn':'1'}
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfixed_ti': barcode_id,
                                    'biop_fixed_ti___1':'0',
                                    'biop_fixed_ti___2':'0',
                                    'biop_fixed_ti___3':'0',
                                    'biop_fixed_ti___4':'0',
                                    'biop_fixed_ti___5':'0',
                                    'biop_fixed_ti___6':'1',
                                    'biop_fixed_ti___7':'0',
                                    'biop_ti_yn':'1'}   
            else: # it should be just Fixed
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fixed_id_ti': barcode_id,
                                    'biop_fixed___1':'1',
                                    'biop_fixed___2':'0',
                                    'biop_fixed___3':'0',
                                    'biop_fixed___4':'0',
                                    'biop_fixed___5':'0',
                                    'biop_fixed___6':'0',
                                    'biop_fixed___7':'0'} # 1, TI | 2, RC | 3, TC | 4, LC | 5, SC | 6, R | 7, not collected,
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fixed_id_rc': barcode_id,
                                    'biop_fixed___1':'0',
                                    'biop_fixed___2':'1',
                                    'biop_fixed___3':'0',
                                    'biop_fixed___4':'0',
                                    'biop_fixed___5':'0',
                                    'biop_fixed___6':'0',
                                    'biop_fixed___7':'0'}
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfixed_ti': barcode_id,
                                    'biop_fixed___1':'0',
                                    'biop_fixed___2':'0',
                                    'biop_fixed___3':'1',
                                    'biop_fixed___4':'0',
                                    'biop_fixed___5':'0',
                                    'biop_fixed___6':'0',
                                    'biop_fixed___7':'0'}
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fixed_id_tc': barcode_id,
                                    'biop_fixed___1':'0',
                                    'biop_fixed___2':'0',
                                    'biop_fixed___3':'0',
                                    'biop_fixed___4':'1',
                                    'biop_fixed___5':'0',
                                    'biop_fixed___6':'0',
                                    'biop_fixed___7':'0'}
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fixed_id_sc': barcode_id,
                                    'biop_fixed___1':'0',
                                    'biop_fixed___2':'0',
                                    'biop_fixed___3':'0',
                                    'biop_fixed___4':'0',
                                    'biop_fixed___5':'1',
                                    'biop_fixed___6':'0',
                                    'biop_fixed___7':'0'}
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_fixed_id_r': barcode_id,
                                    'biop_fixed___1':'0',
                                    'biop_fixed___2':'0',
                                    'biop_fixed___3':'0',
                                    'biop_fixed___4':'0',
                                    'biop_fixed___5':'0',
                                    'biop_fixed___6':'1',
                                    'biop_fixed___7':'0'}   
        elif 'Frozen' in barcode_id: 
            # for fresh biopsies, we don't know what is collected beforehand. so nothing information is recorded. We just need to mark a not collected.
            if 'Frozen_TI' in barcode_id:
                #"Terminal ileum - TI", 1
                # #"Right colon - RC", 2
                # #'Transverse colon - TC', 3 
                # #'Left colon - LC', 4
                # #'Sigmoid colon - SC', 5
                # #'Rectum - R' 6
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfrozen_ti': barcode_id,
                                    'biopsy_id_frozen_ti': barcode_id,
                                    'freezer_frozen_ti':loc_tuple[1],
                                    'rack_frozen_ti':loc_tuple[2],
                                    'box_frozen_ti': loc_tuple[3],
                                    'box_pos_frozen_ti':loc_tuple[4],
                                    'biop_frz_ti___1':'1',
                                    'biop_frz_ti___2':'0',
                                    'biop_frz_ti___3':'0',
                                    'biop_frz_ti___4':'0',
                                    'biop_frz_ti___5':'0',
                                    'biop_frz_ti___6':'0',
                                    'biop_frz_ti___7':'0',
                                    'biop_ti_yn':'1'
                                    }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfrozen_ti': barcode_id,
                                    'biopsy_id_frozen_ti': barcode_id,
                                    'freezer_frozen_ti':loc_tuple[1],
                                    'rack_frozen_ti':loc_tuple[2],
                                    'box_frozen_ti': loc_tuple[3],
                                    'box_pos_frozen_ti':loc_tuple[4],
                                    'biop_frz_ti___1':'0',
                                    'biop_frz_ti___2':'1',
                                    'biop_frz_ti___3':'0',
                                    'biop_frz_ti___4':'0',
                                    'biop_frz_ti___5':'0',
                                    'biop_frz_ti___6':'0',
                                    'biop_frz_ti___7':'0',
                                    'biop_ti_yn':'1',
                                    }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfrozen_ti': barcode_id,
                                    'biopsy_id_frozen_ti': barcode_id,
                                    'freezer_frozen_ti':loc_tuple[1],
                                    'rack_frozen_ti':loc_tuple[2],
                                    'box_frozen_ti': loc_tuple[3],
                                    'box_pos_frozen_ti':loc_tuple[4],
                                    'biop_frz_ti___1':'0',
                                    'biop_frz_ti___2':'0',
                                    'biop_frz_ti___3':'1',
                                    'biop_frz_ti___4':'0',
                                    'biop_frz_ti___5':'0',
                                    'biop_frz_ti___6':'0',
                                    'biop_frz_ti___7':'0',
                                    'biop_ti_yn':'1',
                                    }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfrozen_ti': barcode_id,
                                    'biopsy_id_frozen_ti': barcode_id,
                                    'freezer_frozen_ti':loc_tuple[1],
                                    'rack_frozen_ti':loc_tuple[2],
                                    'box_frozen_ti': loc_tuple[3],
                                    'box_pos_frozen_ti':loc_tuple[4],
                                    'biop_frz_ti___1':'0',
                                    'biop_frz_ti___2':'0',
                                    'biop_frz_ti___3':'0',
                                    'biop_frz_ti___4':'1',
                                    'biop_frz_ti___5':'0',
                                    'biop_frz_ti___6':'0',
                                    'biop_frz_ti___7':'0',
                                    'biop_ti_yn':'1',
                                    }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfrozen_ti': barcode_id,
                                    'biopsy_id_frozen_ti': barcode_id,
                                    'freezer_frozen_ti':loc_tuple[1],
                                    'rack_frozen_ti':loc_tuple[2],
                                    'box_frozen_ti': loc_tuple[3],
                                    'box_pos_frozen_ti':loc_tuple[4],
                                    'biop_frz_ti___1':'0',
                                    'biop_frz_ti___2':'0',
                                    'biop_frz_ti___3':'0',
                                    'biop_frz_ti___4':'0',
                                    'biop_frz_ti___5':'1',
                                    'biop_frz_ti___6':'0',
                                    'biop_frz_ti___7':'0',
                                    'biop_ti_yn':'1',
                                    }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_addfrozen_ti': barcode_id,
                                    'biopsy_id_frozen_ti': barcode_id,
                                    'freezer_frozen_ti':loc_tuple[1],
                                    'rack_frozen_ti':loc_tuple[2],
                                    'box_frozen_ti': loc_tuple[3],
                                    'box_pos_frozen_ti':loc_tuple[4],
                                    'biop_frz_ti___1':'0',
                                    'biop_frz_ti___2':'0',
                                    'biop_frz_ti___3':'0',
                                    'biop_frz_ti___4':'0',
                                    'biop_frz_ti___5':'0',
                                    'biop_frz_ti___6':'1',
                                    'biop_frz_ti___7':'0',
                                    'biop_ti_yn':'1',
                                    }
            elif 'Frozen_1' in  barcode_id:
                if 'Frozen_10'  in  barcode_id:
                    if 'Terminal ileum' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_10_id_ti': barcode_id,
                                    'biopsy_id_frozen_10': barcode_id,
                                    'freezer_frozen_10':loc_tuple[1],
                                    'rack_frozen_10':loc_tuple[2],
                                    'box_frozen_10': loc_tuple[3],
                                    'box_pos_frozen_10':loc_tuple[4],
                                    'biop_frz_10___1':'1',
                                    'biop_frz_10___2':'0',
                                    'biop_frz_10___3':'0',
                                    'biop_frz_10___4':'0',
                                    'biop_frz_10___5':'0',
                                    'biop_frz_10___6':'0',
                                    'biop_frz_10___7':'0'
                                    }
                    elif 'Right colon' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_10_id_rc': barcode_id,
                                    'biopsy_id_frozen_10': barcode_id,
                                    'freezer_frozen_10':loc_tuple[1],
                                    'rack_frozen_10':loc_tuple[2],
                                    'box_frozen_10': loc_tuple[3],
                                    'box_pos_frozen_10':loc_tuple[4],
                                    'biop_frz_10___1':'0',
                                    'biop_frz_10___2':'1',
                                    'biop_frz_10___3':'0',
                                    'biop_frz_10___4':'0',
                                    'biop_frz_10___5':'0',
                                    'biop_frz_10___6':'0',
                                    'biop_frz_10___7':'0'
                                    }
                    elif 'Transverse colon' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_10_id_tc': barcode_id,
                                    'biopsy_id_frozen_10': barcode_id,
                                    'freezer_frozen_10':loc_tuple[1],
                                    'rack_frozen_10':loc_tuple[2],
                                    'box_frozen_10': loc_tuple[3],
                                    'box_pos_frozen_10':loc_tuple[4],
                                    'biop_frz_10___1':'0',
                                    'biop_frz_10___2':'0',
                                    'biop_frz_10___3':'1',
                                    'biop_frz_10___4':'0',
                                    'biop_frz_10___5':'0',
                                    'biop_frz_10___6':'0',
                                    'biop_frz_10___7':'0'
                                    }
                    elif 'Left colon' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_10_id_lc': barcode_id,
                                    'biopsy_id_frozen_10': barcode_id,
                                    'freezer_frozen_10':loc_tuple[1],
                                    'rack_frozen_10':loc_tuple[2],
                                    'box_frozen_10': loc_tuple[3],
                                    'box_pos_frozen_10':loc_tuple[4],
                                    'biop_frz_10___1':'0',
                                    'biop_frz_10___2':'0',
                                    'biop_frz_10___3':'0',
                                    'biop_frz_10___4':'1',
                                    'biop_frz_10___5':'0',
                                    'biop_frz_10___6':'0',
                                    'biop_frz_10___7':'0'
                                    }
                    elif 'Sigmoid colon' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_10_id_sc': barcode_id,
                                    'biopsy_id_frozen_10': barcode_id,
                                    'freezer_frozen_10':loc_tuple[1],
                                    'rack_frozen_10':loc_tuple[2],
                                    'box_frozen_10': loc_tuple[3],
                                    'box_pos_frozen_10':loc_tuple[4],
                                    'biop_frz_10___1':'0',
                                    'biop_frz_10___2':'0',
                                    'biop_frz_10___3':'0',
                                    'biop_frz_10___4':'0',
                                    'biop_frz_10___5':'1',
                                    'biop_frz_10___6':'0',
                                    'biop_frz_10___7':'0'
                                    }
                    elif 'Rectum' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_10_id_r': barcode_id,
                                    'biopsy_id_frozen_10': barcode_id,
                                    'freezer_frozen_10':loc_tuple[1],
                                    'rack_frozen_10':loc_tuple[2],
                                    'box_frozen_10': loc_tuple[3],
                                    'box_pos_frozen_10':loc_tuple[4],
                                    'biop_frz_10___1':'0',
                                    'biop_frz_10___2':'0',
                                    'biop_frz_10___3':'0',
                                    'biop_frz_10___4':'0',
                                    'biop_frz_10___5':'0',
                                    'biop_frz_10___6':'1',
                                    'biop_frz_10___7':'0'
                                    }  
                else: # should be Frozen_1
                    if 'Terminal ileum' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_1_id_ti': barcode_id,
                                    'biopsy_id_frozen_1': barcode_id,
                                    'freezer_frozen_1':loc_tuple[1],
                                    'rack_frozen_1':loc_tuple[2],
                                    'box_frozen_1': loc_tuple[3],
                                    'box_pos_frozen_1':loc_tuple[4],
                                    'biop_frz_1___1':'1',
                                    'biop_frz_1___2':'0',
                                    'biop_frz_1___3':'0',
                                    'biop_frz_1___4':'0',
                                    'biop_frz_1___5':'0',
                                    'biop_frz_1___6':'0',
                                    'biop_frz_1___7':'0'
                                    }
                    elif 'Right colon' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_1_id_rc': barcode_id,
                                    'biopsy_id_frozen_1': barcode_id,
                                    'freezer_frozen_1':loc_tuple[1],
                                    'rack_frozen_1':loc_tuple[2],
                                    'box_frozen_1': loc_tuple[3],
                                    'box_pos_frozen_1':loc_tuple[4],
                                    'biop_frz_1___1':'0',
                                    'biop_frz_1___2':'1',
                                    'biop_frz_1___3':'0',
                                    'biop_frz_1___4':'0',
                                    'biop_frz_1___5':'0',
                                    'biop_frz_1___6':'0',
                                    'biop_frz_1___7':'0'
                                    }
                    elif 'Transverse colon' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_1_id_tc': barcode_id,
                                    'biopsy_id_frozen_1': barcode_id,
                                    'freezer_frozen_1':loc_tuple[1],
                                    'rack_frozen_1':loc_tuple[2],
                                    'box_frozen_1': loc_tuple[3],
                                    'box_pos_frozen_1':loc_tuple[4],
                                    'biop_frz_1___1':'0',
                                    'biop_frz_1___2':'0',
                                    'biop_frz_1___3':'1',
                                    'biop_frz_1___4':'0',
                                    'biop_frz_1___5':'0',
                                    'biop_frz_1___6':'0',
                                    'biop_frz_1___7':'0'
                                    }
                    elif 'Left colon' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_1_id_lc': barcode_id,
                                    'biopsy_id_frozen_1': barcode_id,
                                    'freezer_frozen_1':loc_tuple[1],
                                    'rack_frozen_1':loc_tuple[2],
                                    'box_frozen_1': loc_tuple[3],
                                    'box_pos_frozen_1':loc_tuple[4],
                                    'biop_frz_1___1':'0',
                                    'biop_frz_1___2':'0',
                                    'biop_frz_1___3':'0',
                                    'biop_frz_1___4':'1',
                                    'biop_frz_1___5':'0',
                                    'biop_frz_1___6':'0',
                                    'biop_frz_1___7':'0'
                                    }
                    elif 'Sigmoid colon' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_1_id_sc': barcode_id,
                                    'biopsy_id_frozen_1': barcode_id,
                                    'freezer_frozen_1':loc_tuple[1],
                                    'rack_frozen_1':loc_tuple[2],
                                    'box_frozen_1': loc_tuple[3],
                                    'box_pos_frozen_1':loc_tuple[4],
                                    'biop_frz_1___1':'0',
                                    'biop_frz_1___2':'0',
                                    'biop_frz_1___3':'0',
                                    'biop_frz_1___4':'0',
                                    'biop_frz_1___5':'1',
                                    'biop_frz_1___6':'0',
                                    'biop_frz_1___7':'0'
                                    }
                    elif 'Rectum' in biopsies_type:
                        to_import = {'record_id':subject_id,
                                    'redcap_event_name':tmp_redcap_event_name,
                                    'biopsy_frozen_1_id_r': barcode_id,
                                    'biopsy_id_frozen_1': barcode_id,
                                    'freezer_frozen_1':loc_tuple[1],
                                    'rack_frozen_1':loc_tuple[2],
                                    'box_frozen_1': loc_tuple[3],
                                    'box_pos_frozen_1':loc_tuple[4],
                                    'biop_frz_1___1':'0',
                                    'biop_frz_1___2':'0',
                                    'biop_frz_1___3':'0',
                                    'biop_frz_1___4':'0',
                                    'biop_frz_1___5':'0',
                                    'biop_frz_1___6':'1',
                                    'biop_frz_1___7':'0'
                                    }
            elif 'Frozen_2' in  barcode_id:  
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_2_id_ti': barcode_id,
                                'biopsy_id_frozen_2': barcode_id,
                                'freezer_frozen_2':loc_tuple[1],
                                'rack_frozen_2':loc_tuple[2],
                                'box_frozen_2': loc_tuple[3],
                                'box_pos_frozen_2':loc_tuple[4],
                                'biop_frz_2___1':'1',
                                'biop_frz_2___2':'0',
                                'biop_frz_2___3':'0',
                                'biop_frz_2___4':'0',
                                'biop_frz_2___5':'0',
                                'biop_frz_2___6':'0',
                                'biop_frz_2___7':'0'
                                }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_2_id_rc': barcode_id,
                                'biopsy_id_frozen_2': barcode_id,
                                'freezer_frozen_2':loc_tuple[1],
                                'rack_frozen_2':loc_tuple[2],
                                'box_frozen_2': loc_tuple[3],
                                'box_pos_frozen_2':loc_tuple[4],
                                'biop_frz_2___1':'0',
                                'biop_frz_2___2':'1',
                                'biop_frz_2___3':'0',
                                'biop_frz_2___4':'0',
                                'biop_frz_2___5':'0',
                                'biop_frz_2___6':'0',
                                'biop_frz_2___7':'0'
                                }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_2_id_tc': barcode_id,
                                'biopsy_id_frozen_2': barcode_id,
                                'freezer_frozen_2':loc_tuple[1],
                                'rack_frozen_2':loc_tuple[2],
                                'box_frozen_2': loc_tuple[3],
                                'box_pos_frozen_2':loc_tuple[4],
                                'biop_frz_2___1':'0',
                                'biop_frz_2___2':'0',
                                'biop_frz_2___3':'1',
                                'biop_frz_2___4':'0',
                                'biop_frz_2___5':'0',
                                'biop_frz_2___6':'0',
                                'biop_frz_2___7':'0'
                                }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_2_id_lc': barcode_id,
                                'biopsy_id_frozen_2': barcode_id,
                                'freezer_frozen_2':loc_tuple[1],
                                'rack_frozen_2':loc_tuple[2],
                                'box_frozen_2': loc_tuple[3],
                                'box_pos_frozen_2':loc_tuple[4],
                                'biop_frz_2___1':'0',
                                'biop_frz_2___2':'0',
                                'biop_frz_2___3':'0',
                                'biop_frz_2___4':'1',
                                'biop_frz_2___5':'0',
                                'biop_frz_2___6':'0',
                                'biop_frz_2___7':'0'
                                }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_2_id_sc': barcode_id,
                                'biopsy_id_frozen_2': barcode_id,
                                'freezer_frozen_2':loc_tuple[1],
                                'rack_frozen_2':loc_tuple[2],
                                'box_frozen_2': loc_tuple[3],
                                'box_pos_frozen_2':loc_tuple[4],
                                'biop_frz_2___1':'0',
                                'biop_frz_2___2':'0',
                                'biop_frz_2___3':'0',
                                'biop_frz_2___4':'0',
                                'biop_frz_2___5':'1',
                                'biop_frz_2___6':'0',
                                'biop_frz_2___7':'0'
                                }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_2_id_r': barcode_id,
                                'biopsy_id_frozen_2': barcode_id,
                                'freezer_frozen_2':loc_tuple[1],
                                'rack_frozen_2':loc_tuple[2],
                                'box_frozen_2': loc_tuple[3],
                                'box_pos_frozen_2':loc_tuple[4],
                                'biop_frz_2___1':'0',
                                'biop_frz_2___2':'0',
                                'biop_frz_2___3':'0',
                                'biop_frz_2___4':'0',
                                'biop_frz_2___5':'0',
                                'biop_frz_2___6':'1',
                                'biop_frz_2___7':'0'
                                }           
            elif 'Frozen_3' in  barcode_id:  
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_3_id_ti': barcode_id,
                                'biopsy_id_frozen_3': barcode_id,
                                'freezer_frozen_3':loc_tuple[1],
                                'rack_frozen_3':loc_tuple[2],
                                'box_frozen_3': loc_tuple[3],
                                'box_pos_frozen_3':loc_tuple[4],
                                'biop_frz_3___1':'1',
                                'biop_frz_3___2':'0',
                                'biop_frz_3___3':'0',
                                'biop_frz_3___4':'0',
                                'biop_frz_3___5':'0',
                                'biop_frz_3___6':'0',
                                'biop_frz_3___7':'0'
                                }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_3_id_rc': barcode_id,
                                'biopsy_id_frozen_3': barcode_id,
                                'freezer_frozen_3':loc_tuple[1],
                                'rack_frozen_3':loc_tuple[2],
                                'box_frozen_3': loc_tuple[3],
                                'box_pos_frozen_3':loc_tuple[4],
                                'biop_frz_3___1':'0',
                                'biop_frz_3___2':'1',
                                'biop_frz_3___3':'0',
                                'biop_frz_3___4':'0',
                                'biop_frz_3___5':'0',
                                'biop_frz_3___6':'0',
                                'biop_frz_3___7':'0'
                                }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_3_id_tc': barcode_id,
                                'biopsy_id_frozen_3': barcode_id,
                                'freezer_frozen_3':loc_tuple[1],
                                'rack_frozen_3':loc_tuple[2],
                                'box_frozen_3': loc_tuple[3],
                                'box_pos_frozen_3':loc_tuple[4],
                                'biop_frz_3___1':'0',
                                'biop_frz_3___2':'0',
                                'biop_frz_3___3':'1',
                                'biop_frz_3___4':'0',
                                'biop_frz_3___5':'0',
                                'biop_frz_3___6':'0',
                                'biop_frz_3___7':'0'
                                }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_3_id_lc': barcode_id,
                                'biopsy_id_frozen_3': barcode_id,
                                'freezer_frozen_3':loc_tuple[1],
                                'rack_frozen_3':loc_tuple[2],
                                'box_frozen_3': loc_tuple[3],
                                'box_pos_frozen_3':loc_tuple[4],
                                'biop_frz_3___1':'0',
                                'biop_frz_3___2':'0',
                                'biop_frz_3___3':'0',
                                'biop_frz_3___4':'1',
                                'biop_frz_3___5':'0',
                                'biop_frz_3___6':'0',
                                'biop_frz_3___7':'0'
                                }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_3_id_sc': barcode_id,
                                'biopsy_id_frozen_3': barcode_id,
                                'freezer_frozen_3':loc_tuple[1],
                                'rack_frozen_3':loc_tuple[2],
                                'box_frozen_3': loc_tuple[3],
                                'box_pos_frozen_3':loc_tuple[4],
                                'biop_frz_3___1':'0',
                                'biop_frz_3___2':'0',
                                'biop_frz_3___3':'0',
                                'biop_frz_3___4':'0',
                                'biop_frz_3___5':'1',
                                'biop_frz_3___6':'0',
                                'biop_frz_3___7':'0'
                                }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_3_id_r': barcode_id,
                                'biopsy_id_frozen_3': barcode_id,
                                'freezer_frozen_3':loc_tuple[1],
                                'rack_frozen_3':loc_tuple[2],
                                'box_frozen_3': loc_tuple[3],
                                'box_pos_frozen_3':loc_tuple[4],
                                'biop_frz_3___1':'0',
                                'biop_frz_3___2':'0',
                                'biop_frz_3___3':'0',
                                'biop_frz_3___4':'0',
                                'biop_frz_3___5':'0',
                                'biop_frz_3___6':'1',
                                'biop_frz_3___7':'0'
                                }
            elif 'Frozen_4' in  barcode_id:  
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_4_id_ti': barcode_id,
                                'biopsy_id_frozen_4': barcode_id,
                                'freezer_frozen_4':loc_tuple[1],
                                'rack_frozen_4':loc_tuple[2],
                                'box_frozen_4': loc_tuple[3],
                                'box_pos_frozen_4':loc_tuple[4],
                                'biop_frz_4___1':'1',
                                'biop_frz_4___2':'0',
                                'biop_frz_4___3':'0',
                                'biop_frz_4___4':'0',
                                'biop_frz_4___5':'0',
                                'biop_frz_4___6':'0',
                                'biop_frz_4___7':'0'
                                }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_4_id_rc': barcode_id,
                                'biopsy_id_frozen_4': barcode_id,
                                'freezer_frozen_4':loc_tuple[1],
                                'rack_frozen_4':loc_tuple[2],
                                'box_frozen_4': loc_tuple[3],
                                'box_pos_frozen_4':loc_tuple[4],
                                'biop_frz_4___1':'0',
                                'biop_frz_4___2':'1',
                                'biop_frz_4___3':'0',
                                'biop_frz_4___4':'0',
                                'biop_frz_4___5':'0',
                                'biop_frz_4___6':'0',
                                'biop_frz_4___7':'0'
                                }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_4_id_tc': barcode_id,
                                'biopsy_id_frozen_4': barcode_id,
                                'freezer_frozen_4':loc_tuple[1],
                                'rack_frozen_4':loc_tuple[2],
                                'box_frozen_4': loc_tuple[3],
                                'box_pos_frozen_4':loc_tuple[4],
                                'biop_frz_4___1':'0',
                                'biop_frz_4___2':'0',
                                'biop_frz_4___3':'1',
                                'biop_frz_4___4':'0',
                                'biop_frz_4___5':'0',
                                'biop_frz_4___6':'0',
                                'biop_frz_4___7':'0'
                                }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_4_id_lc': barcode_id,
                                'biopsy_id_frozen_4': barcode_id,
                                'freezer_frozen_4':loc_tuple[1],
                                'rack_frozen_4':loc_tuple[2],
                                'box_frozen_4': loc_tuple[3],
                                'box_pos_frozen_4':loc_tuple[4],
                                'biop_frz_4___1':'0',
                                'biop_frz_4___2':'0',
                                'biop_frz_4___3':'0',
                                'biop_frz_4___4':'1',
                                'biop_frz_4___5':'0',
                                'biop_frz_4___6':'0',
                                'biop_frz_4___7':'0'
                                }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_4_id_sc': barcode_id,
                                'biopsy_id_frozen_4': barcode_id,
                                'freezer_frozen_4':loc_tuple[1],
                                'rack_frozen_4':loc_tuple[2],
                                'box_frozen_4': loc_tuple[3],
                                'box_pos_frozen_4':loc_tuple[4],
                                'biop_frz_4___1':'0',
                                'biop_frz_4___2':'0',
                                'biop_frz_4___3':'0',
                                'biop_frz_4___4':'0',
                                'biop_frz_4___5':'1',
                                'biop_frz_4___6':'0',
                                'biop_frz_4___7':'0'
                                }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_4_id_r': barcode_id,
                                'biopsy_id_frozen_4': barcode_id,
                                'freezer_frozen_4':loc_tuple[1],
                                'rack_frozen_4':loc_tuple[2],
                                'box_frozen_4': loc_tuple[3],
                                'box_pos_frozen_4':loc_tuple[4],
                                'biop_frz_4___1':'0',
                                'biop_frz_4___2':'0',
                                'biop_frz_4___3':'0',
                                'biop_frz_4___4':'0',
                                'biop_frz_4___5':'0',
                                'biop_frz_4___6':'1',
                                'biop_frz_4___7':'0'
                                }       
            elif 'Frozen_5' in  barcode_id:  
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_5_id_ti': barcode_id,
                                'biopsy_id_frozen_5': barcode_id,
                                'freezer_frozen_5':loc_tuple[1],
                                'rack_frozen_5':loc_tuple[2],
                                'box_frozen_5': loc_tuple[3],
                                'box_pos_frozen_5':loc_tuple[4],
                                'biop_frz_5___1':'1',
                                'biop_frz_5___2':'0',
                                'biop_frz_5___3':'0',
                                'biop_frz_5___4':'0',
                                'biop_frz_5___5':'0',
                                'biop_frz_5___6':'0',
                                'biop_frz_5___7':'0'
                                }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_5_id_rc': barcode_id,
                                'biopsy_id_frozen_5': barcode_id,
                                'freezer_frozen_5':loc_tuple[1],
                                'rack_frozen_5':loc_tuple[2],
                                'box_frozen_5': loc_tuple[3],
                                'box_pos_frozen_5':loc_tuple[4],
                                'biop_frz_5___1':'0',
                                'biop_frz_5___2':'1',
                                'biop_frz_5___3':'0',
                                'biop_frz_5___4':'0',
                                'biop_frz_5___5':'0',
                                'biop_frz_5___6':'0',
                                'biop_frz_5___7':'0'
                                }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_5_id_tc': barcode_id,
                                'biopsy_id_frozen_5': barcode_id,
                                'freezer_frozen_5':loc_tuple[1],
                                'rack_frozen_5':loc_tuple[2],
                                'box_frozen_5': loc_tuple[3],
                                'box_pos_frozen_5':loc_tuple[4],
                                'biop_frz_5___1':'0',
                                'biop_frz_5___2':'0',
                                'biop_frz_5___3':'1',
                                'biop_frz_5___4':'0',
                                'biop_frz_5___5':'0',
                                'biop_frz_5___6':'0',
                                'biop_frz_5___7':'0'
                                }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_5_id_lc': barcode_id,
                                'biopsy_id_frozen_5': barcode_id,
                                'freezer_frozen_5':loc_tuple[1],
                                'rack_frozen_5':loc_tuple[2],
                                'box_frozen_5': loc_tuple[3],
                                'box_pos_frozen_5':loc_tuple[4],
                                'biop_frz_5___1':'0',
                                'biop_frz_5___2':'0',
                                'biop_frz_5___3':'0',
                                'biop_frz_5___4':'1',
                                'biop_frz_5___5':'0',
                                'biop_frz_5___6':'0',
                                'biop_frz_5___7':'0'
                                }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_5_id_sc': barcode_id,
                                'biopsy_id_frozen_5': barcode_id,
                                'freezer_frozen_5':loc_tuple[1],
                                'rack_frozen_5':loc_tuple[2],
                                'box_frozen_5': loc_tuple[3],
                                'box_pos_frozen_5':loc_tuple[4],
                                'biop_frz_5___1':'0',
                                'biop_frz_5___2':'0',
                                'biop_frz_5___3':'0',
                                'biop_frz_5___4':'0',
                                'biop_frz_5___5':'1',
                                'biop_frz_5___6':'0',
                                'biop_frz_5___7':'0'
                                }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_5_id_r': barcode_id,
                                'biopsy_id_frozen_5': barcode_id,
                                'freezer_frozen_5':loc_tuple[1],
                                'rack_frozen_5':loc_tuple[2],
                                'box_frozen_5': loc_tuple[3],
                                'box_pos_frozen_5':loc_tuple[4],
                                'biop_frz_5___1':'0',
                                'biop_frz_5___2':'0',
                                'biop_frz_5___3':'0',
                                'biop_frz_5___4':'0',
                                'biop_frz_5___5':'0',
                                'biop_frz_5___6':'1',
                                'biop_frz_5___7':'0'
                                }        
            elif 'Frozen_6' in  barcode_id:  
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_6_id_ti': barcode_id,
                                'biopsy_id_frozen_6': barcode_id,
                                'freezer_frozen_6':loc_tuple[1],
                                'rack_frozen_6':loc_tuple[2],
                                'box_frozen_6': loc_tuple[3],
                                'box_pos_frozen_6':loc_tuple[4],
                                'biop_frz_6___1':'1',
                                'biop_frz_6___2':'0',
                                'biop_frz_6___3':'0',
                                'biop_frz_6___4':'0',
                                'biop_frz_6___5':'0',
                                'biop_frz_6___6':'0',
                                'biop_frz_6___7':'0'
                                }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_6_id_rc': barcode_id,
                                'biopsy_id_frozen_6': barcode_id,
                                'freezer_frozen_6':loc_tuple[1],
                                'rack_frozen_6':loc_tuple[2],
                                'box_frozen_6': loc_tuple[3],
                                'box_pos_frozen_6':loc_tuple[4],
                                'biop_frz_6___1':'0',
                                'biop_frz_6___2':'1',
                                'biop_frz_6___3':'0',
                                'biop_frz_6___4':'0',
                                'biop_frz_6___5':'0',
                                'biop_frz_6___6':'0',
                                'biop_frz_6___7':'0'
                                }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_6_id_tc': barcode_id,
                                'biopsy_id_frozen_6': barcode_id,
                                'freezer_frozen_6':loc_tuple[1],
                                'rack_frozen_6':loc_tuple[2],
                                'box_frozen_6': loc_tuple[3],
                                'box_pos_frozen_6':loc_tuple[4],
                                'biop_frz_6___1':'0',
                                'biop_frz_6___2':'0',
                                'biop_frz_6___3':'1',
                                'biop_frz_6___4':'0',
                                'biop_frz_6___5':'0',
                                'biop_frz_6___6':'0',
                                'biop_frz_6___7':'0'
                                }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_6_id_lc': barcode_id,
                                'biopsy_id_frozen_6': barcode_id,
                                'freezer_frozen_6':loc_tuple[1],
                                'rack_frozen_6':loc_tuple[2],
                                'box_frozen_6': loc_tuple[3],
                                'box_pos_frozen_6':loc_tuple[4],
                                'biop_frz_6___1':'0',
                                'biop_frz_6___2':'0',
                                'biop_frz_6___3':'0',
                                'biop_frz_6___4':'1',
                                'biop_frz_6___5':'0',
                                'biop_frz_6___6':'0',
                                'biop_frz_6___7':'0'
                                }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_6_id_sc': barcode_id,
                                'biopsy_id_frozen_6': barcode_id,
                                'freezer_frozen_6':loc_tuple[1],
                                'rack_frozen_6':loc_tuple[2],
                                'box_frozen_6': loc_tuple[3],
                                'box_pos_frozen_6':loc_tuple[4],
                                'biop_frz_6___1':'0',
                                'biop_frz_6___2':'0',
                                'biop_frz_6___3':'0',
                                'biop_frz_6___4':'0',
                                'biop_frz_6___5':'1',
                                'biop_frz_6___6':'0',
                                'biop_frz_6___7':'0'
                                }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_6_id_r': barcode_id,
                                'biopsy_id_frozen_6': barcode_id,
                                'freezer_frozen_6':loc_tuple[1],
                                'rack_frozen_6':loc_tuple[2],
                                'box_frozen_6': loc_tuple[3],
                                'box_pos_frozen_6':loc_tuple[4],
                                'biop_frz_6___1':'0',
                                'biop_frz_6___2':'0',
                                'biop_frz_6___3':'0',
                                'biop_frz_6___4':'0',
                                'biop_frz_6___5':'0',
                                'biop_frz_6___6':'1',
                                'biop_frz_6___7':'0'
                                }           
            elif 'Frozen_7' in  barcode_id:  
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_7_id_ti': barcode_id,
                                'biopsy_id_frozen_7': barcode_id,
                                'freezer_frozen_7':loc_tuple[1],
                                'rack_frozen_7':loc_tuple[2],
                                'box_frozen_7': loc_tuple[3],
                                'box_pos_frozen_7':loc_tuple[4],
                                'biop_frz_7___1':'1',
                                'biop_frz_7___2':'0',
                                'biop_frz_7___3':'0',
                                'biop_frz_7___4':'0',
                                'biop_frz_7___5':'0',
                                'biop_frz_7___6':'0',
                                'biop_frz_7___7':'0'
                                }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_7_id_rc': barcode_id,
                                'biopsy_id_frozen_7': barcode_id,
                                'freezer_frozen_7':loc_tuple[1],
                                'rack_frozen_7':loc_tuple[2],
                                'box_frozen_7': loc_tuple[3],
                                'box_pos_frozen_7':loc_tuple[4],
                                'biop_frz_7___1':'0',
                                'biop_frz_7___2':'1',
                                'biop_frz_7___3':'0',
                                'biop_frz_7___4':'0',
                                'biop_frz_7___5':'0',
                                'biop_frz_7___6':'0',
                                'biop_frz_7___7':'0'
                                }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_7_id_tc': barcode_id,
                                'biopsy_id_frozen_7': barcode_id,
                                'freezer_frozen_7':loc_tuple[1],
                                'rack_frozen_7':loc_tuple[2],
                                'box_frozen_7': loc_tuple[3],
                                'box_pos_frozen_7':loc_tuple[4],
                                'biop_frz_7___1':'0',
                                'biop_frz_7___2':'0',
                                'biop_frz_7___3':'1',
                                'biop_frz_7___4':'0',
                                'biop_frz_7___5':'0',
                                'biop_frz_7___6':'0',
                                'biop_frz_7___7':'0'
                                }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_7_id_lc': barcode_id,
                                'biopsy_id_frozen_7': barcode_id,
                                'freezer_frozen_7':loc_tuple[1],
                                'rack_frozen_7':loc_tuple[2],
                                'box_frozen_7': loc_tuple[3],
                                'box_pos_frozen_7':loc_tuple[4],
                                'biop_frz_7___1':'0',
                                'biop_frz_7___2':'0',
                                'biop_frz_7___3':'0',
                                'biop_frz_7___4':'1',
                                'biop_frz_7___5':'0',
                                'biop_frz_7___6':'0',
                                'biop_frz_7___7':'0'
                                }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_7_id_sc': barcode_id,
                                'biopsy_id_frozen_7': barcode_id,
                                'freezer_frozen_7':loc_tuple[1],
                                'rack_frozen_7':loc_tuple[2],
                                'box_frozen_7': loc_tuple[3],
                                'box_pos_frozen_7':loc_tuple[4],
                                'biop_frz_7___1':'0',
                                'biop_frz_7___2':'0',
                                'biop_frz_7___3':'0',
                                'biop_frz_7___4':'0',
                                'biop_frz_7___5':'1',
                                'biop_frz_7___6':'0',
                                'biop_frz_7___7':'0'
                                }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_7_id_r': barcode_id,
                                'biopsy_id_frozen_7': barcode_id,
                                'freezer_frozen_7':loc_tuple[1],
                                'rack_frozen_7':loc_tuple[2],
                                'box_frozen_7': loc_tuple[3],
                                'box_pos_frozen_7':loc_tuple[4],
                                'biop_frz_7___1':'0',
                                'biop_frz_7___2':'0',
                                'biop_frz_7___3':'0',
                                'biop_frz_7___4':'0',
                                'biop_frz_7___5':'0',
                                'biop_frz_7___6':'1',
                                'biop_frz_7___7':'0'
                                }
            elif 'Frozen_8' in  barcode_id:  
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_8_id_ti': barcode_id,
                                'biopsy_id_frozen_8': barcode_id,
                                'freezer_frozen_8':loc_tuple[1],
                                'rack_frozen_8':loc_tuple[2],
                                'box_frozen_8': loc_tuple[3],
                                'box_pos_frozen_8':loc_tuple[4],
                                'biop_frz_8___1':'1',
                                'biop_frz_8___2':'0',
                                'biop_frz_8___3':'0',
                                'biop_frz_8___4':'0',
                                'biop_frz_8___5':'0',
                                'biop_frz_8___6':'0',
                                'biop_frz_8___7':'0'
                                }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_8_id_rc': barcode_id,
                                'biopsy_id_frozen_8': barcode_id,
                                'freezer_frozen_8':loc_tuple[1],
                                'rack_frozen_8':loc_tuple[2],
                                'box_frozen_8': loc_tuple[3],
                                'box_pos_frozen_8':loc_tuple[4],
                                'biop_frz_8___1':'0',
                                'biop_frz_8___2':'1',
                                'biop_frz_8___3':'0',
                                'biop_frz_8___4':'0',
                                'biop_frz_8___5':'0',
                                'biop_frz_8___6':'0',
                                'biop_frz_8___7':'0'
                                }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_8_id_tc': barcode_id,
                                'biopsy_id_frozen_8': barcode_id,
                                'freezer_frozen_8':loc_tuple[1],
                                'rack_frozen_8':loc_tuple[2],
                                'box_frozen_8': loc_tuple[3],
                                'box_pos_frozen_8':loc_tuple[4],
                                'biop_frz_8___1':'0',
                                'biop_frz_8___2':'0',
                                'biop_frz_8___3':'1',
                                'biop_frz_8___4':'0',
                                'biop_frz_8___5':'0',
                                'biop_frz_8___6':'0',
                                'biop_frz_8___7':'0'
                                }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_8_id_lc': barcode_id,
                                'biopsy_id_frozen_8': barcode_id,
                                'freezer_frozen_8':loc_tuple[1],
                                'rack_frozen_8':loc_tuple[2],
                                'box_frozen_8': loc_tuple[3],
                                'box_pos_frozen_8':loc_tuple[4],
                                'biop_frz_8___1':'0',
                                'biop_frz_8___2':'0',
                                'biop_frz_8___3':'0',
                                'biop_frz_8___4':'1',
                                'biop_frz_8___5':'0',
                                'biop_frz_8___6':'0',
                                'biop_frz_8___7':'0'
                                }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_8_id_sc': barcode_id,
                                'biopsy_id_frozen_8': barcode_id,
                                'freezer_frozen_8':loc_tuple[1],
                                'rack_frozen_8':loc_tuple[2],
                                'box_frozen_8': loc_tuple[3],
                                'box_pos_frozen_8':loc_tuple[4],
                                'biop_frz_8___1':'0',
                                'biop_frz_8___2':'0',
                                'biop_frz_8___3':'0',
                                'biop_frz_8___4':'0',
                                'biop_frz_8___5':'1',
                                'biop_frz_8___6':'0',
                                'biop_frz_8___7':'0'
                                }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_8_id_r': barcode_id,
                                'biopsy_id_frozen_8': barcode_id,
                                'freezer_frozen_8':loc_tuple[1],
                                'rack_frozen_8':loc_tuple[2],
                                'box_frozen_8': loc_tuple[3],
                                'box_pos_frozen_8':loc_tuple[4],
                                'biop_frz_8___1':'0',
                                'biop_frz_8___2':'0',
                                'biop_frz_8___3':'0',
                                'biop_frz_8___4':'0',
                                'biop_frz_8___5':'0',
                                'biop_frz_8___6':'1',
                                'biop_frz_8___7':'0'
                                }       
            elif 'Frozen_9' in  barcode_id:  
                if 'Terminal ileum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_9_id_ti': barcode_id,
                                'biopsy_id_frozen_9': barcode_id,
                                'freezer_frozen_9':loc_tuple[1],
                                'rack_frozen_9':loc_tuple[2],
                                'box_frozen_9': loc_tuple[3],
                                'box_pos_frozen_9':loc_tuple[4],
                                'biop_frz_9___1':'1',
                                'biop_frz_9___2':'0',
                                'biop_frz_9___3':'0',
                                'biop_frz_9___4':'0',
                                'biop_frz_9___5':'0',
                                'biop_frz_9___6':'0',
                                'biop_frz_9___7':'0'
                                }
                elif 'Right colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_9_id_rc': barcode_id,
                                'biopsy_id_frozen_9': barcode_id,
                                'freezer_frozen_9':loc_tuple[1],
                                'rack_frozen_9':loc_tuple[2],
                                'box_frozen_9': loc_tuple[3],
                                'box_pos_frozen_9':loc_tuple[4],
                                'biop_frz_9___1':'0',
                                'biop_frz_9___2':'1',
                                'biop_frz_9___3':'0',
                                'biop_frz_9___4':'0',
                                'biop_frz_9___5':'0',
                                'biop_frz_9___6':'0',
                                'biop_frz_9___7':'0'
                                }
                elif 'Transverse colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_9_id_tc': barcode_id,
                                'biopsy_id_frozen_9': barcode_id,
                                'freezer_frozen_9':loc_tuple[1],
                                'rack_frozen_9':loc_tuple[2],
                                'box_frozen_9': loc_tuple[3],
                                'box_pos_frozen_9':loc_tuple[4],
                                'biop_frz_9___1':'0',
                                'biop_frz_9___2':'0',
                                'biop_frz_9___3':'1',
                                'biop_frz_9___4':'0',
                                'biop_frz_9___5':'0',
                                'biop_frz_9___6':'0',
                                'biop_frz_9___7':'0'
                                }
                elif 'Left colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_9_id_lc': barcode_id,
                                'biopsy_id_frozen_9': barcode_id,
                                'freezer_frozen_9':loc_tuple[1],
                                'rack_frozen_9':loc_tuple[2],
                                'box_frozen_9': loc_tuple[3],
                                'box_pos_frozen_9':loc_tuple[4],
                                'biop_frz_9___1':'0',
                                'biop_frz_9___2':'0',
                                'biop_frz_9___3':'0',
                                'biop_frz_9___4':'1',
                                'biop_frz_9___5':'0',
                                'biop_frz_9___6':'0',
                                'biop_frz_9___7':'0'
                                }
                elif 'Sigmoid colon' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_9_id_sc': barcode_id,
                                'biopsy_id_frozen_9': barcode_id,
                                'freezer_frozen_9':loc_tuple[1],
                                'rack_frozen_9':loc_tuple[2],
                                'box_frozen_9': loc_tuple[3],
                                'box_pos_frozen_9':loc_tuple[4],
                                'biop_frz_9___1':'0',
                                'biop_frz_9___2':'0',
                                'biop_frz_9___3':'0',
                                'biop_frz_9___4':'0',
                                'biop_frz_9___5':'1',
                                'biop_frz_9___6':'0',
                                'biop_frz_9___7':'0'
                                }
                elif 'Rectum' in biopsies_type:
                    to_import = {'record_id':subject_id,
                                'redcap_event_name':tmp_redcap_event_name,
                                'biopsy_frozen_9_id_r': barcode_id,
                                'biopsy_id_frozen_9': barcode_id,
                                'freezer_frozen_9':loc_tuple[1],
                                'rack_frozen_9':loc_tuple[2],
                                'box_frozen_9': loc_tuple[3],
                                'box_pos_frozen_9':loc_tuple[4],
                                'biop_frz_9___1':'0',
                                'biop_frz_9___2':'0',
                                'biop_frz_9___3':'0',
                                'biop_frz_9___4':'0',
                                'biop_frz_9___5':'0',
                                'biop_frz_9___6':'1',
                                'biop_frz_9___7':'0'
                                }        
        
        self.to_import_list_overwrite.append(to_import)
    
        return True     
