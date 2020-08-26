class LocationHelper:
#     def __init__(self):
#         self._subjec
    
    def fillBoxLocationInfo(self,tupleTable,total_rows):
        curBarcodeId = ''
        curSubject = ''
        curType = ''
        curBoxId = ''
        curBoxPos = ''
        newTuple = []
        #tuple should be 100 elements
        for i in range(0,total_rows):
            tmpBarcodeId = tupleTable[i][0]
            tmpSubject = tmpBarcodeId[3:6]
            tmpBoxId = tupleTable[i][3]
            tmpBoxPos = tupleTable[i][4]
            
            # current barcode is Frozen
            if 'Frozen' in tmpBarcodeId:
                # First met Frozen
                if curType != 'Frozen':
                    curType = 'Frozen'
                    curBarcodeId = tmpBarcodeId
                    curSubject = tmpSubject
                    curBoxId = tmpBoxId
                    curBoxPos = tmpBoxPos
                    
                    newTuple.append([curBarcodeId,'C','C',curBoxId,curBoxPos])
                # curType is Frozen, but need to double check if subject got changed
                else:
                    # subject different, should start over box id and box position
                    if tmpSubject != curSubject :
                        #curType = 'Frozen'
                        curBarcodeId = tmpBarcodeId
                        curSubject = tmpSubject
                        curBoxId = tmpBoxId
                        curBoxPos = tmpBoxPos
                    
                        if curBoxId is "" or curBoxPos is "":
                            return None # location info should not be empty if you want me to auto input....
#                            newTuple.append([curBarcodeId,"",""])
                        else:
                            newTuple.append([curBarcodeId,'C','C',curBoxId,curBoxPos]) # Frozen always Freezer = C, Rack C
                    else:
                        # need to update boxid and box position 
                        curBarcodeId = tmpBarcodeId
                        if curBoxId is "" or curBoxPos is "":
                            return None # location info should not be empty if you want me to auto input....
#                            newTuple.append([curBarcodeId,"",""])
                        else:
                            newCurBoxId,newCurBoxPos = self.getBoxIdAndPos(curBoxId,curBoxPos)
                            if newCurBoxId is None and newCurBoxPos is None:
                                return None # something wroing with box position
                            curBoxId = newCurBoxId
                            curBoxPos = newCurBoxPos
                            newTuple.append([curBarcodeId,'C','C',newCurBoxId,newCurBoxPos])
                        
            elif 'SR' in tmpBarcodeId:
                # First met Frozen
                if curType != 'SR':
                    curType = 'SR'
                    curBarcodeId = tmpBarcodeId
                    curSubject = tmpSubject
                    curBoxId = tmpBoxId
                    curBoxPos = tmpBoxPos
                    
                    
                    if curBoxId is "" or curBoxPos is "":
                        return None # location info should not be empty if you want me to auto input....
#                            newTuple.append([curBarcodeId,"",""])
                    else:
                        newTuple.append([curBarcodeId,'C','A',curBoxId,curBoxPos])# Serum always Freezer = C, Rack A
                # curType is Frozen, but need to double check if subject got changed
                else:
                    # subject different, should start over box id and box position
                    if tmpSubject != curSubject :
                        #curType = 'Frozen'
                        curBarcodeId = tmpBarcodeId
                        curSubject = tmpSubject
                        curBoxId = tmpBoxId
                        curBoxPos = tmpBoxPos
                    
                        if curBoxId is "" or curBoxPos is "":
                            return None # location info should not be empty if you want me to auto input....
#                            newTuple.append([curBarcodeId,"",""])
                        else:
                            newTuple.append([curBarcodeId,'C','A',curBoxId,curBoxPos])# Serum always Freezer = C, Rack A
                    else:
                        # need to update boxid and box position 
                        curBarcodeId = tmpBarcodeId
                        if curBoxId is "" or curBoxPos is "":
                            return None # location info should not be empty if you want me to auto input....
#                            newTuple.append([curBarcodeId,"",""])
                        else:
                            newCurBoxId,newCurBoxPos = self.getBoxIdAndPos(curBoxId,curBoxPos)
                            if newCurBoxId is None and newCurBoxPos is None:
                                return None # something wroing with box position
                            curBoxId = newCurBoxId
                            curBoxPos = newCurBoxPos
                            newTuple.append([curBarcodeId,'C','A',newCurBoxId,newCurBoxPos])# Serum always Freezer = C, Rack A
                        
            elif 'ST' in tmpBarcodeId:
                # First met Frozen
                if curType != 'ST':
                    curType = 'ST'
                    curBarcodeId = tmpBarcodeId
                    curSubject = tmpSubject
                    curBoxId = tmpBoxId
                    curBoxPos = tmpBoxPos
                    
                    if curBoxId is "" or curBoxPos is "":
                        return None # location info should not be empty if you want me to auto input....
#                            newTuple.append([curBarcodeId,"",""])
                    else:
                        newTuple.append([curBarcodeId,'C','B',curBoxId,curBoxPos])# Stool always Freezer = C, Rack B
                # curType is Frozen, but need to double check if subject got changed
                else:
                    # subject different, should start over box id and box position
                    if tmpSubject != curSubject :
                        #curType = 'Frozen'
                        curBarcodeId = tmpBarcodeId
                        curSubject = tmpSubject
                        curBoxId = tmpBoxId
                        curBoxPos = tmpBoxPos
                    
                        if curBoxId is "" or curBoxPos is "":
                            return None # location info should not be empty if you want me to auto input....
#                            newTuple.append([curBarcodeId,"",""])
                        else:
                            newTuple.append([curBarcodeId,'C','B',curBoxId,curBoxPos])# Stool always Freezer = C, Rack B
                    else:
                        # need to update boxid and box position 
                        curBarcodeId = tmpBarcodeId
                        if curBoxId is "" or curBoxPos is "":
                            return None # location info should not be empty if you want me to auto input....
#                            newTuple.append([curBarcodeId,"",""])
                        else:
                            newCurBoxId,newCurBoxPos = self.getBoxIdAndPosStool(curBoxId,curBoxPos)
                            if newCurBoxId is None and newCurBoxPos is None:
                                return None
                            curBoxId = newCurBoxId
                            curBoxPos = newCurBoxPos
                            newTuple.append([curBarcodeId,'C','B',newCurBoxId,newCurBoxPos])# Stool always Freezer = C, Rack B
            else: 
                # no need to set location
                curBarcodeId = tmpBarcodeId
                newTuple.append([curBarcodeId,'','','','']) # forcely set irrelevant barcode id location information as None.
                
        return newTuple
    
    # add more constraint
    def getBoxIdAndPos(self,tmpCurBoxId, tmpCurBoxPos):
        if int(tmpCurBoxPos) < 81:
            newBoxPos = int(tmpCurBoxPos) + 1
            return tmpCurBoxId,str(newBoxPos)
        elif int(tmpCurBoxPos) == 81:
            newBoxId = int(tmpCurBoxId) + 1
            newBoxPos = 1
            return str(newBoxId),str(newBoxPos)
        else: 
            #something wrong with box position value
            return None, None
        
        # add more constraint
    def getBoxIdAndPosStool(self,tmpCurBoxId, tmpCurBoxPos):
        if int(tmpCurBoxPos) < 36:
            newBoxPos = int(tmpCurBoxPos) + 1
            return tmpCurBoxId,str(newBoxPos)
        elif int(tmpCurBoxPos) == 36:
            newBoxId = int(tmpCurBoxId) + 1
            newBoxPos = 1
            return str(newBoxId),str(newBoxPos)
        else: 
            #something wrong with box position value
            return None, None
        
        
    def barcodeListCustomSort(self,tmpBarcodeList):
        # ADDFrozen always goes After regular TI And AC
        # TI comes before AC
        # logic:
        # - TI -> FrozenOrder1
        # - AC -> FrozenOrder2
        # - ADDFrozenTI -> FrozenOrder3
        # - ADDFrozenAC -> FrozenOrder4
        
        # need to check ADD case, since Frozen contains in ADDFrozen... 
        for i in range(0,len(tmpBarcodeList)):
            tmpFrozenId = tmpBarcodeList[i]
            
            if 'ADDFrozenAC' in tmpFrozenId:
                
                tmpReplace = tmpFrozenId.replace("ADDFrozenAC", "FrozenOrder4")
                tmpBarcodeList[i] = tmpReplace

            elif 'ADDFrozenTI' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("ADDFrozenTI", "FrozenOrder3")
                tmpBarcodeList[i] = tmpReplace
                
            elif 'AC' in tmpFrozenId: # hacking for Fresh and Fixed
                tmpReplace = tmpFrozenId.replace("AC", "Order2")
                tmpBarcodeList[i] = tmpReplace
                
            elif 'TI' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("TI", "Order1")
                tmpBarcodeList[i] = tmpReplace
             
            # for lazy, still use tmpFrozenId as variable..
            elif 'SR10' in tmpFrozenId:
                tmpReplace = tmpFrozenId.replace("10", "9910")
                tmpBarcodeList[i] = tmpReplace
            elif 'SR11' in tmpFrozenId:
                tmpReplace = tmpFrozenId.replace("11", "9911")
                tmpBarcodeList[i] = tmpReplace
                                 
        tmpBarcodeList.sort() # regular String list sort
       
        # Remove hacking substring and use original Barcode Id. 
        for i in range(0,len(tmpBarcodeList)):
            tmpFrozenId = tmpBarcodeList[i]
            if 'FrozenOrder4' in tmpFrozenId:
                tmpReplace = tmpFrozenId.replace("FrozenOrder4", "ADDFrozenAC")
                tmpBarcodeList[i] = tmpReplace
            elif 'FrozenOrder3' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("FrozenOrder3", "ADDFrozenTI")
                tmpBarcodeList[i] = tmpReplace
            elif 'Order2' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("Order2", "AC")
                tmpBarcodeList[i] = tmpReplace
            elif 'Order1' in tmpFrozenId: 
                tmpReplace = tmpFrozenId.replace("Order1", "TI")
                tmpBarcodeList[i] = tmpReplace
            elif '9910' in tmpFrozenId:
                tmpReplace = tmpFrozenId.replace("9910", "10")
                tmpBarcodeList[i] = tmpReplace
            elif '9911' in tmpFrozenId:
                tmpReplace = tmpFrozenId.replace("9911", "11")
                tmpBarcodeList[i] = tmpReplace
                      
        return tmpBarcodeList