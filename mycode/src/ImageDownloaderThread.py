'''
Created on Nov 10th, 2009

@author: jflalonde
'''

import logging
import threading
import ImageDownloader

class ImageDownloaderThread(threading.Thread):
    
    def __init__(self, name, webcamsDbFile, outputPath, logPath, filterSunAltitude=True, filterExistingFile=True, filterJpg=True):
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        self.fh = logging.FileHandler(logPath, mode='w')
        self.fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.fh)
            
        # Initialize imageDownloader object
        self.imgDownloader = ImageDownloader.ImageDownloader(filterSunAltitude=filterSunAltitude, \
                                                             filterExistingFile=filterExistingFile, \
                                                             filterJpg=filterJpg, \
                                                             emailNotification=True, logger=self.logger)
        
        self.webcamsDbFile = webcamsDbFile
        self.outputPath = outputPath
        
        threading.Thread.__init__(self, name=name)

    
    def run(self):
        # Main thread function
        self.imgDownloader.downloadImages(self.webcamsDbFile, self.outputPath)
        
        # Close the file handler
        self.logger.removeHandler(self.fh)
        self.fh.close()
        

        
