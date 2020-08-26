# BarcodeRedcapIntegration

This is a project integrate barcode tracking systems to a REDCap project. We implement our systems with utilizing the RECap tuple table to 
(1) track all specimen barcode status: Print / Re-print / Store / Destroy / Distribute or mail specimen to other lab.
(2) validate a data entry: detect a duplicate and inconsistent data entry.
(3) generate simple stats of the specimen collection status. 

# Label printer
We choose the DYMO LabelWriters 450. The drivers are available at [mac os, windows](https://www.dymo.com/en-US/compatibility-chart), [linux (not testing)](https://www.dymo.com/en-US/dymo-label-sdk-cups-linux-p?storeId=20051&catalogId=10551).

# Installation
Python version: tested on python 3.6 and 3.7.
```bash
pip install -r requirements.txt 
```

# Usage
All REDCAP API_KEY related code are removed. The REDCap project design is customized. The programs are for templates usage. Please design your own REDCap project.

PrinterApp
```bash
cd PrinterApp
python PrinterApp.py
```
LocationApp
```bash
cd LocationApp
python LocationApp.py
```
Dashboard: a python script which is currently running on a secure online web page built on an Apache HTTP server.

# Key engineering design criteria
## 1. Digitize the physical sample identification with human-readable sample recognition. 
According the type of labelprinter and the size of label, we choose to use EAN8 code as the barcode, with human readable barcode ID attaches to the label (due to the small size of the label). We also provide a webcam barcode identification feature, so we cannot use more complex format digital identification (e.g., PDF417, QR code). If users have a high quality printer, or the label is big enough, users can surly choose more complex barcode format.

## 2. Tracking specimen status in longitudinal manner – using REDCap tuple table. 
All barcode action event should be recorded in the REDCap. e.g., print, scanned, re-print, distributed to other lab, barcode destroyed etc. Administrators can do simple longitudinal query on the tuple table.

## 3. Customized specifications:
PrinterApp: Print full pack; Print extra frozen specimen only; Print full pack with extra frozen specimen; Print full pack without fresh specimen; Re-print missing barcode; Re-print destroyed barcode. 

LocationApp: Users prefer an Excel like data entry. The input table should be sorted based on barcode ID. The form can be automatically filled. The App should notified if a barcode has been destroyed/stored/distributed for avoiding to duplicate/error data entries. 

## 4.Detect data inconsistency.
Validate if the barcode is valid.

Detect un-recorded manual entries.

Patient ID should match patient category (study type)
