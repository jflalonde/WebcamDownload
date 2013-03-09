'''
Created on Nov. 10th, 2009

@author: Jean-Francois Lalonde
'''

import ImageDownloader
import os.path
import sys
import logging

def usage():
    print 'Usage: \
        DownloadImagesThreads.py webcamsDbFile outputImagesPath nbThreads logPath'

if __name__ == '__main__':
    # read arguments
    if len(sys.argv) < 5:
        usage()
        sys.exit()
        
    # --- Options ---
    
    # whether to filter based on sun position (for daytime images) 
    filterSunAltitude = True
    minSunAltitude = -10 # in degrees
    
    # whether or not to check for duplicates
    filterExistingFile = True
    
    # email notifications
    emailNotification = True
    emailAddress = 'yourname@yourdomain.com'
    # how often do you want to know if it's still running (in seconds)
    emailRunningNotificationInterval = 24*3600; # 24 hours
    
    # whether to filter for bad/corrupted jpgs
    filterJpg = True
    filterJpgExec = '/path/to/jpeginfo'
    
    # Time interval (in seconds)
    timeInterval = 10*60   
    
    # Total time (in seconds)
    totalTime = float('inf'); #7 * 24 * 3600 # (1 week)

    # --- Done setting options ---
    
    webcamsDbFile = sys.argv[1]
    outputImagesPath = sys.argv[2]
    nbThreads = int(sys.argv[3])
    logPath = sys.argv[4]
            
    # load the log file (if needed)
    logger = logging.getLogger('DownloadImagesThreads')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    fh = logging.FileHandler(logPath, mode='w')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    # setup console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
        
    # Prepare temporary path
    outputTmpPath = os.path.join(os.path.dirname(webcamsDbFile), 'downloadDb')
    if not os.path.exists(outputTmpPath):
        os.makedirs(outputTmpPath)
                                        
    # Download one image for each webcam
    imgDownloader = ImageDownloader.ImageDownloader(filterSunAltitude=filterSunAltitude, minSunAltitude=minSunAltitude, \
                                                    filterExistingFile=filterExistingFile, \
                                                    filterJpg=filterJpg, filterJpgExec=filterJpgExec, \
                                                    emailNotification=emailNotification, emailAddress=emailAddress, \
                                                    emailRunningNotificationInterval=emailRunningNotificationInterval, \
                                                    logger=logging.getLogger('DownloadImagesThreads.ImageDownloader'), \
                                                    nbThreads=nbThreads)
    
    # Launch the download of images at regular intervals
    logger.info('Downloading images at regular intervals')
    imgDownloader.downloadImagesAtRegularIntervals(webcamsDbFile, outputImagesPath, [], \
                                                   outputTmpPath, logPath, timeInterval, totalTime)
    logger.info('Done downloading images at regular intervals!')

    
