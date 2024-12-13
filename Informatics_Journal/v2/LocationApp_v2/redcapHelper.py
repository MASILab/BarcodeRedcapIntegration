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
        
        return self.getRecordFromRedcap(['cd_arm_1','control_arm_1','cd_arm_2','control_arm_2'],['record_id'])
    
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
                tmp_subj = self._tmp_subset[idx].get('barcode_sample_id')[4:7]
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
            aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8
            
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
            aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8
            
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
            if 'SR10' in barcode_id or 'SR11' in barcode_id:
                aliquot_id = barcode_id[-2:] # SR10, SR11
            else:
                aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8,SR9,
            
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
            aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8
            
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
            aliquot_id = barcode_id[-1:] # SR1, SR2, SR3, ... SR8

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
        if study_type == 'UC_ENDO':
            tmp_redcap_event_name = 'uc_arm_1'
        elif study_type == 'CD_ENDO':
            tmp_redcap_event_name = 'cd_arm_1'
        elif study_type == 'CTL_ENDO':
            tmp_redcap_event_name = 'control_arm_1'
        elif study_type == 'UC_Surgery':
            tmp_redcap_event_name = 'uc_arm_2'
        elif study_type == 'CD_Surgery':
            tmp_redcap_event_name = 'cd_arm_2'
        elif study_type == 'CTL_Surgery':
            tmp_redcap_event_name = 'control_arm_2'
         
        to_import = {}
        if 'SR' in barcode_id:
            if 'SR1' in barcode_id:
                if 'SR10' in barcode_id:
                    to_import = {'record_id':subject_id,
                                  'redcap_event_name':tmp_redcap_event_name,
                                  'specimen_serum_al_500_2':'',                                  
                                  'specimen_serum_500_2_freezer':'',
                                  'specimen_serum_500_2_rack_loc':'',
                                  'specimen_serum_500_2_box':'',
                                  'specimen_serum_500_2_box_pos':''}
                elif 'SR11' in barcode_id:
                    to_import = {'record_id':subject_id,
                                  'redcap_event_name':tmp_redcap_event_name,
                                  'specimen_serum_al_500_3':'',
                                  'specimen_serum_500_3_freezer':'',
                                  'specimen_serum_500_3_rack_loc':'',
                                  'specimen_serum_500_3_box':'',
                                  'specimen_serum_500_3_box_pos':''}
                else: # should be SR1
                    to_import = {'record_id':subject_id,
                                  'redcap_event_name':tmp_redcap_event_name,
                                  'specimen_serum_al_1_100_id':'',              
                                  'specimen_serum_100_1_freezer':'',
                                  'specimen_serum_100_1_rack_loc':'',
                                  'specimen_serum_100_1_box_2':'',
                                  'specimen_serum1_box_pos':''}
            elif 'SR2' in barcode_id:
                to_import = {'record_id':subject_id,
                               'redcap_event_name':tmp_redcap_event_name,
                               'specimen_serum_al_2_100_id':'',                     
                                'specimen_serum_100_2_freezer':'',
                                'specimen_serum_100_2_rack_loc':'',
                                'specimen_serum_100_1_box':'',
                                'specimen_serum_100_1_box_pos':''}
            elif 'SR3' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_al_3_100':'',              
                              'specimen_serum_100_3_freezer_2':'',
                              'specimen_serum_100_3_rack_loc_2':'',
                              'specimen_serum_100_3_box':'',
                              'specimen_serum_100_1_box_pos_3':''}
            elif 'SR4' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_al_4_100':'',              
                              'specimen_serum_100_4_freezer':'',
                              'specimen_serum_100_4_rack_loc_4':'',
                              'specimen_serum_100_4_box_2':'',
                              'specimen_serum_100_4_box_pos_4':''}

            elif 'SR5' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_al_250_1':'',              
                              'specimen_serum_250_freezer':'',
                              'specimen_serum_250_rack_loc':'',
                              'specimen_serum_250_box':'',
                              'specimen_serum_250_box_pos':''}
            elif 'SR6' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_al_250_2':'',              
                              'specimen_serum_250_freezer_2':'',
                              'specimen_serum_250_rack_loc_2':'',
                              'specimen_serum_250_box_2':'',
                              'specimen_serum_250_box_pos_2':''}
            elif 'SR7' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_al_250_3':'',              
                              'specimen_serum_250_freezer_3':'',
                              'specimen_serum_250_rack_loc_3':'',
                              'specimen_serum_250_box_3':'',
                              'specimen_serum_250_box_pos_3':''}
            elif 'SR8' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_al_250_4':'',              
                              'specimen_serum_250_freezer_4':'',
                              'specimen_serum_250_rack_loc_4':'',
                              'specimen_serum_250_box_4':'',
                              'specimen_serum_250_box_pos_4':''}
            elif 'SR9' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_al_500_1':'',              
                              'specimen_serum_500_1_freezer':'',
                              'specimen_serum_500_1_rack_loc':'',
                              'specimen_serum_500_1_box':'',
                              'specimen_serum_500_1_box_pos':''}
        elif 'Fresh' in barcode_id:
            to_import = {'record_id':subject_id,
                         'redcap_event_name':tmp_redcap_event_name, 
                         'biopsy_fresh_id_rc':'',
                         'biopsy_fresh_id_tc':'',
                         'biopsy_fresh_id_lc':'',
                         'biopsy_fresh_id_sc':'',
                         'biopsy_fresh_id_r':'',
                         'biopsies_collected_endo_rc___1':'0',
                         'biopsies_collected_endo_tc___1':'0',
                         'biopsies_collected_endo_lc___1':'0',
                         'biopsies_collected_endo_sc___1':'0',
                         'biopsies_collected_endo_r___1':'0'}         
        elif 'Fixed' in barcode_id:
            to_import = {'record_id':subject_id,
                         'redcap_event_name':tmp_redcap_event_name, 
                         'biopsy_fixed_id_rc':'',
                         'biopsy_fixed_id_tc':'',
                         'biopsy_fixed_id_lc':'',
                         'biopsy_fixed_id_sc':'',
                         'biopsy_fixed_id_r':'',
                         'biopsies_collected_endo_rc___2':'0',
                         'biopsies_collected_endo_tc___2':'0',
                         'biopsies_collected_endo_lc___2':'0',
                         'biopsies_collected_endo_sc___2':'0',
                         'biopsies_collected_endo_r___2':'0'}          
        elif 'Frozen' in barcode_id:
            if 'Frozen_1' in barcode_id:
                print('......')
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'cd_endo_biopsy_id':'',
                              'cd_endo_biopsies_freezer':'',
                              'cd_endo_biopsy_rack_location':'',
                              'cd_endo_biopsy_box_2':'',
                              'cd_endo_biopsy_box_position_2':'',
                              'biopsy_frozen_id_1_rc':'',
                              'biopsy_frozen_id_1_tc':'',
                              'biopsy_frozen_id_1_lc':'',
                              'biopsy_frozen_id_1_sc':'',
                              'biopsy_frozen_id_1_r':'',
                              'biopsies_collected_endo_rc___3':'0',
                              'biopsies_collected_endo_tc___3':'0',
                              'biopsies_collected_endo_lc___3':'0',
                              'biopsies_collected_endo_sc___3':'0',
                              'biopsies_collected_endo_r___3':'0'} 
            elif 'Frozen_2' in barcode_id:
                print('......')
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,   
                              'cd_endo_biopsy_id2':'',
                              'cd_endo_biopsies_freezer_2':'',
                              'cd_endo_biopsy_rack_location_2':'',
                              'cd_endo_biopsy_box_3':'',
                              'cd_endo_biopsy_box_position':'',
                              'biopsy_frozen_id_2_rc':'',
                              'biopsy_frozen_id_2_tc':'',
                              'biopsy_frozen_id_2_lc':'',
                              'biopsy_frozen_id_2_sc':'',
                              'biopsy_frozen_id_2_r':'',
                              'biopsies_collected_endo_rc___4':'0',
                              'biopsies_collected_endo_tc___4':'0',
                              'biopsies_collected_endo_lc___4':'0',
                              'biopsies_collected_endo_sc___4':'0',
                              'biopsies_collected_endo_r___4':'0'} 
            elif 'Frozen_3' in barcode_id:
                print('......')
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,  
                              'cd_endo_biopsy_id3':'', 
                              'cd_endo_biopsies_freezer_4':'',
                              'cd_endo_biopsy_rack_location_4':'',
                              'cd_endo_biopsy_box':'',
                              'cd_endo_biopsy_box_position_3':'',
                              'biopsy_frozen_id_3_rc':'',
                              'biopsy_frozen_id_3_tc':'',
                              'biopsy_frozen_id_3_lc':'',
                              'biopsy_frozen_id_3_sc':'',
                              'biopsy_frozen_id_3_r':'',
                              'biopsies_collected_endo_rc___5':'0',
                              'biopsies_collected_endo_tc___5':'0',
                              'biopsies_collected_endo_lc___5':'0',
                              'biopsies_collected_endo_sc___5':'0',
                              'biopsies_collected_endo_r___5':'0'}
            elif 'AddFrozen' in barcode_id:
                print('......')
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,  
                              'cd_endo_biopsy_id4':'', 
                              'cd_endo_biopsies_freezer_3':'',
                              'cd_endo_biopsy_rack_location_3':'',
                              'cd_endo_biopsy_box_4':'',
                              'cd_endo_biopsy_box_position_4':'',
                              'biopsy_addfrozen_id_rc':'',
                              'biopsy_addfrozen_id_tc':'',
                              'biopsy_addfrozen_id_lc':'',
                              'biopsy_addfrozen_id_sc':'',
                              'biopsy_addfrozen_id_r':'',
                              'biopsies_collected_endo_rc___6':'0',
                              'biopsies_collected_endo_tc___6':'0',
                              'biopsies_collected_endo_lc___6':'0',
                              'biopsies_collected_endo_sc___6':'0',
                              'biopsies_collected_endo_r___6':'0'}              
        elif 'DNA' in barcode_id:
            to_import = {'record_id':subject_id,
                           'redcap_event_name':tmp_redcap_event_name,
                           'specimen_dna_id':'',
                           'dna_collected_endo_cd_v2':'0'}
        
#         response = self.project.import_records(to_import,overwrite='overwrite')
        self.to_import_list_overwrite.append(to_import)
        print('?????3%s' % len(self.to_import_list_overwrite))
        return True 
    
# 
                              
    def update_REDCAP_SOPHIE_FROM_LOCATION_APP(self,subject_id,barcode_id, study_type, loc_tuple, biopsies_type ):
        tmp_redcap_event_name = ''
        if study_type == 'UC_ENDO':
            tmp_redcap_event_name = 'uc_arm_1'
        elif study_type == 'CD_ENDO':
            tmp_redcap_event_name = 'cd_arm_1'
        elif study_type == 'CTL_ENDO':
            tmp_redcap_event_name = 'control_arm_1'
        elif study_type == 'UC_Surgery':
            tmp_redcap_event_name = 'uc_arm_2'
        elif study_type == 'CD_Surgery':
            tmp_redcap_event_name = 'cd_arm_2'
        elif study_type == 'CTL_Surgery':
            tmp_redcap_event_name = 'control_arm_2'
           
        to_import = {}
        if 'SR' in barcode_id:
            if 'SR1' in barcode_id:
                if 'SR10' in barcode_id:
                    to_import = {'record_id':subject_id,
                                  'redcap_event_name':tmp_redcap_event_name,
                                  'specimen_serum_500_2_freezer':loc_tuple[1],
                                  'specimen_serum_500_2_rack_loc':loc_tuple[2],
                                  'specimen_serum_500_2_box':loc_tuple[3],
                                  'specimen_serum_500_2_box_pos':loc_tuple[4]}
                elif 'SR11' in barcode_id:
                    to_import = {'record_id':subject_id,
                                  'redcap_event_name':tmp_redcap_event_name,
                                  'specimen_serum_500_3_freezer':loc_tuple[1],
                                  'specimen_serum_500_3_rack_loc':loc_tuple[2],
                                  'specimen_serum_500_3_box':loc_tuple[3],
                                  'specimen_serum_500_3_box_pos':loc_tuple[4]}
                else: # should be SR1
                    to_import = {'record_id':subject_id,
                                  'redcap_event_name':tmp_redcap_event_name,
                                  'specimen_serum_100_1_freezer':loc_tuple[1],
                                  'specimen_serum_100_1_rack_loc':loc_tuple[2],
                                  'specimen_serum_100_1_box_2':loc_tuple[3],
                                  'specimen_serum1_box_pos':loc_tuple[4]}
            elif 'SR2' in barcode_id:
                to_import = {'record_id':subject_id,
                               'redcap_event_name':tmp_redcap_event_name,
                                'specimen_serum_100_2_freezer':loc_tuple[1],
                                'specimen_serum_100_2_rack_loc':loc_tuple[2],
                                'specimen_serum_100_1_box':loc_tuple[3],
                                'specimen_serum_100_1_box_pos':loc_tuple[4]}
            elif 'SR3' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_100_3_freezer_2':loc_tuple[1],
                              'specimen_serum_100_3_rack_loc_2':loc_tuple[2],
                              'specimen_serum_100_3_box':loc_tuple[3],
                              'specimen_serum_100_1_box_pos_3':loc_tuple[4]}
            elif 'SR4' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_100_4_freezer':loc_tuple[1],
                              'specimen_serum_100_4_rack_loc_4':loc_tuple[2],
                              'specimen_serum_100_4_box_2':loc_tuple[3],
                              'specimen_serum_100_4_box_pos_4':loc_tuple[4]}

            elif 'SR5' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_250_freezer':loc_tuple[1],
                              'specimen_serum_250_rack_loc':loc_tuple[2],
                              'specimen_serum_250_box':loc_tuple[3],
                              'specimen_serum_250_box_pos':loc_tuple[4]}
            elif 'SR6' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_250_freezer_2':loc_tuple[1],
                              'specimen_serum_250_rack_loc_2':loc_tuple[2],
                              'specimen_serum_250_box_2':loc_tuple[3],
                              'specimen_serum_250_box_pos_2':loc_tuple[4]}
            elif 'SR7' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_250_freezer_3':loc_tuple[1],
                              'specimen_serum_250_rack_loc_3':loc_tuple[2],
                              'specimen_serum_250_box_3':loc_tuple[3],
                              'specimen_serum_250_box_pos_3':loc_tuple[4]}
            elif 'SR8' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_250_freezer_4':loc_tuple[1],
                              'specimen_serum_250_rack_loc_4':loc_tuple[2],
                              'specimen_serum_250_box_4':loc_tuple[3],
                              'specimen_serum_250_box_pos_4':loc_tuple[4]}
            elif 'SR9' in barcode_id:
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,
                              'specimen_serum_500_1_freezer':loc_tuple[1],
                              'specimen_serum_500_1_rack_loc':loc_tuple[2],
                              'specimen_serum_500_1_box':loc_tuple[3],
                              'specimen_serum_500_1_box_pos':loc_tuple[4]}
        elif 'Frozen' in barcode_id:
            if 'Frozen_1' in barcode_id:
                print('......')
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'cd_endo_biopsies_freezer':loc_tuple[1],
                             'cd_endo_biopsy_rack_location':loc_tuple[2],
                             'cd_endo_biopsy_box_2':loc_tuple[3],
                             'cd_endo_biopsy_box_position_2':loc_tuple[4]} 
                    
            elif 'Frozen_2' in barcode_id:
                print('......')
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,   
                              'cd_endo_biopsies_freezer_2':loc_tuple[1],
                              'cd_endo_biopsy_rack_location_2':loc_tuple[2],
                              'cd_endo_biopsy_box_3':loc_tuple[3],
                              'cd_endo_biopsy_box_position':loc_tuple[4]} 
            elif 'Frozen_3' in barcode_id:
                print('......')
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,  
                              'cd_endo_biopsies_freezer_4':loc_tuple[1],
                              'cd_endo_biopsy_rack_location_4':loc_tuple[2],
                              'cd_endo_biopsy_box':loc_tuple[3],
                              'cd_endo_biopsy_box_position_3':loc_tuple[4]}
            elif 'AddFrozen' in barcode_id:
                print('......')
                to_import = {'record_id':subject_id,
                              'redcap_event_name':tmp_redcap_event_name,  
                              'cd_endo_biopsies_freezer_3':loc_tuple[1],
                              'cd_endo_biopsy_rack_location_3':loc_tuple[2],
                              'cd_endo_biopsy_box_4':loc_tuple[3],
                              'cd_endo_biopsy_box_position_4':loc_tuple[4]}           
            # now update the ID field
            
#         elif 'DNA' in barcode_id: # no need to do DNA
#             to_import = {'record_id':subject_id,
#                            'redcap_event_name':tmp_redcap_event_name,
#                            'specimen_dna_id':''}
        
#         response = self.project.import_records(to_import,overwrite='overwrite')
        self.to_import_list_overwrite.append(to_import)
        to_import = {}
        # Now let's start deal with frozen, fresh, fixed ID in Right colon - RC", "Transverse colon - TC", 'Left colon - LC', 'Sigmoid colon - SC', 'Rectum - R
        if 'Right colon' in biopsies_type:
            if 'Frozen_1' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_1_rc':barcode_id,
                             'biopsies_collected_endo_rc___3':'1'} 
            elif 'Frozen_2' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_2_rc':barcode_id,
                             'biopsies_collected_endo_rc___4':'1'}                
            elif 'Frozen_3' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_3_rc':barcode_id,
                             'biopsies_collected_endo_rc___5':'1'}
            elif 'AddFrozen' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_addfrozen_id_rc':barcode_id,
                             'biopsies_collected_endo_rc___6':'1'}
            elif 'Fresh' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fresh_id_rc':barcode_id,
                             'biopsies_collected_endo_rc___1':'1'}
            elif 'Fixed' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fixed_id_rc':barcode_id,
                             'biopsies_collected_endo_rc___2':'1'}                
        elif 'Transverse colon' in biopsies_type:
            if 'Frozen_1' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_1_tc':barcode_id,
                             'biopsies_collected_endo_tc___3':'1'} 
            elif 'Frozen_2' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_2_tc':barcode_id,
                             'biopsies_collected_endo_tc___4':'1'}                
            elif 'Frozen_3' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_3_tc':barcode_id,
                             'biopsies_collected_endo_tc___5':'1'}   
            elif 'AddFrozen' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_addfrozen_id_tc':barcode_id,
                             'biopsies_collected_endo_tc___6':'1'} 
            elif 'Fresh' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fresh_id_tc':barcode_id,
                             'biopsies_collected_endo_tc___1':'1'}
            elif 'Fixed' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fixed_id_tc':barcode_id,
                             'biopsies_collected_endo_tc___2':'1'}            
            
        elif 'Left colon' in biopsies_type:
            if 'Frozen_1' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_1_lc':barcode_id,
                             'biopsies_collected_endo_lc___3':'1'} 
            elif 'Frozen_2' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_2_lc':barcode_id,
                             'biopsies_collected_endo_lc___4':'1'}                
            elif 'Frozen_3' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_3_lc':barcode_id,
                             'biopsies_collected_endo_lc___5':'1'}
            elif 'AddFrozen' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_addfrozen_id_lc':barcode_id,
                             'biopsies_collected_endo_lc___6':'1'}  
            elif 'Fresh' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fresh_id_lc':barcode_id,
                             'biopsies_collected_endo_lc___1':'1'}
            elif 'Fixed' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fixed_id_lc':barcode_id,
                             'biopsies_collected_endo_lc___2':'1'}
                
        elif 'Sigmoid colon' in biopsies_type:
            if 'Frozen_1' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_1_sc':barcode_id,
                             'biopsies_collected_endo_sc___3':'1'} 
            elif 'Frozen_2' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_2_sc':barcode_id,
                             'biopsies_collected_endo_sc___4':'1'}                
            elif 'Frozen_3' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_3_sc':barcode_id,
                             'biopsies_collected_endo_sc___5':'1'}  
            elif 'AddFrozen' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_addfrozen_id_sc':barcode_id,
                             'biopsies_collected_endo_sc___6':'1'} 
            elif 'Fresh' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fresh_id_sc':barcode_id,
                             'biopsies_collected_endo_sc___1':'1'}
            elif 'Fixed' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fixed_id_sc':barcode_id,
                             'biopsies_collected_endo_sc___2':'1'}
                
        elif 'Rectum' in biopsies_type:
            if 'Frozen_1' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_1_r':barcode_id,
                             'biopsies_collected_endo_r___3':'1'} 
            elif 'Frozen_2' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_2_r':barcode_id,
                             'biopsies_collected_endo_r___4':'1'}                
            elif 'Frozen_3' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_frozen_id_3_r':barcode_id,
                             'biopsies_collected_endo_r___5':'1'}
            elif 'AddFrozen' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_addfrozen_id_r':barcode_id,
                             'biopsies_collected_endo_r___6':'1'}
            elif 'Fresh' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fresh_id_r':barcode_id,
                             'biopsies_collected_endo_r___1':'1'}
            elif 'Fixed' in barcode_id:
                to_import = {'record_id':subject_id,
                             'redcap_event_name':tmp_redcap_event_name,
                             'biopsy_fixed_id_r':barcode_id,
                             'biopsies_collected_endo_r___2':'1'}               
        self.to_import_list_overwrite.append(to_import)
    
        print('?????3%s' % len(self.to_import_list_overwrite))
        return True     
