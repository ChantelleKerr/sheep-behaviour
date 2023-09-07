import os
from datetime import datetime

class TestData():
    def test_files(self, folder_path):
        
        # Assigns file paths.
        file_names = sorted(os.listdir(folder_path))
        cleanedFile = ""
        originalFiles = []
        for file in file_names:
            if file == "cleaned.csv":
                cleanedFile = folder_path + "/cleaned.csv"
            elif file.endswith(".txt"):
                originalFiles.append(folder_path + "/" + file)
            else:
                print("Error - unknown file found: " + file)
        
        # Initializes datetime format.
        datetime_format = '%Y-%m-%d %H:%M:%S'

        # Initializes cleaned file pointer and line string + error checking.
        if cleanedFile != "":
            CFP = open(cleanedFile, 'r')
            CFPLine = CFP.readline()
            CFPLine = CFP.readline() # Skips the header.
        else:
            print("Error - no cleaned file found")
            return None
        
        if len(originalFiles) == 0:
            print("Error - no data files found")
            return None

        # Iterate through both of the files and compare to make sure the cleaned file is as expected.
        for dataFile in originalFiles:

            OFP = open(dataFile, 'r')
            OFPLine = OFP.readline()
                
            index = 0
            while (CFPLine != '') and (OFPLine != ''):
                index += 1
                CFPLine = CFPLine.rstrip()
                OFPLine = OFPLine.rstrip()
                
                if CFPLine[:-1] != OFPLine:
                    
                    if OFPLine[:5] == "0,0,0" or OFPLine[0] == '*' or OFPLine == "-2048,-2048,-2048" or OFPLine == "ACCEL_X,ACCEL_Y,ACCEL_Z,LAT,LON,DAY,MONTH,YEAR,HOUR,MINUTE,SECOND":
                        OFPLine = OFP.readline()
                        continue
                    
                    isdate = True
                    try:
                        isdate = bool(datetime.strptime(CFPLine[-19:], datetime_format))
                    except ValueError:
                        isdate = False
                    
                    if not isdate:
                        print(f'Difference Detected ({dataFile}, Line {index}): {OFPLine} --> {CFPLine}')
                    
                CFPLine = CFP.readline()
                OFPLine = OFP.readline()
            OFP.close()
        CFP.close()

# For testing purposes.
if __name__ == "__main__":
    dataTest = TestData()
    folder_path = "test_data/sheep1"
    dataTest.test_files(folder_path)