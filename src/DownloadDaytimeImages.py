'''
Created on May 18, 2009

@author: jflalonde
'''

import ImageDownloader
import OnlineDatabaseConnection
import Webcam
import os
import os.path
import glob
import xml.dom.minidom
import sys
import logging
import socket

def usage():
    print 'Usage: \
        DownloadDaytimeImages.py webcamsDbFile outputImagesPath [outputLogPath] [hostListFile]'

if __name__ == '__main__':
    # read arguments
    if len(sys.argv) < 3:
        usage()
        sys.exit()

    webcamsDbFile = sys.argv[1]
    outputImagesPath = sys.argv[2]

    # load the hosts (if needed)
    if len(sys.argv) >= 5:
        hostListFile = sys.argv[4]
    else:
        hostListFile = ''
        
    # load the log file (if needed)
    logger = logging.getLogger('DownloadDaytimeImages')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if len(sys.argv) >= 4:
        logPath = sys.argv[3]
        if len(hostListFile):
            logFile = 'root.log'            
            fh = logging.FileHandler(os.path.join(logPath, logFile), mode='w')
            fh.setLevel(logging.INFO)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
    else:
        logPath = ''

    # if len(sys.argv) < 4 or len(hostListFile):
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
        
    # Prepare temporary path
    outputTmpPath = os.path.join(os.path.dirname(webcamsDbFile), 'downloadDb')
    if not os.path.exists(outputTmpPath):
        os.makedirs(outputTmpPath)
                
    # Time interval (in seconds)
    timeInterval = 10*60   
    
    # Total time (in seconds)
    totalTime = float('inf'); #7 * 24 * 3600 # (1 week)
                        
    # Download one image for each webcam
    imgDownloader = ImageDownloader.ImageDownloader(pythonExecutable='DownloadDaytimeImages.py', \
                                                    filterSunAltitude=True, filterExistingFile=True, \
                                                    filterJpg=True, logger=logging.getLogger('DownloadDaytimeImages.ImageDownloader'))
    
    if len(hostListFile) > 1:
        # Launch the download of images at regular intervals
        logger.info('Downloading images at regular intervals')
        imgDownloader.downloadImagesAtRegularIntervals(webcamsDbFile, outputImagesPath, hostListFile, \
                                                       outputTmpPath, logPath, timeInterval, totalTime)
        logger.info('Done downloading images at regular intervals!')
    else:
        # Simply download images from the list
        logger.info('Downloading images from the list')
        imgDownloader.downloadImages(webcamsDbFile, outputImagesPath, outputTmpPath, logPath)

    
