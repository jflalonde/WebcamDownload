'''
Created on May 19, 2009

@author: jflalonde
'''

import os
import os.path
import glob
import subprocess
import time
import logging
import shutil
import datetime
import threading
import ImageDownloaderThread

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

class HostConnection():
    """ Manages the connections to remote hosts"""
    
    def __init__(self, processName, logger=None):
        """ Constructor: initializes the running process list """
        self.processName = processName
   
        if logger == None:
            self.logger = logging.getLogger('HostConnection')
            self.logger.addHandler(NullHandler())
        else:
            self.logger = logger
            
    def clearLogs(self, logPath):
        """ Clears the current logs to avoid pile-up """                
        logPath = os.path.dirname(logPath)
        logFiles = glob.glob(os.path.join(logPath, 'tmp_*.log'))
        for file in logFiles:
            os.remove(file)
            
        
    def backupLogs(self, logPath):
        """ Create a backup of the logs """
        curDate = datetime.datetime.now()
        dirName = 'backup-%04d%02d%02d_%02d%02d' % (curDate.year, curDate.month, curDate.day, curDate.hour, curDate.minute)

        logPath = os.path.dirname(logPath)
        logFiles = glob.glob(os.path.join(logPath, 'tmp_*.log'))
            
        outputDir = os.path.join(logPath, dirName)
        os.mkdir(outputDir)
            
        for file in logFiles:
            shutil.copy(file, outputDir)
    
    def runningProcesses(self):
        """ Returns the list of processes that are still running """
        stillRunning = []
        
        # Get threads on localhost
        threadList = threading.enumerate()
            
        # Make sure they're our download threads
        for thread in threadList:
            if thread.name.find('ImageDownloader') == 0:
                stillRunning.append(thread)
                                        
        return stillRunning
                
    def startThread(self, xmlFile, outputPath, logPath, threadNb, filterSunAltitude, filterExistingFile, filterJpg):
        """ Launches a single thread """
        imageDownloaderThread = ImageDownloaderThread.ImageDownloaderThread('ImageDownloader-%d' % threadNb, xmlFile, outputPath, logPath, filterSunAltitude, filterExistingFile, filterJpg)
        imageDownloaderThread.start()
        
    def killAllProcesses(self):
        """ Kill all processes that are still running """

        # You can't actually kill a thread in Python, let it run
        self.logger.debug('I''d like to kill threads but I can''t...')
