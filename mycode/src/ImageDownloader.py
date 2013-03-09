'''
Created on May 18, 2009

@author: jflalonde
'''

import solar
import filecmp
import os.path
import glob
import datetime
import urllib2
import random
import Webcam
import HostConnection
import smtplib
import email
import math
import time
import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

class ImageDownloader():
    """Class used to download images from a library
    
        Contains some useful functions that can be used by anyone
        
        Can be initialized in two different ways:
          - stand-alone, the localhost is used to download the images
          - using an XML configuration file specifying the hosts to use. 
            Downloading is split across these hosts to diminish local bandwidth usage.
    """
    
    def __init__(self, \
                 filterSunAltitude=False, minSunAltitude=0, \
                 filterExistingFile=False, \
                 filterJpg=False, filterJpgExec='', \
                 emailNotification=False, emailAddress='', \
                 emailRunningNotificationInterval=60, \
                 logger=None, nbThreads=1):
        """ Initializes the class with an optional set of hosts """
        
        self.filterSunAltitude = filterSunAltitude
        self.minSunAltitude = minSunAltitude
        
        self.filterExistingFile = filterExistingFile
        
        self.filterJpg = filterJpg
        self.filterJpgExec = filterJpgExec
        
        # Email notification if host is still downloading
        self.emailNotification = emailNotification
        self.email = emailAddress
        self.emailRunningNotificationInterval = emailRunningNotificationInterval;
        
        # logger
        if logger == None:
            self.logger = logging.getLogger('ImageDownloader')
            self.logger.addHandler(NullHandler())
        else:
            self.logger = logger
                
        # Number of threads
        self.nbThreads = nbThreads
        
        # Host connection object
        self.hostConnection = HostConnection.HostConnection('webcamDownload', logger=logger)
                    
        
    def sendEmail(self, emailMessage, emailSubject):
        if self.emailNotification:
            msg = email.message_from_string(emailMessage)
            msg['To'] = self.email
            msg['From'] = self.email
            msg['Subject'] = '[WebcamDownload]: ' + emailSubject
                            
            s = smtplib.SMTP()
            s.connect()
            s.sendmail(self.email, [self.email], msg.as_string())
            s.quit()
        
    def downloadImagesAtRegularIntervals(self, webcamDbFile, outputPath, hostListFile, outputTmpPath='.', logPath='.', \
                                         timeInterval=10*60, totalTime=float('inf')):
        """Downloads a list of images to disk at regular intervals for a given period of time"""
        
        cumulTime = 0
        maxFactor = 0.0
        while cumulTime < totalTime:
            # Measure starting time
            startTime = time.time()

            # Send notification to tell that we're still alive! (once every interval)
            curFactor = math.floor(float(cumulTime) / float(self.emailRunningNotificationInterval))
            self.logger.debug('cumulTime = %.2f, i = %.2f, curFactor = %.2f' % (float(cumulTime), \
                              curFactor, self.emailRunningNotificationInterval) )
            if (curFactor > maxFactor):
                self.sendEmail('Have a good webcam-downloading day! See ya tomorrow.\n', 'Webcams are downloading...');
                self.logger.info('Webcams are still downloading!')
                maxFactor = curFactor;
                
            # Is someone still trying to download?
            runningHosts = self.hostConnection.runningProcesses()
            if len(runningHosts):
                self.logger.error('%d hosts are still trying to download images... sending notification email' % len(runningHosts))
                # Send email to notify
                self.sendEmail('List of running hosts: \n %s' % runningHosts, \
                               'Hosts are still trying to download images')
            
                # Stop them all
                self.hostConnection.killAllProcesses()
                
                # Backup their logs
                self.hostConnection.backupLogs(logPath)

            # Clear previous logs
            self.hostConnection.clearLogs(logPath)
                        
            # Start download processes on localhost
            self.downloadImagesThreads(webcamDbFile, outputPath, outputTmpPath, logPath)
            
            # Measure end time
            elapsedTime = time.time() - startTime
            
            # Sleep
            if elapsedTime < timeInterval:
                self.logger.info('Sleeping for %d seconds' % (timeInterval-elapsedTime))
                time.sleep(timeInterval-elapsedTime)
            else:
                self.logger.warning('Time interval already elapsed by %d seconds! Sending notification email' % (elapsedTime-timeInterval))
                self.sendEmail('Time interval already elapsed by %d seconds!' % (elapsedTime-timeInterval), 'Time interval elapsed')
            
            cumulTime += timeInterval
            
        self.logger.info('Done downloading images at regular intervals')
                
    def downloadImagesThreads(self, webcamsDbFile, outputPath, outputTmpPath='.', logPath='.'):
        """Downloads a list of images to disk, using threads on the current host"""
        
        # Reads the XML file and build a webcam database
        self.logger.info('Downloading images using threads...')
        self.logger.info('Loading database...')
        webcamDb = Webcam.WebcamDatabase([])
        webcamDb.loadFromXMLFile(webcamsDbFile)
        self.logger.info('Done loading %d webcams.' % len(webcamDb))
        
        # Split the image list across hosts
        random.shuffle(webcamDb)
        nbWebcamsPerThread = int(math.ceil(float(len(webcamDb))/float(self.nbThreads)))
        
        self.logger.info('Each of the %d threads will download %d images' % (self.nbThreads, nbWebcamsPerThread))
        
        nbWebcamsDownloaded = 0
        for i in range(0, self.nbThreads):
            # Select which webcams to download
            subWebcamDb = webcamDb[nbWebcamsDownloaded:(nbWebcamsPerThread+nbWebcamsDownloaded)]
            nbWebcamsDownloaded = nbWebcamsDownloaded + len(subWebcamDb)
            
            # Create temporary XML file for that process need absolute path)
            tmpXMLFile = os.path.join(outputTmpPath, 'thread_%03d.xml' % i)
            subWebcamDb.saveToXMLFile(tmpXMLFile)
            
            tmpLogPath = os.path.join(os.path.dirname(logPath), 'thread_%03d.log' % i)
            
            # Start thread with input XML file
            self.hostConnection.startThread(tmpXMLFile, outputPath, tmpLogPath, i, \
                                            filterSunAltitude = self.filterSunAltitude, \
                                            filterExistingFile = self.filterExistingFile, \
                                            filterJpg = self.filterJpg)
            
            # Stop if we've processed all webcams
            if nbWebcamsDownloaded == len(webcamDb):
                break
      
        
    def downloadImages(self, webcamsDbFile, outputPath):
        """Downloads a list of images to disk"""
        
        # Reads the XML file and build a webcam database
        self.logger.info('Loading database...')
        webcamDb = Webcam.WebcamDatabase([])
        webcamDb.loadFromXMLFile(webcamsDbFile)
        self.logger.info('Done loading %d webcams.' % len(webcamDb))
        
        self.logger.info('Started downloading %d images...' % len(webcamDb))
        startTime = time.time()
        for webcam in webcamDb:
            # build url (depending on its status)
            if webcam.status == Webcam.Status.DOWNLOAD or webcam.status == Webcam.Status.ALREADY_DL:
                webcamUrl = webcam.imageUrl
            else:
                webcamUrl = webcam.origUrl
                
            self.downloadWebcamImage(webcam, webcamUrl, os.path.join(outputPath, webcam.name))
            
        self.logger.info('Done downloading all %d images in %d seconds' % (len(webcamDb), time.time()-startTime))
                
            
    def downloadWebcamImage(self, webcam, inputUrl, outputPath):
        """Downloads a webcam image from the input URL, makes sure it doesn't already exist and save it at the output path"""
      
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
      
        downloadImage = False
        if self.filterSunAltitude:
            # Make sure it's daytime (use latitude/longitude)
            curDate = datetime.datetime.utcnow()
            sunAltitude = solar.GetAltitude(webcam.latitude, webcam.longitude, curDate)
            
            downloadImage = sunAltitude > self.minSunAltitude
            
        else:
            # No need to check, go ahead and download
            downloadImage = True

        if downloadImage:
            try:
                # Build output filename
                outputFilename = self.createImageFilename(outputPath)
            
                # Download the image
                self.logger.info('Downloading image from %s' % inputUrl)
                self.downloadImage(inputUrl, outputFilename)
                
                if self.filterExistingFile:    
                    # Make sure the image is new
                    imgList = glob.glob(os.path.join(outputPath, '*.jpg'))
                    imgList.sort()
                    
                    # Compare with second-to-last 
                    if len(imgList) > 1 and filecmp.cmp(outputFilename, imgList[-2]):
                        self.logger.debug('Image already exists')
                        # It's the same, remove it
                        os.unlink(outputFilename)
                   
                # Make sure the file is a valid jpg file
                if self.filterJpg and os.path.exists(outputFilename):
                    # Use the external program jpeginfo
                    os.system('%s %s >> /dev/null' % (self.filterJpgExec, outputFilename))
                    self.logger.debug('Successfully saved image to %s' % outputFilename)
                    
            except urllib2.URLError as error:
                self.logger.error('Encountered an URL error: %s' % error)
                
            except RuntimeError as error:
                self.logger.error('Encountered a runtime error: %s' % error)
                
            except:
                self.logger.exception('Could not download image from URL %s' % inputUrl)
                
        else:
            self.logger.debug('URL %s is night-time' % inputUrl)
            
    def downloadImage(self, inputUrl, outputFilename):
        """Downloads an image from the web and saves it to the disk"""
        
        if inputUrl.find('faststream') > -1 or inputUrl.find('mjpg') > -1 or inputUrl.lower().find('motionjpeg') > -1:
            raise RuntimeError('Don\'t know what to do with mjpegs')
        
        # Download image (timeout of 45 seconds if it doesn't work)
        webcamImgData = urllib2.urlopen(inputUrl, timeout=45).read()

        # Save to disk
        fw = open(outputFilename, 'wb')
        fw.write(webcamImgData)
        fw.close()


    def createImageFilename(self, outputPath='.'):
        """Creates an image filename based on the current time and date in UTC coordinates"""
        
        curDate = datetime.datetime.utcnow()
        imageFilename = '%04d%02d%02d_%02d%02d%02d.jpg' % (curDate.year, curDate.month, curDate.day, curDate.hour, curDate.minute, curDate.second)
                
        return os.path.join(outputPath, imageFilename)    
        
