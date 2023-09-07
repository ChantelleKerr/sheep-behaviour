
from datetime import datetime

# Assign file paths, can be improved later.
cleanedFile = "test_data/sheep1/cleaned.csv"
originalFile = "test_data/sheep1/file000.txt"

# Initializes file pointers and assigns string values to initial lines.
CFP = open(cleanedFile, 'r')
OFP = open(originalFile, 'r')
CFPLine = CFP.readline()
OFPLine = OFP.readline()

# Initializes datetime format.
datetime_format = '%Y-%m-%d %H:%M:%S'

# Skips the first few lines in both files.
CFPLine = CFP.readline()
for startLines in range(3):
    OFPLine = OFP.readline()

# Iterate through both of the files and compare to make sure the cleaned file is as expected.
index = 0
while (CFPLine != '') and (OFPLine != ''):
    index += 1
    CFPLine = CFPLine.rstrip()
    OFPLine = OFPLine.rstrip()
    
    if OFPLine[:5] == "0,0,0" or OFPLine[0] == '*':
        OFPLine = OFP.readline()
        continue
    
    if CFPLine[:-1] != OFPLine:
        isdate = True
        try:
            isdate = bool(datetime.strptime(CFPLine[-19:], datetime_format))
        except ValueError:
            isdate = False
        
        if not isdate:
            print(f'Difference Detected ({index}): {OFPLine}, {CFPLine}')
        
    CFPLine = CFP.readline()
    OFPLine = OFP.readline()
    

print(index)
CFP.close()
OFP.close()