'''
Created on May 18, 2009

@author: jflalonde
'''

import OnlineDatabaseConnection
import sys
import glob
import os
import Webcam

def usage():
    print 'Usage: \
        UpdateDatabase.py outputDbFilesPath outputDbFile'

if __name__ == '__main__':
    """ Updates the database from the webcams.travel website to the local disk """
    if len(sys.argv) != 3:
        usage()
        sys.exit()
    
    outputDbFilesPath = sys.argv[1]
    outputDbFile = sys.argv[2]
    
    # Update the database with the new files
    dbConnection = OnlineDatabaseConnection.OnlineDatabaseConnection()
    dbConnection.updateDatabase(outputDbFilesPath)
    
    # Save database into a single XML file
    fileList = glob.glob(os.path.join(outputDbFilesPath, '*.xml'))
    
    # Load webcam database
    webcamDb = Webcam.WebcamDatabase()
    webcamDb.loadFromXMLFiles(fileList)
    webcamDb.saveToXMLFile(outputDbFile)
    