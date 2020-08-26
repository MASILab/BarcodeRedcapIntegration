#!/usr/bin/env python
import redcap
import pandas as pd
import csv
import cgi

    
def overview_subj_stats(dataset,project):
    
#     dataset = project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id','barcode_subject_type','barcode_action_type'])
    df = pd.DataFrame.from_dict(dataset)

    query_table = df[
            (df['barcode_action_type'].str.contains('distributed')) |
            (df['barcode_action_type'].str.contains('stored in rack')) |
            (df['barcode_action_type'].str.contains('printed')) |
            (df['barcode_action_type'].str.contains('Re-print')) |
            (df['barcode_action_type'].str.contains('Barcode destroyed')) ] \
            .drop_duplicates(subset=['barcode_sample_id'], keep="last")

    query_table_collected = query_table[
            (query_table['barcode_action_type'].str.contains('distributed')) |
            (query_table['barcode_action_type'].str.contains('stored in rack'))]

    query_table_destroyed = query_table[query_table['barcode_action_type'].str.contains('Barcode destroyed')]

    query_table_wait = query_table[
            (query_table['barcode_action_type'].str.contains('printed')) |
            (query_table['barcode_action_type'].str.contains('Re-print'))]

    # for add print stats
    query_table_print = df[
            (df['barcode_action_type'].str.contains('printed')) |
            (df['barcode_action_type'].str.contains('Re-print'))] \
            .drop_duplicates(subset=['barcode_sample_id'], keep="last")

    subject_dataset = project.export_records(fields=['record_id_dem_endo'])
    df_subj  = pd.DataFrame.from_dict(subject_dataset)
    query_subject = df_subj[df_subj["record_id_dem_endo"].str.contains('action') == False].drop_duplicates(subset=['record_id_dem_endo'], keep="last")
    df_subject_id = set(query_subject['record_id_dem_endo'])

    final_subj_list = []
    for i in df_subject_id:
        tmp = None         
        tmp = int(i)
        if tmp < 10:
            final_subj_list.append('00%s' % str(tmp))
        elif tmp < 100:
            final_subj_list.append('0%s' % str(tmp))
        else:
            final_subj_list.append(str(tmp))

    #print(sorted(final_subj_list))

    # df_sample_id = df[['barcode_sample_id']]
    # df_subject_id = set(df_sample_id['barcode_sample_id'].str[3:6].to_list())

    with open('/var/www/html/shunxing/gca/summary/data_collection_QA.html','w') as outfile:

        outfile.write('<!DOCTYPE html>\n')
        outfile.write('<html>\n')
        outfile.write('<body>\n')

        outfile.write('<h2>Data collection quality control</h2>\n')
        outfile.write('<h4>NC:not collected</h4>\n')

        with open('/var/www/html/shunxing/gca/tableStyle.txt') as fp:
            for line in fp:
                print(line)
                outfile.write(line)

        outfile.write('<table class="tg">\n')
        outfile.write('<thead>\n')
        outfile.write('<tr>\n')
        outfile.write('<th class="tg-0lax"></th>\n')
        outfile.write('<th class="tg-0lax">Stool</th>\n')
        outfile.write('<th class="tg-0lax">Serum</th>\n')
        outfile.write('<th class="tg-0lax">DNA</th>\n')
        outfile.write('<th class="tg-0lax">Fresh</th>\n')
        outfile.write('<th class="tg-0lax">Fixed</th>\n')
        outfile.write('<th class="tg-0lax">Frozen</th>\n')
        outfile.write('<th class="tg-0lax">Add Frozen</th>\n')
        outfile.write('</tr>\n')
        outfile.write('</thead>\n')
        outfile.write('<tbody>\n')

        for val in sorted(final_subj_list):
            if val == '999':
                continue

            tmp_type = df_subj.loc[df_subj['record_id_dem_endo'] == str(int(val))]
            studyType_redcap = tmp_type.iloc[0]['redcap_event_name']

            if studyType_redcap == 'cd_arm_1':
                studyType_checker = 'CD_ENDO'
            elif studyType_redcap == 'control_arm_1':
                studyType_checker = 'CTL_ENDO'
            elif studyType_redcap == 'cd_arm_2':
                studyType_checker = 'CD_Surgery'
            elif studyType_redcap == 'control_arm_2':
                studyType_checker = 'CTL_Surgery'

            #outfile.write('<h4>Subject %s: %s</h4>\n' % (val,studyType_checker))

            my_df_printed  = query_table_print[query_table_print['barcode_sample_id'].str.contains(val)]
            if len(my_df_printed) == 0:
                outfile.write('<tr>\n')
                outfile.write('<td class="tg-0lax">%s:%s</td>\n' % (val,studyType_checker))
                outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' ) 
                outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' )
                outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' )
                outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' )
                outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' )
                outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' )
                outfile.write('<td class="tg-0lax">-</td>\n' )
                outfile.write('</tr>\n')

                continue

            else:

                my_df_collected  = query_table_collected[query_table_collected['barcode_sample_id'].str.contains(val)]

                my_df_collected_stool = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('ST')]
                my_df_collected_serum = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('SR')]
                my_df_collected_DNA = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('DNA')]
                my_df_collected_fresh = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('Fresh')]
                my_df_collected_fixed = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('Fixed')]
                my_df_collected_frozen = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('Frozen')]
                my_df_collected_add_frozen = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('ADD')]

                outfile.write('<tr>\n')
                outfile.write('<td class="tg-0lax">%s:%s</td>\n' % (val,studyType_checker))
                if int(my_df_collected_stool.shape[0]) > 0:
                    outfile.write('<td class="tg-0lax">collected</td>\n')
                else:   
                    outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' )

                if int(my_df_collected_serum.shape[0]) >0:
                    outfile.write('<td class="tg-0lax">collected</td>\n')
                else:
                    outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' )

                if int(my_df_collected_DNA.shape[0])>0:
                    outfile.write('<td class="tg-0lax">collected</td>\n')
                else:
                    outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n' )

                if int(my_df_collected_fresh.shape[0]) > 0:
                    outfile.write('<td class="tg-0lax">collected</td>\n')
                else:
                    outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n')

                if int(my_df_collected_fixed.shape[0])>0:
                    outfile.write('<td class="tg-0lax">collected</td>\n')
                else:
                    outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n')

                tmp_frozen = int(my_df_collected_frozen.shape[0])-int(my_df_collected_add_frozen.shape[0])
                if tmp_frozen > 0:
                    outfile.write('<td class="tg-0lax">collected</td>\n')
                else:
                    outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">NC</td>\n')

                my_df_printed_add_frozen = my_df_printed[my_df_printed['barcode_sample_id'].str.contains('ADD')]
                if int(my_df_printed_add_frozen.shape[0]) ==0:
                    outfile.write('<td class="tg-0lax">-</td>\n')
                elif int(my_df_collected_add_frozen.shape[0]) > 0:
                    outfile.write('<td class="tg-0lax">collected</td>\n')
                else:
                    outfile.write('<td class="tg-0lax">-</td>\n')              
                outfile.write('</tr>\n')

        outfile.write('</tbody>')
        outfile.write('</table>')


        outfile.write('</body>\n')
        outfile.write('</html>\n')

        
    with open('/var/www/html/shunxing/gca/summary/subject_stats.html','w') as outfile:

        outfile.write('<!DOCTYPE html>\n')
        outfile.write('<html>\n')
        outfile.write('<body>\n')

        outfile.write('<h2>Overview of subjects\' specimens</h2>\n')

        with open('/var/www/html/shunxing/gca/tableStyle.txt') as fp:
            for line in fp:
                print(line)
                outfile.write(line)

        for val in sorted(final_subj_list):
            if val == '999':
                continue

            tmp_type = df_subj.loc[df_subj['record_id_dem_endo'] == str(int(val))]
            studyType_redcap = tmp_type.iloc[0]['redcap_event_name']

            if studyType_redcap == 'cd_arm_1':
                studyType_checker = 'CD_ENDO'
            elif studyType_redcap == 'control_arm_1':
                studyType_checker = 'CTL_ENDO'
            elif studyType_redcap == 'cd_arm_2':
                studyType_checker = 'CD_Surgery'
            elif studyType_redcap == 'control_arm_2':
                studyType_checker = 'CTL_Surgery'

            outfile.write('<h4>Subject %s: %s</h4>\n' % (val,studyType_checker))
            my_df_printed  = query_table_print[query_table_print['barcode_sample_id'].str.contains(val)]
            if len(my_df_printed) == 0:
                outfile.write('<d style="font-weight: bold;color:red">&nbsp Not printed yet</d>\n')
                continue

            else:

                outfile.write('<table class="tg">\n')
                outfile.write('<thead>\n')
                outfile.write('<tr>\n')
                outfile.write('<th class="tg-0lax"></th>\n')
                outfile.write('<th class="tg-0lax">Stool</th>\n')
                outfile.write('<th class="tg-0lax">Serum</th>\n')
                outfile.write('<th class="tg-0lax">DNA</th>\n')
                outfile.write('<th class="tg-0lax">Fresh</th>\n')
                outfile.write('<th class="tg-0lax">Fixed</th>\n')
                outfile.write('<th class="tg-0lax">Frozen</th>\n')
                outfile.write('<th class="tg-0lax">Add Frozen</th>\n')
                outfile.write('</tr>\n')
                outfile.write('</thead>\n')
                outfile.write('<tbody>\n')   

                my_df_printed_stool = my_df_printed[my_df_printed['barcode_sample_id'].str.contains('ST')]
                my_df_printed_serum = my_df_printed[my_df_printed['barcode_sample_id'].str.contains('SR')]
                my_df_printed_DNA = my_df_printed[my_df_printed['barcode_sample_id'].str.contains('DNA')]
                my_df_printed_fresh = my_df_printed[my_df_printed['barcode_sample_id'].str.contains('Fresh')]
                my_df_printed_fixed = my_df_printed[my_df_printed['barcode_sample_id'].str.contains('Fixed')]
                my_df_printed_frozen = my_df_printed[my_df_printed['barcode_sample_id'].str.contains('Frozen')]
                my_df_printed_add_frozen = my_df_printed[my_df_printed['barcode_sample_id'].str.contains('ADD')]

                outfile.write('<tr>\n')
                outfile.write('<td class="tg-0lax">Printed</td>\n')
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_printed_stool.shape[0]) 
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_printed_serum.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_printed_DNA.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_printed_fresh.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_printed_fixed.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % (int(my_df_printed_frozen.shape[0])-int(my_df_printed_add_frozen.shape[0])))
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_printed_add_frozen.shape[0])
                outfile.write('</tr>\n')


                my_df_collected  = query_table_collected[query_table_collected['barcode_sample_id'].str.contains(val)]

                my_df_collected_stool = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('ST')]
                my_df_collected_serum = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('SR')]
                my_df_collected_DNA = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('DNA')]
                my_df_collected_fresh = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('Fresh')]
                my_df_collected_fixed = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('Fixed')]
                my_df_collected_frozen = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('Frozen')]
                my_df_collected_add_frozen = my_df_collected[my_df_collected['barcode_sample_id'].str.contains('ADD')]

                outfile.write('<tr>\n')
                outfile.write('<td class="tg-0lax">Collected</td>\n')
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_collected_stool.shape[0]) 
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_collected_serum.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_collected_DNA.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_collected_fresh.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_collected_fixed.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % (int(my_df_collected_frozen.shape[0])-int(my_df_collected_add_frozen.shape[0])))
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_collected_add_frozen.shape[0])
                outfile.write('</tr>\n')

                my_df_destroyed = query_table_destroyed[query_table_destroyed['barcode_sample_id'].str.contains(val)]
                #if len(my_df_destroyed) > 0:
                my_df_destroyed_stool = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('ST')]
                my_df_destroyed_serum = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('SR')]
                my_df_destroyed_DNA = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('DNA')]
                my_df_destroyed_fresh = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('Fresh')]
                my_df_destroyed_fixed = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('Fixed')]
                my_df_destroyed_frozen = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('Frozen')]
                my_df_destroyed_add_frozen = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('ADD')]


                outfile.write('<tr>\n')
                outfile.write('<td class="tg-0lax">Destroyed</td>\n')
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_destroyed_stool.shape[0]) 
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_destroyed_serum.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_destroyed_DNA.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_destroyed_fresh.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_destroyed_fixed.shape[0])
                outfile.write('<td class="tg-0lax">%s</td>\n' % (int(my_df_destroyed_frozen.shape[0])-int(my_df_destroyed_add_frozen.shape[0])))
                outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_destroyed_add_frozen.shape[0])
                outfile.write('</tr>\n')



                my_df_not_collected  = query_table_wait[query_table_wait['barcode_sample_id'].str.contains(val)]
                if len(my_df_not_collected) > 0:
                    my_df_not_collected_stool = my_df_not_collected[my_df_not_collected['barcode_sample_id'].str.contains('ST')]
                    my_df_not_collected_serum = my_df_not_collected[my_df_not_collected['barcode_sample_id'].str.contains('SR')]
                    my_df_not_collected_DNA = my_df_not_collected[my_df_not_collected['barcode_sample_id'].str.contains('DNA')]
                    my_df_not_collected_fresh = my_df_not_collected[my_df_not_collected['barcode_sample_id'].str.contains('Fresh')]
                    my_df_not_collected_fixed = my_df_not_collected[my_df_not_collected['barcode_sample_id'].str.contains('Fixed')]
                    my_df_not_collected_frozen = my_df_not_collected[my_df_not_collected['barcode_sample_id'].str.contains('Frozen')]
                    my_df_not_collected_add_frozen = my_df_not_collected[my_df_not_collected['barcode_sample_id'].str.contains('ADD')]

                    outfile.write('<tr>\n')
                    outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">Not Collected/Destroyed</td>\n')
                    if int(my_df_not_collected_stool.shape[0]) == 0:
                        outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_not_collected_stool.shape[0])
                    else:
                        outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">%s</td>\n' % my_df_not_collected_stool.shape[0])

                    if int(my_df_not_collected_serum.shape[0]) ==0:
                        outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_not_collected_serum.shape[0])
                    else:
                        outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">%s</td>\n' % my_df_not_collected_serum.shape[0])

                    if int(my_df_not_collected_DNA.shape[0])==0:
                        outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_not_collected_DNA.shape[0])
                    else:
                        outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">%s</td>\n' % my_df_not_collected_DNA.shape[0])

                    if int(my_df_not_collected_fresh.shape[0]) == 0:
                        outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_not_collected_fresh.shape[0])
                    else:
                        outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">%s</td>\n' % my_df_not_collected_fresh.shape[0])

                    if int(my_df_not_collected_fixed.shape[0])==0:
                        outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_not_collected_fixed.shape[0])
                    else:
                        outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">%s</td>\n' % my_df_not_collected_fixed.shape[0])

                    tmp_frozen = int(my_df_not_collected_frozen.shape[0])-int(my_df_not_collected_add_frozen.shape[0])
                    if tmp_frozen == 0:
                        outfile.write('<td class="tg-0lax">%s</td>\n' % tmp_frozen)
                    else:
                        outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">%s</td>\n' % tmp_frozen)

                    if int(my_df_not_collected_add_frozen.shape[0]) == 0:
                        outfile.write('<td class="tg-0lax">%s</td>\n' % my_df_not_collected_add_frozen.shape[0])
                    else:
                        outfile.write('<td class="tg-0lax"style="font-weight: bold;color:red">%s</td>\n' % my_df_not_collected_add_frozen.shape[0])              
                    outfile.write('</tr>\n')

                outfile.write('</tbody>')
                outfile.write('</table>')

                my_df_not_collected  = query_table_wait[query_table_wait['barcode_sample_id'].str.contains(val)]['barcode_sample_id']
                if len(my_df_not_collected) > 0:
                    outfile.write('\n<d style="font-weight: bold;color:blue">Not collected/destroyed barcode ID(s):</d>\n')
                    my_df_not_collected.to_string(outfile,index = False)

        outfile.write('</body>\n')
        outfile.write('</html>\n')

def overview_specimens_storage(dataset):
    df = pd.DataFrame.from_dict(dataset)

    query_table = df[
            (df['barcode_action_type'].str.contains('distributed')) |
            (df['barcode_action_type'].str.contains('stored in rack')) |
            (df['barcode_action_type'].str.contains('printed')) |
            (df['barcode_action_type'].str.contains('Re-print')) |
            (df['barcode_action_type'].str.contains('Barcode destroyed')) ] \
            .drop_duplicates(subset=['barcode_sample_id'], keep="last")

    serum_query_table = query_table[query_table['barcode_action_type'].str.contains('Serum stored in rack')]
    stool_query_table = query_table[query_table['barcode_action_type'].str.contains('Stool stored in rack')]
    DNA_query_table = query_table[query_table['barcode_action_type'].str.contains('DNA distributed to Vantage')]
    # CD_ENDO
    serum_CD_ENDO = serum_query_table[(serum_query_table['barcode_subject_type'].str.contains('CD_ENDO'))]
    stool_CD_ENDO = stool_query_table[(stool_query_table['barcode_subject_type'].str.contains('CD_ENDO'))]
    DNA_CD_ENDO = DNA_query_table[(DNA_query_table['barcode_subject_type'].str.contains('CD_ENDO'))]

    # CTL_ENDO                     
    serum_CTL_ENDO = serum_query_table[(serum_query_table['barcode_subject_type'].str.contains('CTL_ENDO'))]
    stool_CTL_ENDO = stool_query_table[(stool_query_table['barcode_subject_type'].str.contains('CTL_ENDO'))]
    DNA_CTL_ENDO = DNA_query_table[(DNA_query_table['barcode_subject_type'].str.contains('CTL_ENDO'))]

    # CD_Surgery

    serum_CD_Surgery = serum_query_table[(serum_query_table['barcode_subject_type'].str.contains('CD_Surgery'))]
    stool_CD_Surgery = stool_query_table[(stool_query_table['barcode_subject_type'].str.contains('CD_Surgery'))]
    DNA_CD_Surgery = DNA_query_table[(DNA_query_table['barcode_subject_type'].str.contains('CD_Surgery'))]

    # CTL_Surgery

    serum_CTL_Surgery = serum_query_table[(serum_query_table['barcode_subject_type'].str.contains('CTL_Surgery')) ]
    stool_CTL_Surgery = stool_query_table[(stool_query_table['barcode_subject_type'].str.contains('CTL_Surgery'))]
    DNA_CTL_Surgery = DNA_query_table[(DNA_query_table['barcode_subject_type'].str.contains('CTL_Surgery'))]


    stats = {
        'Study_type': ['CD_ENDO', 'CTL_ENDO', 'CD_Surgery', 'CTL_Surgery','Total'], 
        'Serum': [serum_CD_ENDO.shape[0], serum_CTL_ENDO.shape[0],serum_CD_Surgery.shape[0],serum_CTL_Surgery.shape[0],
                 serum_CD_ENDO.shape[0]+serum_CTL_ENDO.shape[0]+serum_CD_Surgery.shape[0]+serum_CTL_Surgery.shape[0]],
        'Stool': [stool_CD_ENDO.shape[0], stool_CTL_ENDO.shape[0],stool_CD_Surgery.shape[0],stool_CTL_Surgery.shape[0],
                 stool_CD_ENDO.shape[0]+stool_CTL_ENDO.shape[0]+stool_CD_Surgery.shape[0]+stool_CTL_Surgery.shape[0]],
        'DNA': [DNA_CD_ENDO.shape[0], DNA_CTL_ENDO.shape[0],DNA_CD_Surgery.shape[0],DNA_CTL_Surgery.shape[0],
               DNA_CD_ENDO.shape[0]+DNA_CTL_ENDO.shape[0]+DNA_CD_Surgery.shape[0]+DNA_CTL_Surgery.shape[0]]
        }
    df_result = pd.DataFrame(data=stats)

    #to get patient number
    serum_CD_ENDO_patient_num = len(set(list(map(lambda x: x[3:6], serum_CD_ENDO.barcode_sample_id.tolist()))))
    serum_CTL_ENDO_patient_num = len(set(list(map(lambda x: x[3:6], serum_CTL_ENDO.barcode_sample_id.tolist()))))
    serum_CD_Surgery_patient_num = len(set(list(map(lambda x: x[3:6], serum_CD_Surgery.barcode_sample_id.tolist()))))
    serum_CTL_Surgery_patient_num = len(set(list(map(lambda x: x[3:6], serum_CTL_Surgery.barcode_sample_id.tolist()))))
    
    stool_CD_ENDO_patient_num = len(set(list(map(lambda x: x[3:6], stool_CD_ENDO.barcode_sample_id.tolist()))))
    stool_CTL_ENDO_patient_num = len(set(list(map(lambda x: x[3:6], stool_CTL_ENDO.barcode_sample_id.tolist()))))
    stool_CD_Surgery_patient_num = len(set(list(map(lambda x: x[3:6], stool_CD_Surgery.barcode_sample_id.tolist()))))
    stool_CTL_Surgery_patient_num = len(set(list(map(lambda x: x[3:6], stool_CTL_Surgery.barcode_sample_id.tolist()))))
    
    DNA_CD_ENDO_patient_num = len(set(list(map(lambda x: x[3:6], DNA_CD_ENDO.barcode_sample_id.tolist()))))
    DNA_CTL_ENDO_patient_num = len(set(list(map(lambda x: x[3:6], DNA_CTL_ENDO.barcode_sample_id.tolist()))))
    DNA_CD_Surgery_patient_num = len(set(list(map(lambda x: x[3:6], DNA_CD_Surgery.barcode_sample_id.tolist()))))
    DNA_CTL_Surgery_patient_num = len(set(list(map(lambda x: x[3:6], DNA_CTL_Surgery.barcode_sample_id.tolist()))))
    
    stats_patient = {
        'Study_type': ['CD_ENDO', 'CTL_ENDO', 'CD_Surgery', 'CTL_Surgery','Total'], 
        'Serum': [serum_CD_ENDO_patient_num, serum_CTL_ENDO_patient_num,serum_CD_Surgery_patient_num,serum_CTL_Surgery_patient_num,
                 serum_CD_ENDO_patient_num+serum_CTL_ENDO_patient_num+serum_CD_Surgery_patient_num+serum_CTL_Surgery_patient_num],
        'Stool': [stool_CD_ENDO_patient_num, stool_CTL_ENDO_patient_num,stool_CD_Surgery_patient_num,stool_CTL_Surgery_patient_num,
                 stool_CD_ENDO_patient_num+stool_CTL_ENDO_patient_num+stool_CD_Surgery_patient_num+stool_CTL_Surgery_patient_num],
        'DNA': [DNA_CD_ENDO_patient_num, DNA_CTL_ENDO_patient_num,DNA_CD_Surgery_patient_num,DNA_CTL_Surgery_patient_num,
               DNA_CD_ENDO_patient_num+DNA_CTL_ENDO_patient_num+DNA_CD_Surgery_patient_num+DNA_CTL_Surgery_patient_num]
                  }
    df_result_patient = pd.DataFrame(data=stats_patient)

    with open('/var/www/html/shunxing/gca/summary/specimens_stats.txt','w') as outfile:
        outfile.write('Overview of specimens storage (Specimen stats):\n\n')
        df_result.to_string(outfile,index = False)
        outfile.write('\n\nOverview of specimens storage (Patient stats):\n\n')
        df_result_patient.to_string(outfile,index = False)

def overview_biopsies_storage(dataset):
    df = pd.DataFrame.from_dict(dataset)

    query_table = df[
            (df['barcode_action_type'].str.contains('distributed')) |
            (df['barcode_action_type'].str.contains('stored in rack')) |
            (df['barcode_action_type'].str.contains('printed')) |
            (df['barcode_action_type'].str.contains('Re-print')) |
            (df['barcode_action_type'].str.contains('Barcode destroyed')) ] \
            .drop_duplicates(subset=['barcode_sample_id'], keep="last")

    fresh_qt = query_table[(query_table['barcode_action_type'].str.contains('Fresh distributed to Lau'))]
    fixed_qt = query_table[(query_table['barcode_action_type'].str.contains('Fixed distributed to TPSR'))]
    frozen_qt = query_table[(query_table['barcode_action_type'].str.contains('Frozen stored in rack'))]

    # CD_ENDO
    fresh_CD_ENDO = fresh_qt[(fresh_qt['barcode_subject_type'].str.contains('CD_ENDO')) ]

    fresh_CD_ENDO_TIA = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshTIA'))]
    fresh_CD_ENDO_TIB = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshTIB'))]
    fresh_CD_ENDO_ACA = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshACA'))]
    fresh_CD_ENDO_ACB = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshACB'))]

    fixed_CD_ENDO = fixed_qt[(fixed_qt['barcode_subject_type'].str.contains('CD_ENDO')) ]

    fixed_CD_ENDO_TIA = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedTIA'))]
    fixed_CD_ENDO_TIB = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedTIB'))]
    fixed_CD_ENDO_ACA = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedACA'))]
    fixed_CD_ENDO_ACB = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedACB'))]


    frozen_CD_ENDO = frozen_qt[(frozen_qt['barcode_subject_type'].str.contains('CD_ENDO')) ]

    frozen_CD_ENDO_TIA_ONLY = frozen_CD_ENDO[
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIA')) &
            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIA'))]

    frozen_CD_ENDO_TIA_ADD = frozen_CD_ENDO[
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIA')) &
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIA'))]

    frozen_CD_ENDO_TIB_ONLY = frozen_CD_ENDO[
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIB')) &
            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIB'))]

    frozen_CD_ENDO_TIB_ADD = frozen_CD_ENDO[
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIB')) &
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIB'))]

    frozen_CD_ENDO_ACA_ONLY = frozen_CD_ENDO[
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACA')) &
            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACA'))]

    frozen_CD_ENDO_ACA_ADD = frozen_CD_ENDO[
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACA')) &
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACA'))]

    frozen_CD_ENDO_ACB_ONLY = frozen_CD_ENDO[
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACB')) &
            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACB'))]

    frozen_CD_ENDO_ACB_ADD = frozen_CD_ENDO[
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACB')) &
            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACB'))]

    # CTL_ENDO
    fresh_CTL_ENDO = fresh_qt[(fresh_qt['barcode_subject_type'].str.contains('CTL_ENDO')) ]

    fresh_CTL_ENDO_TI = fresh_CTL_ENDO[(fresh_CTL_ENDO['barcode_sample_id'].str.contains('FreshTI'))]
    fresh_CTL_ENDO_AC = fresh_CTL_ENDO[(fresh_CTL_ENDO['barcode_sample_id'].str.contains('FreshAC'))]

    fixed_CTL_ENDO = fixed_qt[(fixed_qt['barcode_subject_type'].str.contains('CTL_ENDO')) ]

    fixed_CTL_ENDO_TI = fixed_CTL_ENDO[(fixed_CTL_ENDO['barcode_sample_id'].str.contains('FixedTI'))]
    fixed_CTL_ENDO_AC = fixed_CTL_ENDO[(fixed_CTL_ENDO['barcode_sample_id'].str.contains('FixedAC'))]


    frozen_CTL_ENDO = frozen_qt[(frozen_qt['barcode_subject_type'].str.contains('CTL_ENDO')) ]

    frozen_CTL_ENDO_TI_ONLY = frozen_CTL_ENDO[
            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenTI')) &
            (~frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenTI'))]

    frozen_CTL_ENDO_TI_ADD = frozen_CTL_ENDO[
            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenTI')) &
            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenTI'))]

    frozen_CTL_ENDO_AC_ONLY = frozen_CTL_ENDO[
            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenAC')) &
            (~frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenAC'))]

    frozen_CTL_ENDO_AC_ADD = frozen_CTL_ENDO[
            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenAC')) &
            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenAC'))]


    # CD_Surgery
    fresh_CD_Surgery = fresh_qt[(fresh_qt['barcode_subject_type'].str.contains('CD_Surgery')) ]

    fresh_CD_Surgery_TI = fresh_CD_Surgery[(fresh_CD_Surgery['barcode_sample_id'].str.contains('FreshTI'))]
    fresh_CD_Surgery_AC = fresh_CD_Surgery[(fresh_CD_Surgery['barcode_sample_id'].str.contains('FreshAC'))]

    fixed_CD_Surgery = fixed_qt[(fixed_qt['barcode_subject_type'].str.contains('CD_Surgery')) ]

    fixed_CD_Surgery_TI = fixed_CD_Surgery[(fixed_CD_Surgery['barcode_sample_id'].str.contains('FixedTI'))]
    fixed_CD_Surgery_AC = fixed_CD_Surgery[(fixed_CD_Surgery['barcode_sample_id'].str.contains('FixedAC'))]


    frozen_CD_Surgery = frozen_qt[(frozen_qt['barcode_subject_type'].str.contains('CD_Surgery')) ]

    frozen_CD_Surgery_TI_ONLY = frozen_CD_Surgery[
            (frozen_CD_Surgery['barcode_sample_id'].str.contains('FrozenTI')) &
            (~frozen_CD_Surgery['barcode_sample_id'].str.contains('ADDFrozenTI'))]

    frozen_CD_Surgery_TI_ADD = frozen_CD_Surgery[
            (frozen_CD_Surgery['barcode_sample_id'].str.contains('FrozenTI')) &
            (frozen_CD_Surgery['barcode_sample_id'].str.contains('ADDFrozenTI'))]

    frozen_CD_Surgery_AC_ONLY = frozen_CD_Surgery[
            (frozen_CD_Surgery['barcode_sample_id'].str.contains('FrozenAC')) &
            (~frozen_CD_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC'))]

    frozen_CD_Surgery_AC_ADD = frozen_CD_Surgery[
            (frozen_CD_Surgery['barcode_sample_id'].str.contains('FrozenAC')) &
            (frozen_CD_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC'))]

    # CTL_Surgery
    fresh_CTL_Surgery = fresh_qt[(fresh_qt['barcode_subject_type'].str.contains('CTL_Surgery')) ]
    fresh_CTL_Surgery_TI1 = fresh_CTL_Surgery[(fresh_CTL_Surgery['barcode_sample_id'].str.contains('FreshTI1'))]
    fresh_CTL_Surgery_TI2 = fresh_CTL_Surgery[(fresh_CTL_Surgery['barcode_sample_id'].str.contains('FreshTI2'))]
    fresh_CTL_Surgery_TI3 = fresh_CTL_Surgery[(fresh_CTL_Surgery['barcode_sample_id'].str.contains('FreshTI3'))]
    fresh_CTL_Surgery_AC4 = fresh_CTL_Surgery[(fresh_CTL_Surgery['barcode_sample_id'].str.contains('FreshAC4'))]
    fresh_CTL_Surgery_AC5 = fresh_CTL_Surgery[(fresh_CTL_Surgery['barcode_sample_id'].str.contains('FreshAC5'))]
    fresh_CTL_Surgery_AC6 = fresh_CTL_Surgery[(fresh_CTL_Surgery['barcode_sample_id'].str.contains('FreshAC6'))]
    fresh_CTL_Surgery_AC7 = fresh_CTL_Surgery[(fresh_CTL_Surgery['barcode_sample_id'].str.contains('FreshAC7'))]
    fresh_CTL_Surgery_AC8 = fresh_CTL_Surgery[(fresh_CTL_Surgery['barcode_sample_id'].str.contains('FreshAC8'))]

    fixed_CTL_Surgery = fixed_qt[(fixed_qt['barcode_subject_type'].str.contains('CTL_Surgery')) ]

    fixed_CTL_Surgery_TI1 = fixed_CTL_Surgery[(fixed_CTL_Surgery['barcode_sample_id'].str.contains('FixedTI1'))]
    fixed_CTL_Surgery_TI2 = fixed_CTL_Surgery[(fixed_CTL_Surgery['barcode_sample_id'].str.contains('FixedTI2'))]
    fixed_CTL_Surgery_TI3 = fixed_CTL_Surgery[(fixed_CTL_Surgery['barcode_sample_id'].str.contains('FixedTI3'))]
    fixed_CTL_Surgery_AC4 = fixed_CTL_Surgery[(fixed_CTL_Surgery['barcode_sample_id'].str.contains('FixedAC4'))]
    fixed_CTL_Surgery_AC5 = fixed_CTL_Surgery[(fixed_CTL_Surgery['barcode_sample_id'].str.contains('FixedAC5'))]
    fixed_CTL_Surgery_AC6 = fixed_CTL_Surgery[(fixed_CTL_Surgery['barcode_sample_id'].str.contains('FixedAC6'))]
    fixed_CTL_Surgery_AC7 = fixed_CTL_Surgery[(fixed_CTL_Surgery['barcode_sample_id'].str.contains('FixedAC7'))]
    fixed_CTL_Surgery_AC8 = fixed_CTL_Surgery[(fixed_CTL_Surgery['barcode_sample_id'].str.contains('FixedAC8'))]

    frozen_CTL_Surgery = frozen_qt[(frozen_qt['barcode_subject_type'].str.contains('CTL_Surgery')) ]

    frozen_CTL_Surgery_TI1_ONLY = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenTI1')) &
            (~frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenTI1'))]

    frozen_CTL_Surgery_TI1_ADD = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenTI1')) &
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenTI1'))]

    frozen_CTL_Surgery_TI2_ONLY = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenTI2')) &
            (~frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenTI2'))]

    frozen_CTL_Surgery_TI2_ADD = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenTI2')) &
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenTI2'))]

    frozen_CTL_Surgery_TI3_ONLY = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenTI3')) &
            (~frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenTI3'))]

    frozen_CTL_Surgery_TI3_ADD = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenTI3')) &
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenTI3'))]

    frozen_CTL_Surgery_AC4_ONLY = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC4')) &
            (~frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC4'))]

    frozen_CTL_Surgery_AC4_ADD = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC4')) &
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC4'))]

    frozen_CTL_Surgery_AC5_ONLY = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC5')) &
            (~frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC5'))]

    frozen_CTL_Surgery_AC5_ADD = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC5')) &
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC5'))]

    frozen_CTL_Surgery_AC6_ONLY = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC6')) &
            (~frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC6'))]

    frozen_CTL_Surgery_AC6_ADD = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC6')) &
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC6'))]

    frozen_CTL_Surgery_AC7_ONLY = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC7')) &
            (~frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC7'))]

    frozen_CTL_Surgery_AC7_ADD = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC7')) &
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC7'))]

    frozen_CTL_Surgery_AC8_ONLY = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC8')) &
            (~frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC8'))]

    frozen_CTL_Surgery_AC8_ADD = frozen_CTL_Surgery[
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('FrozenAC8')) &
            (frozen_CTL_Surgery['barcode_sample_id'].str.contains('ADDFrozenAC8'))]

    stats_hope = {'Study_type':['CD_ENDO','','','','CTL_ENDO','','CD_Surgery','','CTL_Surgery','','','','','','','','TOTAL'],
                  'Biopsies_type':['TIA','TIB','ACA','ACB','TI','AC','TI','AC','TI1','TI2','TI3','AC4','AC5','AC6','AC7','AC8',''],
                  'Fresh':[fresh_CD_ENDO_TIA.shape[0],fresh_CD_ENDO_TIB.shape[0],fresh_CD_ENDO_ACA.shape[0],fresh_CD_ENDO_ACB.shape[0],fresh_CTL_ENDO_TI.shape[0],fresh_CTL_ENDO_AC.shape[0],fresh_CD_Surgery_TI.shape[0],fresh_CD_Surgery_AC.shape[0],fresh_CTL_Surgery_TI1.shape[0],fresh_CTL_Surgery_TI2.shape[0],fresh_CTL_Surgery_TI3.shape[0],fresh_CTL_Surgery_AC4.shape[0],fresh_CTL_Surgery_AC5.shape[0],fresh_CTL_Surgery_AC6.shape[0],fresh_CTL_Surgery_AC7.shape[0],fresh_CTL_Surgery_AC8.shape[0],
                          fresh_CD_ENDO_TIA.shape[0]+fresh_CD_ENDO_TIB.shape[0]+fresh_CD_ENDO_ACA.shape[0]+fresh_CD_ENDO_ACB.shape[0]+fresh_CTL_ENDO_TI.shape[0]+fresh_CTL_ENDO_AC.shape[0]+fresh_CD_Surgery_TI.shape[0]+fresh_CD_Surgery_AC.shape[0]+fresh_CTL_Surgery_TI1.shape[0]+fresh_CTL_Surgery_TI2.shape[0]+fresh_CTL_Surgery_TI3.shape[0]+fresh_CTL_Surgery_AC4.shape[0]+fresh_CTL_Surgery_AC5.shape[0]+fresh_CTL_Surgery_AC6.shape[0]+fresh_CTL_Surgery_AC7.shape[0]+fresh_CTL_Surgery_AC8.shape[0]],
                  'Fixed':[fixed_CD_ENDO_TIA.shape[0],fixed_CD_ENDO_TIB.shape[0],fixed_CD_ENDO_ACA.shape[0],fixed_CD_ENDO_ACB.shape[0],fixed_CTL_ENDO_TI.shape[0],fixed_CTL_ENDO_AC.shape[0],fixed_CD_Surgery_TI.shape[0],fixed_CD_Surgery_AC.shape[0],fixed_CTL_Surgery_TI1.shape[0],fixed_CTL_Surgery_TI2.shape[0],fixed_CTL_Surgery_TI3.shape[0],fixed_CTL_Surgery_AC4.shape[0],fixed_CTL_Surgery_AC5.shape[0],fixed_CTL_Surgery_AC6.shape[0],fixed_CTL_Surgery_AC7.shape[0],fixed_CTL_Surgery_AC8.shape[0],
                          fixed_CD_ENDO_TIA.shape[0]+fixed_CD_ENDO_TIB.shape[0]+fixed_CD_ENDO_ACA.shape[0]+fixed_CD_ENDO_ACB.shape[0]+fixed_CTL_ENDO_TI.shape[0]+fixed_CTL_ENDO_AC.shape[0]+fixed_CD_Surgery_TI.shape[0]+fixed_CD_Surgery_AC.shape[0]+fixed_CTL_Surgery_TI1.shape[0]+fixed_CTL_Surgery_TI2.shape[0]+fixed_CTL_Surgery_TI3.shape[0]+fixed_CTL_Surgery_AC4.shape[0]+fixed_CTL_Surgery_AC5.shape[0]+fixed_CTL_Surgery_AC6.shape[0]+fixed_CTL_Surgery_AC7.shape[0]+fixed_CTL_Surgery_AC8.shape[0]],
                  'Frozen':[frozen_CD_ENDO_TIA_ONLY.shape[0],frozen_CD_ENDO_TIB_ONLY.shape[0],frozen_CD_ENDO_ACA_ONLY.shape[0],frozen_CD_ENDO_ACB_ONLY.shape[0],frozen_CTL_ENDO_TI_ONLY.shape[0],frozen_CTL_ENDO_AC_ONLY.shape[0],frozen_CD_Surgery_TI_ONLY.shape[0],frozen_CD_Surgery_AC_ONLY.shape[0],frozen_CTL_Surgery_TI1_ONLY.shape[0],frozen_CTL_Surgery_TI2_ONLY.shape[0],frozen_CTL_Surgery_TI3_ONLY.shape[0],frozen_CTL_Surgery_AC4_ONLY.shape[0],frozen_CTL_Surgery_AC5_ONLY.shape[0],frozen_CTL_Surgery_AC6_ONLY.shape[0],frozen_CTL_Surgery_AC7_ONLY.shape[0],frozen_CTL_Surgery_AC8_ONLY.shape[0],
                           frozen_CD_ENDO_TIA_ONLY.shape[0]+frozen_CD_ENDO_TIB_ONLY.shape[0]+frozen_CD_ENDO_ACA_ONLY.shape[0]+frozen_CD_ENDO_ACB_ONLY.shape[0]+frozen_CTL_ENDO_TI_ONLY.shape[0]+frozen_CTL_ENDO_AC_ONLY.shape[0]+frozen_CD_Surgery_TI_ONLY.shape[0]+frozen_CD_Surgery_AC_ONLY.shape[0]+frozen_CTL_Surgery_TI1_ONLY.shape[0]+frozen_CTL_Surgery_TI2_ONLY.shape[0]+frozen_CTL_Surgery_TI3_ONLY.shape[0]+frozen_CTL_Surgery_AC4_ONLY.shape[0]+frozen_CTL_Surgery_AC5_ONLY.shape[0]+frozen_CTL_Surgery_AC6_ONLY.shape[0]+frozen_CTL_Surgery_AC7_ONLY.shape[0]+frozen_CTL_Surgery_AC8_ONLY.shape[0]],
                  'Add_Frozen':[frozen_CD_ENDO_TIA_ADD.shape[0],frozen_CD_ENDO_TIB_ADD.shape[0],frozen_CD_ENDO_ACA_ADD.shape[0],frozen_CD_ENDO_ACB_ADD.shape[0],frozen_CTL_ENDO_TI_ADD.shape[0],frozen_CTL_ENDO_AC_ADD.shape[0],frozen_CD_Surgery_TI_ADD.shape[0],frozen_CD_Surgery_AC_ADD.shape[0],frozen_CTL_Surgery_TI1_ADD.shape[0],frozen_CTL_Surgery_TI2_ADD.shape[0],frozen_CTL_Surgery_TI3_ADD.shape[0],frozen_CTL_Surgery_AC4_ADD.shape[0],frozen_CTL_Surgery_AC5_ADD.shape[0],frozen_CTL_Surgery_AC6_ADD.shape[0],frozen_CTL_Surgery_AC7_ADD.shape[0],frozen_CTL_Surgery_AC8_ADD.shape[0],
                               frozen_CD_ENDO_TIA_ADD.shape[0]+frozen_CD_ENDO_TIB_ADD.shape[0]+frozen_CD_ENDO_ACA_ADD.shape[0]+frozen_CD_ENDO_ACB_ADD.shape[0]+frozen_CTL_ENDO_TI_ADD.shape[0]+frozen_CTL_ENDO_AC_ADD.shape[0]+frozen_CD_Surgery_TI_ADD.shape[0]+frozen_CD_Surgery_AC_ADD.shape[0]+frozen_CTL_Surgery_TI1_ADD.shape[0]+frozen_CTL_Surgery_TI2_ADD.shape[0]+frozen_CTL_Surgery_TI3_ADD.shape[0]+frozen_CTL_Surgery_AC4_ADD.shape[0]+frozen_CTL_Surgery_AC5_ADD.shape[0]+frozen_CTL_Surgery_AC6_ADD.shape[0]+frozen_CTL_Surgery_AC7_ADD.shape[0]+frozen_CTL_Surgery_AC8_ADD.shape[0]]   
    }

    df_result_HOPE = pd.DataFrame(data=stats_hope)

    # get sub total for Sophie...
    stats_hope_sub = {'Study_type':['CD_ENDO','CTL_ENDO','CD_Surgery','CTL_Surgery'],
                  'Fresh':[fresh_CD_ENDO_TIA.shape[0]+fresh_CD_ENDO_TIB.shape[0]+fresh_CD_ENDO_ACA.shape[0]+fresh_CD_ENDO_ACB.shape[0],fresh_CTL_ENDO_TI.shape[0]+fresh_CTL_ENDO_AC.shape[0],fresh_CD_Surgery_TI.shape[0]+fresh_CD_Surgery_AC.shape[0],fresh_CTL_Surgery_TI1.shape[0]+fresh_CTL_Surgery_TI2.shape[0]+fresh_CTL_Surgery_TI3.shape[0]+fresh_CTL_Surgery_AC4.shape[0]+fresh_CTL_Surgery_AC5.shape[0]+fresh_CTL_Surgery_AC6.shape[0]+fresh_CTL_Surgery_AC7.shape[0]+fresh_CTL_Surgery_AC8.shape[0]],
                  'Fixed':[fixed_CD_ENDO_TIA.shape[0]+fixed_CD_ENDO_TIB.shape[0]+fixed_CD_ENDO_ACA.shape[0]+fixed_CD_ENDO_ACB.shape[0],fixed_CTL_ENDO_TI.shape[0]+fixed_CTL_ENDO_AC.shape[0],fixed_CD_Surgery_TI.shape[0]+fixed_CD_Surgery_AC.shape[0],fixed_CTL_Surgery_TI1.shape[0]+fixed_CTL_Surgery_TI2.shape[0]+fixed_CTL_Surgery_TI3.shape[0]+fixed_CTL_Surgery_AC4.shape[0]+fixed_CTL_Surgery_AC5.shape[0]+fixed_CTL_Surgery_AC6.shape[0]+fixed_CTL_Surgery_AC7.shape[0]+fixed_CTL_Surgery_AC8.shape[0]],
                  'Frozen':[frozen_CD_ENDO_TIA_ONLY.shape[0]+frozen_CD_ENDO_TIB_ONLY.shape[0]+frozen_CD_ENDO_ACA_ONLY.shape[0]+frozen_CD_ENDO_ACB_ONLY.shape[0],frozen_CTL_ENDO_TI_ONLY.shape[0]+frozen_CTL_ENDO_AC_ONLY.shape[0],frozen_CD_Surgery_TI_ONLY.shape[0]+frozen_CD_Surgery_AC_ONLY.shape[0],frozen_CTL_Surgery_TI1_ONLY.shape[0]+frozen_CTL_Surgery_TI2_ONLY.shape[0]+frozen_CTL_Surgery_TI3_ONLY.shape[0]+frozen_CTL_Surgery_AC4_ONLY.shape[0]+frozen_CTL_Surgery_AC5_ONLY.shape[0]+frozen_CTL_Surgery_AC6_ONLY.shape[0]+frozen_CTL_Surgery_AC7_ONLY.shape[0]+frozen_CTL_Surgery_AC8_ONLY.shape[0]],
                  'Add_Frozen':[frozen_CD_ENDO_TIA_ADD.shape[0]+frozen_CD_ENDO_TIB_ADD.shape[0]+frozen_CD_ENDO_ACA_ADD.shape[0]+frozen_CD_ENDO_ACB_ADD.shape[0],frozen_CTL_ENDO_TI_ADD.shape[0]+frozen_CTL_ENDO_AC_ADD.shape[0],frozen_CD_Surgery_TI_ADD.shape[0]+frozen_CD_Surgery_AC_ADD.shape[0],frozen_CTL_Surgery_TI1_ADD.shape[0]+frozen_CTL_Surgery_TI2_ADD.shape[0]+frozen_CTL_Surgery_TI3_ADD.shape[0]+frozen_CTL_Surgery_AC4_ADD.shape[0]+frozen_CTL_Surgery_AC5_ADD.shape[0]+frozen_CTL_Surgery_AC6_ADD.shape[0]+frozen_CTL_Surgery_AC7_ADD.shape[0]+frozen_CTL_Surgery_AC8_ADD.shape[0]],
                  'Total':[fresh_CD_ENDO_TIA.shape[0]+fresh_CD_ENDO_TIB.shape[0]+fresh_CD_ENDO_ACA.shape[0]+fresh_CD_ENDO_ACB.shape[0]+fixed_CD_ENDO_TIA.shape[0]+fixed_CD_ENDO_TIB.shape[0]+fixed_CD_ENDO_ACA.shape[0]+fixed_CD_ENDO_ACB.shape[0]+frozen_CD_ENDO_TIA_ONLY.shape[0]+frozen_CD_ENDO_TIB_ONLY.shape[0]+frozen_CD_ENDO_ACA_ONLY.shape[0]+frozen_CD_ENDO_ACB_ONLY.shape[0]+frozen_CD_ENDO_TIA_ADD.shape[0]+frozen_CD_ENDO_TIB_ADD.shape[0]+frozen_CD_ENDO_ACA_ADD.shape[0]+frozen_CD_ENDO_ACB_ADD.shape[0],
                          fresh_CTL_ENDO_TI.shape[0]+fresh_CTL_ENDO_AC.shape[0]+fixed_CTL_ENDO_TI.shape[0]+fixed_CTL_ENDO_AC.shape[0]+frozen_CTL_ENDO_TI_ONLY.shape[0]+frozen_CTL_ENDO_AC_ONLY.shape[0]+frozen_CTL_ENDO_TI_ADD.shape[0]+frozen_CTL_ENDO_AC_ADD.shape[0],
                          fresh_CD_Surgery_TI.shape[0]+fresh_CD_Surgery_AC.shape[0] + fixed_CD_Surgery_TI.shape[0]+fixed_CD_Surgery_AC.shape[0] + frozen_CD_Surgery_TI_ONLY.shape[0]+frozen_CD_Surgery_AC_ONLY.shape[0] + frozen_CD_Surgery_TI_ADD.shape[0]+frozen_CD_Surgery_AC_ADD.shape[0],
                          fresh_CTL_Surgery_TI1.shape[0]+fresh_CTL_Surgery_TI2.shape[0]+fresh_CTL_Surgery_TI3.shape[0]+fresh_CTL_Surgery_AC4.shape[0]+fresh_CTL_Surgery_AC5.shape[0]+fresh_CTL_Surgery_AC6.shape[0]+fresh_CTL_Surgery_AC7.shape[0]+fresh_CTL_Surgery_AC8.shape[0]+fixed_CTL_Surgery_TI1.shape[0]+fixed_CTL_Surgery_TI2.shape[0]+fixed_CTL_Surgery_TI3.shape[0]+fixed_CTL_Surgery_AC4.shape[0]+fixed_CTL_Surgery_AC5.shape[0]+fixed_CTL_Surgery_AC6.shape[0]+fixed_CTL_Surgery_AC7.shape[0]+fixed_CTL_Surgery_AC8.shape[0]+frozen_CTL_Surgery_TI1_ONLY.shape[0]+frozen_CTL_Surgery_TI2_ONLY.shape[0]+frozen_CTL_Surgery_TI3_ONLY.shape[0]+frozen_CTL_Surgery_AC4_ONLY.shape[0]+frozen_CTL_Surgery_AC5_ONLY.shape[0]+frozen_CTL_Surgery_AC6_ONLY.shape[0]+frozen_CTL_Surgery_AC7_ONLY.shape[0]+frozen_CTL_Surgery_AC8_ONLY.shape[0]+frozen_CTL_Surgery_TI1_ADD.shape[0]+frozen_CTL_Surgery_TI2_ADD.shape[0]+frozen_CTL_Surgery_TI3_ADD.shape[0]+frozen_CTL_Surgery_AC4_ADD.shape[0]+frozen_CTL_Surgery_AC5_ADD.shape[0]+frozen_CTL_Surgery_AC6_ADD.shape[0]+frozen_CTL_Surgery_AC7_ADD.shape[0]+frozen_CTL_Surgery_AC8_ADD.shape[0]]
    }

    df_result_HOPE_sub = pd.DataFrame(data=stats_hope_sub)

    fresh_TI = fresh_qt[(fresh_qt['barcode_sample_id'].str.contains('TI'))]
    fixed_TI = fixed_qt[(fixed_qt['barcode_sample_id'].str.contains('TI'))]
    frozen_TI = frozen_qt[(frozen_qt['barcode_sample_id'].str.contains('TI'))]

    fresh_AC = fresh_qt[(fresh_qt['barcode_sample_id'].str.contains('AC'))]
    fixed_AC = fixed_qt[(fixed_qt['barcode_sample_id'].str.contains('AC'))]
    frozen_AC = frozen_qt[(frozen_qt['barcode_sample_id'].str.contains('AC'))]

    stats_total = {'TI':[fresh_TI.shape[0] + fixed_TI.shape[0] + frozen_TI.shape[0]],
                   'AC':[fresh_AC.shape[0] + fixed_AC.shape[0] + frozen_AC.shape[0]],
                   'TOTAL' :[fresh_TI.shape[0] + fixed_TI.shape[0] + frozen_TI.shape[0] + fresh_AC.shape[0] + fixed_AC.shape[0] + frozen_AC.shape[0]]}

    df_result_TOTAL = pd.DataFrame(data=stats_total)
    with open('/var/www/html/shunxing/gca/summary/biopsies_stats.txt','w') as outfile:
        outfile.write('Overview of biopsies storage:\n\n')
        df_result_HOPE.to_string(outfile,index = False)
        outfile.write('\n\nSub-total of biopsies storage:\n')
        df_result_HOPE_sub.to_string(outfile,index = False)
        outfile.write('\n\nTotal of biopsies collected:\n')
        df_result_TOTAL.to_string(outfile,index = False)

def overview_freezer_storage(project):
    dataset = project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id','barcode_action_type','barcode_action_date','barcode_processed_by','barcode_freezer','barcode_rack','barcode_box_id','barcode_box_position'])
    df = pd.DataFrame.from_dict(dataset)


    query_table = df[
            (df['barcode_action_type'].str.contains('distributed')) |
            (df['barcode_action_type'].str.contains('stored in rack')) |
            (df['barcode_action_type'].str.contains('printed')) |
            (df['barcode_action_type'].str.contains('Re-print')) |
            (df['barcode_action_type'].str.contains('Barcode destroyed')) ] \
            .drop_duplicates(subset=['barcode_sample_id'], keep="last")

    qt = query_table[(query_table['barcode_action_type'].str.contains('stored in rack'))]

    df_uniq_full = qt[['barcode_freezer','barcode_rack','barcode_box_id','barcode_box_position','barcode_sample_id','barcode_action_date','barcode_processed_by']]

    df_uniq_full.barcode_box_id = pd.to_numeric(df_uniq_full.barcode_box_id, errors='coerce')
    df_uniq_full.barcode_box_position = pd.to_numeric(df_uniq_full.barcode_box_position, errors='coerce')

    boxInfo = df_uniq_full.sort_values(['barcode_rack', 'barcode_box_id', 'barcode_box_position'], ascending=[True, True, True])

    rack_uniq = set(boxInfo['barcode_rack'].to_list())
    box_id_uniq = set(boxInfo['barcode_box_id'].to_list())
    rack_uniq.remove('')    

    for tmp_rack in rack_uniq:
        for tmp_box_id in box_id_uniq:
            my_df_tmp = boxInfo[boxInfo['barcode_rack'].str.contains(tmp_rack)]
            my_df = my_df_tmp[my_df_tmp['barcode_box_id'].astype(str).str.contains(str(tmp_box_id))]
            if(len(my_df) > 0):
                my_df.to_csv (r'/var/www/html/shunxing/gca/summary/freezer_stats/FreezerC_Rack%s_Box%s.txt'% (tmp_rack,tmp_box_id), index = False, header=True)
            
            
#     x = df_uniq_full.sort_values(['barcode_rack', 'barcode_box_id', 'barcode_box_position'], ascending=[True, True, True])

    with open('/var/www/html/shunxing/gca/summary/freezer_stats.txt','w') as outfile:
        outfile.write('Overview of freezer storage:\n\n')
        boxInfo.to_string(outfile,index = False)
        
def quality_control(project):
    all_data = project.export_records()
    df_all = pd.DataFrame.from_dict(all_data)

    dataset = project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id','barcode_subject_type','barcode_action_type'])
    df = pd.DataFrame.from_dict(dataset)

    query_table = df[
            (df['barcode_action_type'].str.contains('distributed')) |
            (df['barcode_action_type'].str.contains('stored in rack')) |
            (df['barcode_action_type'].str.contains('printed')) |
            (df['barcode_action_type'].str.contains('Re-print')) |
            (df['barcode_action_type'].str.contains('Barcode destroyed')) ] \
            .drop_duplicates(subset=['barcode_sample_id'], keep="last")

    query_table_collected = query_table[
        (query_table['barcode_action_type'].str.contains('stored in rack')) |
        (query_table['barcode_action_type'].str.contains('distributed'))]

    fresh_qt = query_table_collected[(query_table_collected['barcode_action_type'].str.contains('Fresh distributed to Lau'))]
    fixed_qt = query_table_collected[(query_table_collected['barcode_action_type'].str.contains('Fixed distributed to TPSR'))]
    frozen_qt = query_table_collected[(query_table_collected['barcode_action_type'].str.contains('Frozen stored in rack'))]

    query_table_destroyed = query_table[query_table['barcode_action_type'].str.contains('Barcode destroyed')]

    df_sample_id = df[['barcode_sample_id']]
    df_subject_id = set(df_sample_id['barcode_sample_id'].str[3:6].to_list())

    with open('/var/www/html/shunxing/gca/summary/quality_control.txt','w') as outfile:
        outfile.write('Quality control\n')
        outfile.write('\nSample output:')
        outfile.write('\n>>>Subject xxx')
        outfile.write('\n>>>There should be no stool collection, please select no in stool collected field.')
        outfile.write('\n>>>There should be no serum collection, please select no in serum collected field.')
        outfile.write('\n>>>There should be no DNA collection, please select no in DNA collected field.')
        outfile.write('\n>>>There should be no FreshTIA, please unclick the checkbox')
        outfile.write('\n>>>Collected ADDFrozenTIA, please click the checkbox')
        outfile.write('\n>>>......')

        for val in sorted(df_subject_id):
            # Stool
            if val == '999':
                continue

            outfile.write('\n\nSubject %s:\n' % val)
            to_print = [];

            tmp_subject =  df_all[df_all['record_id_dem_endo'] == str(int(val))]
            my_df_destroyed = query_table_destroyed[query_table_destroyed['barcode_sample_id'].str.contains(val)]


            if len(my_df_destroyed) > 0:

                # Stool
                my_df_destroyed_stool = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('ST')]
                if my_df_destroyed_stool.shape[0] == 4:                
                    if tmp_subject.iloc[0]['stool_collected_endo_cd_v2'] is not '0':
                        to_print.append('There should be no stool collection, please select no in stool collected field.\n')

                # Sreum
                my_df_destroyed_serum = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('SR')]
                if my_df_destroyed_serum.shape[0] == 8 or my_df_destroyed_serum.shape[0] == 11  :                
                    if tmp_subject.iloc[0]['serum_collected_endo_cd_v2'] is not '0':
                        to_print.append('There should be no serum collection, please select no in serum collected field.\n')

                # DNA
                my_df_destroyed_DNA = my_df_destroyed[my_df_destroyed['barcode_sample_id'].str.contains('DNA')]
                if my_df_destroyed_DNA.shape[0] == 1  :   
                    if tmp_subject.iloc[0]['dna_collected_endo_cd_v2'] is not '0':
                        to_print.append('There should be no DNA collection, please select no in DBA collected field.\n')

                # CD_ENDO
                fresh_CD_ENDO = my_df_destroyed[(my_df_destroyed['barcode_subject_type'].str.contains('CD_ENDO')) ]

                if fresh_CD_ENDO.shape[0] > 0:
                    fresh_CD_ENDO_TIA = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshTIA'))]
                    if fresh_CD_ENDO_TIA.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_involved_a_v2___1'] is not '0':
                            to_print.append('There should be no FreshTIA, please unclick the checkbox\n')

                    fresh_CD_ENDO_TIB = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshTIB'))]
                    if fresh_CD_ENDO_TIB.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_non_involved_b_v2___1'] is not '0':
                            to_print.append('There should be no FreshTIB, please unclick the checkbox\n')

                    fresh_CD_ENDO_ACA = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshACA'))]
                    if fresh_CD_ENDO_ACA.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_involved___1'] is not '0':
                            to_print.append('There should be no FreshACA, please unclick the checkbox\n')

                    fresh_CD_ENDO_ACB = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshACB'))]
                    if fresh_CD_ENDO_ACB.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_non_involved___1'] is not '0':
                            to_print.append('There should be no FreshACB, please unclick the checkbox\n')

                fixed_CD_ENDO = my_df_destroyed[(my_df_destroyed['barcode_subject_type'].str.contains('CD_ENDO')) ]
                if fixed_CD_ENDO.shape[0] > 0:
                    fixed_CD_ENDO_TIA = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedTIA'))]
                    if fixed_CD_ENDO_TIA.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_involved_a_v2___2'] is not '0':
                            to_print.append('There should be no FixedTIA, please unclick the checkbox\n') 

                    fixed_CD_ENDO_TIB = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedTIB'))]
                    if fixed_CD_ENDO_TIB.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_non_involved_b_v2___2'] is not '0':
                            to_print.append('There should be no FixedTIB, please unclick the checkbox\n') 

                    fixed_CD_ENDO_ACA = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedACA'))]
                    if fixed_CD_ENDO_ACA.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_involved___2'] is not '0':
                            to_print.append('There should be no FixedACA, please unclick the checkbox\n')
                    fixed_CD_ENDO_ACB = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedACB'))]
                    if fixed_CD_ENDO_ACB.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_non_involved___2'] is not '0':
                            to_print.append('There should be no FixedACB, please unclick the checkbox\n')

                frozen_CD_ENDO = my_df_destroyed[(my_df_destroyed['barcode_subject_type'].str.contains('CD_ENDO')) ]
                if frozen_CD_ENDO.shape[0] > 0:
                    frozen_CD_ENDO_TIA_ONLY = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIA')) &
                            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIA'))]
                    if frozen_CD_ENDO_TIA_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_involved_a_v2___3'] is not '0':
                            to_print.append('There should be no FrozenTIA, please unclick the checkbox\n')

                    frozen_CD_ENDO_TIA_ADD = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIA')) &
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIA'))]
                    if frozen_CD_ENDO_TIA_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_involved_a_v2___4'] is not '0':
                            to_print.append('There should be no ADDFrozenTIA, please unclick the checkbox\n')

                    frozen_CD_ENDO_TIB_ONLY = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIB')) &
                            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIB'))]
                    if frozen_CD_ENDO_TIB_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_non_involved_b_v2___3'] is not '0':
                            to_print.append('There should be no FrozenTIB, please unclick the checkbox\n') 

                    frozen_CD_ENDO_TIB_ADD = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIB')) &
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIB'))]
                    if frozen_CD_ENDO_TIB_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_non_involved_b_v2___4'] is not '0':
                            to_print.append('There should be no ADDFrozenTIB, please unclick the checkbox\n') 

                    frozen_CD_ENDO_ACA_ONLY = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACA')) &
                            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACA'))]
                    if frozen_CD_ENDO_ACA_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_involved___3'] is not '0':
                            to_print.append('There should be no FrozenACA, please unclick the checkbox\n')

                    frozen_CD_ENDO_ACA_ADD = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACA')) &
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACA'))]
                    if frozen_CD_ENDO_ACA_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_involved___4'] is not '0':
                            to_print.append('There should be no ADDFrozenACA, please unclick checkbox\n')

                    frozen_CD_ENDO_ACB_ONLY = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACB')) &
                            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACB'))]

                    if frozen_CD_ENDO_ACB_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_non_involved___3'] is not '0':
                            to_print.append('There should be no FrozenACB, please unclick the checkbox\n')

                    frozen_CD_ENDO_ACB_ADD = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACB')) &
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACB'))]
                    if frozen_CD_ENDO_ACB_ADD.shape[0] == 1  :  
                        print(frozen_CD_ENDO_ACB_ADD)
                        if tmp_subject.iloc[0]['ac_non_involved___4'] is not '0':
                            to_print.append('There should be no ADDFrozenACB, please unclick the checkbox\n')

                # CTL_ENDO
                fresh_CTL_ENDO = my_df_destroyed[(my_df_destroyed['barcode_subject_type'].str.contains('CTL_ENDO')) ]

                if fresh_CTL_ENDO.shape[0] > 0: 
                    fresh_CTL_ENDO_TI = fresh_CTL_ENDO[(fresh_CTL_ENDO['barcode_sample_id'].str.contains('FreshTI'))]
                    if fresh_CTL_ENDO_TI.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ti___1'] is not '0':
                            to_print.append('There should be no FreshTI, please unclick the checkbox\n')

                    fresh_CTL_ENDO_AC = fresh_CTL_ENDO[(fresh_CTL_ENDO['barcode_sample_id'].str.contains('FreshAC'))]
                    if fresh_CTL_ENDO_AC.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ac___1'] is not '0':
                            to_print.append('There should be no FreshAC, please unclick the checkbox\n')

                fixed_CTL_ENDO = my_df_destroyed[(my_df_destroyed['barcode_subject_type'].str.contains('CTL_ENDO')) ]
                if fixed_CTL_ENDO.shape[0] > 0:
                    fixed_CTL_ENDO_TI = fixed_CTL_ENDO[(fixed_CTL_ENDO['barcode_sample_id'].str.contains('FixedTI'))]
                    if fixed_CTL_ENDO_TI.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ti___2'] is not '0':
                            to_print.append('There should be no FreshTI, please unclick the checkbox\n')

                    fixed_CTL_ENDO_AC = fixed_CTL_ENDO[(fixed_CTL_ENDO['barcode_sample_id'].str.contains('FixedAC'))]
                    if fixed_CTL_ENDO_AC.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ac___2'] is not '0':
                            to_print.append('There should be no FreshAC, please unclick the checkbox\n')


                frozen_CTL_ENDO = my_df_destroyed[(my_df_destroyed['barcode_subject_type'].str.contains('CTL_ENDO')) ]
                if frozen_CTL_ENDO.shape[0] > 0:
                    frozen_CTL_ENDO_TI_ONLY = frozen_CTL_ENDO[
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenTI')) &
                            (~frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenTI'))]                
                    if frozen_CTL_ENDO_TI_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ti___3'] is not '0':
                            to_print.append('There should be no FrozenTI, please unclick the checkbox\n')

                    frozen_CTL_ENDO_TI_ADD = frozen_CTL_ENDO[
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenTI')) &
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenTI'))]                
                    if frozen_CTL_ENDO_TI_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ti___4'] is not '0':
                            to_print.append('There should be no ADDFrozenTI, please unclick the checkbox\n')

                    frozen_CTL_ENDO_AC_ONLY = frozen_CTL_ENDO[
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenAC')) &
                            (~frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenAC'))]
                    if frozen_CTL_ENDO_AC_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ac___3'] is not '0':
                            to_print.append('There should be no FrozenAC, please unclick the checkbox\n')

                    frozen_CTL_ENDO_AC_ADD = frozen_CTL_ENDO[
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenAC')) &
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenAC'))] 
                    if frozen_CTL_ENDO_AC_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ac___4'] is not '0':
                            to_print.append('There should be no ADDFrozenAC, please unclick the checkbox\n')

    # CHECK COLLECTED
            my_fresh_df_collected = fresh_qt[fresh_qt['barcode_sample_id'].str.contains(val)]
            my_fixed_df_collected = fixed_qt[fixed_qt['barcode_sample_id'].str.contains(val)]
            my_frozen_df_collected = frozen_qt[frozen_qt['barcode_sample_id'].str.contains(val)]
            if len(my_fresh_df_collected) > 0:
                # CD_ENDO
                fresh_CD_ENDO = my_fresh_df_collected[(my_fresh_df_collected['barcode_subject_type'].str.contains('CD_ENDO')) ]

                if fresh_CD_ENDO.shape[0] > 0:
                    fresh_CD_ENDO_TIA = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshTIA'))]
                    if fresh_CD_ENDO_TIA.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_involved_a_v2___1'] is not '1':
                            to_print.append('Collected FreshTIA, please click checkbox\n')

                    fresh_CD_ENDO_TIB = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshTIB'))]
                    if fresh_CD_ENDO_TIB.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_non_involved_b_v2___1'] is not '1':
                            to_print.append('Collected FreshTIB, please click checkbox\n')

                    fresh_CD_ENDO_ACA = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshACA'))]
                    if fresh_CD_ENDO_ACA.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_involved___1'] is not '1':
                            to_print.append('Collected FreshACA, please click checkbox\n')

                    fresh_CD_ENDO_ACB = fresh_CD_ENDO[(fresh_CD_ENDO['barcode_sample_id'].str.contains('FreshACB'))]
                    if fresh_CD_ENDO_ACB.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_non_involved___1'] is not '1':
                            to_print.append('Collected FreshACB, please click checkbox\n')


            if len(my_fixed_df_collected) > 0:                        
                fixed_CD_ENDO = my_fixed_df_collected[(my_fixed_df_collected['barcode_subject_type'].str.contains('CD_ENDO')) ]
                if fixed_CD_ENDO.shape[0] > 0:
                    fixed_CD_ENDO_TIA = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedTIA'))]
                    if fixed_CD_ENDO_TIA.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_involved_a_v2___2'] is not '1':
                            to_print.append('Collected FixedTIA, please click checkbox\n') 

                    fixed_CD_ENDO_TIB = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedTIB'))]
                    if fixed_CD_ENDO_TIB.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_non_involved_b_v2___2'] is not '1':
                            to_print.append('Collected FixedTIB, please click checkbox\n') 

                    fixed_CD_ENDO_ACA = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedACA'))]
                    if fixed_CD_ENDO_ACA.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_involved___2'] is not '1':
                            to_print.append('Collected FixedACA, please click checkbox\n')
                    fixed_CD_ENDO_ACB = fixed_CD_ENDO[(fixed_CD_ENDO['barcode_sample_id'].str.contains('FixedACB'))]
                    if fixed_CD_ENDO_ACB.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_non_involved___2'] is not '1':
                            to_print.append('Collected FixedACB, please click checkbox\n')


            if len(my_frozen_df_collected) > 0:                           
                frozen_CD_ENDO = my_frozen_df_collected[(my_frozen_df_collected['barcode_subject_type'].str.contains('CD_ENDO')) ]
                if frozen_CD_ENDO.shape[0] > 0:
                    frozen_CD_ENDO_TIA_ONLY = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIA')) &
                            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIA'))]
                    if frozen_CD_ENDO_TIA_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_involved_a_v2___3'] is not '1':
                            to_print.append('Collected FrozenTIA, please click checkbox\n')

                    frozen_CD_ENDO_TIA_ADD = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIA')) &
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIA'))]
                    if frozen_CD_ENDO_TIA_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_involved_a_v2___4'] is not '1':
                            to_print.append('Collected ADDFrozenTIA, please click checkbox\n')

                    frozen_CD_ENDO_TIB_ONLY = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIB')) &
                            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIB'))]
                    if frozen_CD_ENDO_TIB_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_non_involved_b_v2___3'] is not '1':
                            to_print.append('Collected FrozenTIB, please click checkbox\n') 

                    frozen_CD_ENDO_TIB_ADD = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenTIB')) &
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenTIB'))]
                    if frozen_CD_ENDO_TIB_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ti_non_involved_b_v2___4'] is not '1':
                            to_print.append('Collected ADDFrozenTIB, please click checkbox\n') 

                    frozen_CD_ENDO_ACA_ONLY = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACA')) &
                            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACA'))]
                    if frozen_CD_ENDO_ACA_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_involved___3'] is not '1':
                            to_print.append('Collected FrozenACA, please click checkbox\n')

                    frozen_CD_ENDO_ACA_ADD = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACA')) &
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACA'))]
                    if frozen_CD_ENDO_ACA_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_involved___4'] is not '1':
                            to_print.append('Collected ADDFrozenACA, please click checkbox\n')

                    frozen_CD_ENDO_ACB_ONLY = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACB')) &
                            (~frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACB'))]

                    if frozen_CD_ENDO_ACB_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['ac_non_involved___3'] is not '1':
                            to_print.append('Collected FrozenACB, please click checkbox\n')

                    frozen_CD_ENDO_ACB_ADD = frozen_CD_ENDO[
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('FrozenACB')) &
                            (frozen_CD_ENDO['barcode_sample_id'].str.contains('ADDFrozenACB'))]
                    if frozen_CD_ENDO_ACB_ADD.shape[0] == 1  : 
                        if tmp_subject.iloc[0]['ac_non_involved___4'] is not '1':
                            to_print.append('Collected ADDFrozenACB, please click checkbox\n')

                # CTL_ENDO
            if len(my_fresh_df_collected) > 0:
                fresh_CTL_ENDO = my_fresh_df_collected[(my_fresh_df_collected['barcode_subject_type'].str.contains('CTL_ENDO')) ]

                if fresh_CTL_ENDO.shape[0] > 0: 
                    fresh_CTL_ENDO_TI = fresh_CTL_ENDO[(fresh_CTL_ENDO['barcode_sample_id'].str.contains('FreshTI'))]
                    if fresh_CTL_ENDO_TI.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ti___1'] is not '1':
                            to_print.append('Collected FreshTI, please click checkbox\n')

                    fresh_CTL_ENDO_AC = fresh_CTL_ENDO[(fresh_CTL_ENDO['barcode_sample_id'].str.contains('FreshAC'))]
                    if fresh_CTL_ENDO_AC.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ac___1'] is not '1':
                            to_print.append('Collected FreshAC, please click checkbox\n')

            if len(my_fixed_df_collected) > 0:                
                fixed_CTL_ENDO = my_fixed_df_collected[(my_fixed_df_collected['barcode_subject_type'].str.contains('CTL_ENDO')) ]
                if fixed_CTL_ENDO.shape[0] > 0: 
                    fixed_CTL_ENDO_TI = fixed_CTL_ENDO[(fixed_CTL_ENDO['barcode_sample_id'].str.contains('FixedTI'))]
                    if fixed_CTL_ENDO_TI.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ti___2'] is not '1':
                            to_print.append('Collected FreshTI, please click checkbox\n')

                    fixed_CTL_ENDO_AC = fixed_CTL_ENDO[(fixed_CTL_ENDO['barcode_sample_id'].str.contains('FixedAC'))]
                    if fixed_CTL_ENDO_AC.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ac___2'] is not '1':
                            to_print.append('Collected FreshAC, please click checkbox\n')

            if len(my_frozen_df_collected) > 0:
                frozen_CTL_ENDO = my_frozen_df_collected[(my_frozen_df_collected['barcode_subject_type'].str.contains('CTL_ENDO')) ]
                if frozen_CTL_ENDO.shape[0] > 0: 
                    frozen_CTL_ENDO_TI_ONLY = frozen_CTL_ENDO[
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenTI')) &
                            (~frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenTI'))]                
                    if frozen_CTL_ENDO_TI_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ti___3'] is not '1':
                            to_print.append('Collected FrozenTI, please click checkbox\n')

                    frozen_CTL_ENDO_TI_ADD = frozen_CTL_ENDO[
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenTI')) &
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenTI'))]                
                    if frozen_CTL_ENDO_TI_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ti___4'] is not '1':
                            to_print.append('Collected ADDFrozenTI, please click checkbox\n')

                    frozen_CTL_ENDO_AC_ONLY = frozen_CTL_ENDO[
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenAC')) &
                            (~frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenAC'))]
                    if frozen_CTL_ENDO_AC_ONLY.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ac___3'] is not '1':
                            to_print.append('Collected FrozenAC, please click checkbox\n')

                    frozen_CTL_ENDO_AC_ADD = frozen_CTL_ENDO[
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('FrozenAC')) &
                            (frozen_CTL_ENDO['barcode_sample_id'].str.contains('ADDFrozenAC'))] 
                    if frozen_CTL_ENDO_AC_ADD.shape[0] == 1  :   
                        if tmp_subject.iloc[0]['specimen_bio_ctl_ac___4'] is not '1':
                            to_print.append('Collected ADDFrozenAC, please click checkbox\n')
   
            if to_print == []:
                outfile.write("OK")
            else:
                for item in to_print:
                    outfile.write("%s\n" % item)


    
def subject_status_report(project):
    dataset = project.export_records(events=['action_tuple_table_arm_3'],fields=['record_id_dem_endo','barcode_sample_id','barcode_subject_type','barcode_action_type','barcode_action_date','barcode_processed_by','barcode_freezer','barcode_rack','barcode_box_id','barcode_box_position'])
    df = pd.DataFrame.from_dict(dataset)
#df_uniq = df.drop_duplicates(subset=['barcode_sample_id'], keep="last")
    df_uniq_full = df[['record_id_dem_endo','barcode_sample_id','barcode_subject_type','barcode_action_type','barcode_action_date','barcode_processed_by','barcode_freezer','barcode_rack','barcode_box_id','barcode_box_position']]

    df_uniq_full.sort_values('barcode_sample_id', inplace=False, ascending=True)

    df_sample_id = df_uniq_full[['barcode_sample_id']]
    df_subject_id = set(df_sample_id['barcode_sample_id'].str[3:6].to_list())
#df_subject_id = df_subject_id.drop_duplicates(subset=['subject_id'], keep="last")
    for val in df_subject_id:
        my_df  = df_uniq_full[df_uniq_full['barcode_sample_id'].str.contains(val)]
        my_df.to_csv (r'/var/www/html/shunxing/gca/summary/subject/%s.txt'% val, index = False, header=True)
        
def application(environ,start_response):
    status = '200 OK'
    project = redcap.Project('https://redcap.vanderbilt.edu/api/','PLEASE FILL IN THE REDCAP API_KEY')
    dataset = project.export_records(events=['action_tuple_table_arm_3'],fields=['barcode_sample_id','barcode_subject_type','barcode_action_type'])
    # 1. QA table
    #data_collection_QA(dataset, project)
    # 2. Overview of subjects stats.
    overview_subj_stats(dataset,project)
    # 3. Overview of specimens storage.
    overview_specimens_storage(dataset)
    # 4. Overview of biopsies storage.
    overview_biopsies_storage(dataset)
    # 6. Overview of freezer storage.
    overview_freezer_storage(project)
    # 7. Quality Control 
    quality_control(project)
    # 8. Record tracking of patients' specimens.
    subject_status_report(project)

    html = ['<html>',
            '<body>',
            '<h2><b>DASHBOARD</b></h2>',
            '<h3>- Combinatorial Single Cell Strategies for a Crohn\'s Disease Gut Cell Atlas_Specimen</h3>',
            '<div style="width: 100%; font-size: 16x; font-weight: bold; text-align: left;">',
            '<a href="http://masi.vuse.vanderbilt.edu/shunxing/gca/summary/data_collection_QA.html">1. Data collection quality control. </a><br />',
            '<a href="http://masi.vuse.vanderbilt.edu/shunxing/gca/summary/subject_stats.html">2. Overview of subjects stats. </a><br />',
            '<a href="http://masi.vuse.vanderbilt.edu/shunxing/gca/summary/specimens_stats.txt">3. Overview of specimen storage. </a><br />',
            '<a href="http://masi.vuse.vanderbilt.edu/shunxing/gca/summary/biopsies_stats.txt">4. Overview of biopsies storage.</a><br />',
            '5. What specimens have been shipped, where, who and date? <br />',
            '<a href="http://masi.vuse.vanderbilt.edu/shunxing/gca/summary/freezer_stats">6. Overview of freezer storage.</a><br />',
            '<a href="http://masi.vuse.vanderbilt.edu/shunxing/gca/summary/quality_control.txt">7. Redcap form consistency check.</a><br />',
            '<a href="http://masi.vuse.vanderbilt.edu/shunxing/gca/summary/subject">8. All specimens stats. </a><br />',
            '</div>',
            '</body>',
            '</html>']
    s = ''.join(html)
    response_header = [('Content-type','text/html')]
    start_response(status,response_header)
    return [s.encode()]
