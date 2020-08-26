class CheatSheetEAN_Converter:
    """
    class for static list. 
    This class is very important, it is the key (hacking) way to convert ean8 code to real barcode id. 
    
    Modified on Mar 17, 2020,
    Add more different Frozen ID for CTL_ENDO, CD_Surgery, CTL_Surgery
    """
    CD_ENDO_CHEAT_LIST=[
    'FreshTIA',
    'FixedTIA',
    'FrozenTIA',
    'FreshTIB',
    'FixedTIB',
    'FrozenTIB',
    'FreshACA',
    'FixedACA',
    'FrozenACA',
    'FreshACB',
    'FixedACB',
    'FrozenACB',
    'DNA',
    'ST1', 
    'ST2', 
    'ST3',
    'ST4',
    'SR1',
    'SR2',
    'SR3', 
    'SR4',
    'SR5',
    'SR6',
    'SR7',
    'SR8',
    'SR9',
    'SR10',
    'SR11',
    'ADDFrozenTIA',
    'ADDFrozenTIB',
    'ADDFrozenACA',
    'ADDFrozenACB']
    
    CTL_ENDO_CHEAT_LIST=[
    'FreshTI',
    'FixedTI',
    'FrozenTI',
    'FreshAC',
    'FixedAC',
    'FrozenAC',
    'DNA',
    'ST1',
    'ST2',
    'ST3',
    'ST4',
    'SR1',
    'SR2',
    'SR3',
    'SR4',
    'SR5',
    'SR6',
    'SR7', 
    'SR8',    
    'SR9',
    'SR10',
    'SR11',
    'ADDFrozenTI',
    'ADDFrozenAC']

    CD_Surgery_CHEAT_LIST=[
    'FreshTI',
    'FixedTI',
    'FrozenTI',
    'FreshAC',
    'FixedAC',
    'FrozenAC',
    'ADDFrozenTI',
    'ADDFrozenAC']

    CTL_Surgery_CHEAT_LIST=[
    'FreshTI1',
    'FixedTI1',
    'FrozenTI1',
    'FreshTI2',
    'FixedTI2',
    'FrozenTI2',
    'FreshTI3',
    'FixedTI3',
    'FrozenTI3',
    'FreshAC4',
    'FixedAC4',
    'FrozenAC4',
    'FreshAC5',
    'FixedAC5',
    'FrozenAC5',
    'FreshAC6',
    'FixedAC6',
    'FrozenAC6',
    'FreshAC7',
    'FixedAC7',
    'FrozenAC7',
    'FreshAC8',
    'FixedAC8',
    'FrozenAC8',
    'ADDFrozenTI1',
    'ADDFrozenTI2',
    'ADDFrozenTI3',
    'ADDFrozenAC4',
    'ADDFrozenAC5',
    'ADDFrozenAC6',
    'ADDFrozenAC7',
    'ADDFrozenAC8']
    