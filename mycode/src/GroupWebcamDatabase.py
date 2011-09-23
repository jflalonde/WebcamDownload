'''
Created on May 18, 2009

@author: jflalonde
'''

import Webcam
import os
import os.path
import glob
import xml.dom.minidom
import sys

def usage():
    print 'Usage: \
        GroupWebcamDatabase.py inputWebcamsPath outputWebcamsDbFile'

if __name__ == '__main__':
    # read arguments
    if len(sys.argv) < 3:
        usage()
        sys.exit()

    inputWebcamsPath = sys.argv[1]
    outputWebcamsDbFile = sys.argv[2]
                
    # read all files from input path into webcam database
    fileList = glob.glob(os.path.join(inputWebcamsPath, '*.xml'))
    webcamsDb = Webcam.WebcamDatabase()
    
    for file in fileList:
        webcam = Webcam.Webcam()
        webcam.loadFromXMLFile(file)
        
        # only add it if it must be downloaded
        if webcam.status == Webcam.Status.DOWNLOAD or webcam.status == Webcam.Status.ALREADY_DL:
            webcamsDb.append(webcam)
        
    # save webcam database to output XML file
    webcamsDb.saveToXMLFile(outputWebcamsDbFile)
    
