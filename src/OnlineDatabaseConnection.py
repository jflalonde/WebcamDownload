import urllib2
import xml.dom.minidom
import os.path
import datetime
from Webcam import Webcam
from math import *

class OnlineDatabaseConnection:
    """Handles the connections with the webcams.travel website"""
     
    def __init__(self): 
        self.urlBasePath = 'http://api.webcams.travel'
        self.urlImgPath = 'http://images.webcams.travel/webcam'
        self.developerId = 'cc75055acd7cc4b9fdda3af54214465a'
        
        # list of continents to download
        self.continentList = ['AF', 'AN', 'AS', 'EU', 'NA', 'OC', 'SA']
    
    def getWebcamImageUrl(self, webcamId):
        return '%s/%d.jpg' % (self.urlImgPath, webcamId)
   
    def downloadImage(self, outputBasePath, webcamId):
        """Downloads the most recent image for the given webcam name"""
        webcamUrl = os.path.join(self.urlImgPath, webcamId + '.jpg')
        outputUrl = os.path.join(outputBasePath, webcamId)
        
        imgDownloader = ImageDownloader()
        imgDownloader.downloadImage(webcamUrl, outputPath)
        
    def updateDatabase(self, outputPath):
        """Updates the database with the new webcams found online"""
        
        # Download webcams from all continents
        for continentName in self.continentList:
            
            # Download first page to figure out how many webcams there are
            nbWebcams = self.downloadContinentPage(outputPath, continentName, 1)
            nbPagesTotal = int(ceil(float(nbWebcams)/50));
            
            print 'Found {0} pages for continent {1}'.format(nbPagesTotal, continentName)
            
            # Download remaining pages
            for pageId in range(1,nbPagesTotal):
                print 'Downloading page {0} of {1} for continent {2}'.format(pageId+1, nbPagesTotal, continentName)
                self.downloadContinentPage(outputPath, continentName, pageId)
            

    def downloadContinentPage(self, outputPath, continentName, pageId):
        """Downloads all the webcams from a single continent"""
        
        # Create the URL
        fullUrl = self.urlBasePath + '/rest?method=wct.webcams.list_by_continent&devid={devid}&continent={continent}&per_page=50&page={pageId}'.\
            format(devid=self.developerId,continent=continentName,pageId=pageId)
            
        # Get the XML file containing all webcams
        continentXmlStr = urllib2.urlopen(fullUrl).read()
        
        # Setup the XML parser
        xmlDocument = xml.dom.minidom.parseString(continentXmlStr)
        
        # Retrieve the number of webcams
        webcamsEl = xmlDocument.getElementsByTagName('webcams')
        nbWebcams = int(webcamsEl[0].getElementsByTagName('count')[0].firstChild.data)
                        
        # Create individual xml files
        for webcamEl in webcamsEl[0].getElementsByTagName('webcam'):
            # Build filename
            webcamId = webcamEl.getElementsByTagName('webcamid')[0].firstChild.data
            filename = os.path.join(outputPath, webcamId + '.xml')
            
            # Don't overwrite the existing file
            if os.path.exists(filename):
                continue
            
            # Create temporary XML document
            try:
                # Create a webcam object, then save it to XML
                curWebcam = Webcam()
                curWebcam.loadFromOnlineDbXMLString(webcamEl.toxml())
                curWebcam.origUrl = self.getWebcamImageUrl(curWebcam.webcamId)
                curWebcam.saveToXMLFile(filename)
                                            
            except:
                print 'Problem with webcam ' + webcamId
                raise
            
        return nbWebcams
        

