# BarcodeRedcapIntegration

This is a project integrate barcode tracking systems to a REDCap project. We implement our systems with utilizing the RECap tuple table to 
(1) track all specimen barcode status: Print / Re-print / Store / Destroy / Distribute or mail specimen to other lab.
(2) validate a data entry: detect a duplicate and inconsistent data entry.
(3) generate simple stats of the specimen collection status. 

# Label printer
We choose the DYMO LabelWriters 450. The drivers are available at [mac os, windows](https://www.dymo.com/en-US/compatibility-chart), [linux (not testing)](https://www.dymo.com/en-US/dymo-label-sdk-cups-linux-p?storeId=20051&catalogId=10551)

