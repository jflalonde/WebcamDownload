'''
Created on May 18, 2009

@author: jflalonde
'''

import xml.dom.minidom
import os
import tempfile
import os.path
import shutil

def saveXmlFile(xmlDocument, xmlFilename):
	# Save to file
	fw = open('tempfile', 'w')
	fw.write(xmlDocument.toxml('UTF-8'))
	fw.close()

	try:
		if os.path.exists(xmlFilename):
			os.unlink(xmlFilename)
		
		cmd = 'xmllint --format %s > %s' % (fw.name, xmlFilename)
		os.system(cmd)
	except:
		print 'Could not re-format the output XML'
		shutil.copyfile(fw.name, xmlFilename)

	os.unlink('tempfile')

class Status(object):
	EMPTY = 'EMPTY'
	NEW = 'NEW'
	READY = 'READY'
	DOWNLOAD = 'DOWNLOAD'
        ALREADY_DL = 'ALREADY-DL'
	BAD = 'BAD'
	NO_SKY = 'NO-SKY'
	CANNOT_FIND = 'CANNOT-FIND'

class Webcam(object):
	""" Represents a webcam sequence, storing relevant information """

	def __init__(self):
		self.status = Status.EMPTY
		
		# File
		self.filename = ''
		self.folder = '.'
		
		# Sequence
		self.id = 0
		
		# GPS coordinates
		self.latitude = 0
		self.longitude = 0
		
		# Location
		self.continent = ''
		self.country = ''
		self.city = ''
		self.title = ''
		
		# URL
		self.origUrl = ''
		self.webUrl = ''
		self.imageUrl = ''
		
	def loadFromXMLElement(self, xmlElement):
		""" Loads webcam information from an XML element """
		# Status
		self.status = xmlElement.getElementsByTagName('status')[0].getAttribute('value')
		
		# File
		self.filename = xmlElement.getElementsByTagName('file')[0].getAttribute('filename')
		self.folder = xmlElement.getElementsByTagName('file')[0].getAttribute('folder')
		
		# Sequence
		self.id = int(xmlElement.getElementsByTagName('sequence')[0].getAttribute('name'))
		
		# URL
		self.origUrl = xmlElement.getElementsByTagName('url')[0].getAttribute('orig')
		self.webUrl = xmlElement.getElementsByTagName('url')[0].getAttribute('web')
		self.imageUrl = xmlElement.getElementsByTagName('url')[0].getAttribute('image')
		
		# GPS coordinates
		self.latitude = float(xmlElement.getElementsByTagName('gpsCoordinates')[0].getAttribute('lat'))	  
		self.longitude = float(xmlElement.getElementsByTagName('gpsCoordinates')[0].getAttribute('long'))
		
		# Location
		self.continent = xmlElement.getElementsByTagName('location')[0].getAttribute('continent')
		self.country = xmlElement.getElementsByTagName('location')[0].getAttribute('country')
		self.city = xmlElement.getElementsByTagName('location')[0].getAttribute('city')
		self.title = xmlElement.getElementsByTagName('location')[0].getAttribute('title')

						
	def loadFromXMLFile(self, xmlFilename):
		""" Loads webcam information from XML file """
		xmlDocument = xml.dom.minidom.parse(xmlFilename)
		self.loadFromXMLElement(xmlDocument)
		xmlDocument.unlink()
		
	def loadFromOnlineDbXMLString(self, xmlString):
		""" Loads webcam information from XML string """
		xmlDocument = xml.dom.minidom.parseString(xmlString.encode("UTF-8"))
		
		# webcam id
		self.id = int(xmlDocument.getElementsByTagName('webcamid')[0].firstChild.data)
		
		# GPS coordinates
		self.latitude = float(xmlDocument.getElementsByTagName('latitude')[0].firstChild.data)
		self.longitude = float(xmlDocument.getElementsByTagName('longitude')[0].firstChild.data)
		
		# Location information
		self.continent = xmlDocument.getElementsByTagName('continent')[0].firstChild.data
		self.country = xmlDocument.getElementsByTagName('country')[0].firstChild.data
		self.city = xmlDocument.getElementsByTagName('city')[0].firstChild.data
		self.title = xmlDocument.getElementsByTagName('title')[0].firstChild.data
		
		# Create file/folder name
		self.filename = '%d.xml' % self.id
		self.folder = '.'
		
		# Set status
		self.status = 'NEW'
		
		# close the parser
		xmlDocument.unlink()
		
	def convertToXmlElement(self):
		""" Converts the webcam information to an XML element """
		doc = xml.dom.minidom.Document()
		webcamEl = doc.createElement(u'webcam')
		
		# Status
		statusEl = doc.createElement(u'status')
		statusEl.setAttribute(u'value', self.status)
		webcamEl.appendChild(statusEl)
		
		# File
		fileEl = doc.createElement(u'file')
		fileEl.setAttribute(u'filename', self.filename)
		fileEl.setAttribute(u'folder', self.folder)
		webcamEl.appendChild(fileEl)
		
		# Sequence
		seqEl = doc.createElement(u'sequence')
		seqEl.setAttribute(u'name', '%d' % self.id)
		seqEl.setAttribute(u'origName', '%d' % self.id)
		webcamEl.appendChild(seqEl)
		
		# URL
		urlEl = doc.createElement(u'url')
		urlEl.setAttribute(u'orig', self.origUrl)
		urlEl.setAttribute(u'web', self.webUrl)
		urlEl.setAttribute(u'image', self.imageUrl)
		webcamEl.appendChild(urlEl)
		
		# GPS coordinates element
		gpsEl = doc.createElement(u'gpsCoordinates')
		gpsEl.setAttribute(u'lat', '%.8f' % self.latitude)
		gpsEl.setAttribute(u'long', '%.8f' % self.longitude)
		webcamEl.appendChild(gpsEl)
		
		# Location element
		locationEl = doc.createElement(u'location')
		locationEl.setAttribute(u'continent', self.continent)
		locationEl.setAttribute(u'country', self.country)
		locationEl.setAttribute(u'city', self.city)
		locationEl.setAttribute(u'title', self.title)
		webcamEl.appendChild(locationEl)
		
		return webcamEl

		
	def saveToXMLFile(self, xmlFilename):
		""" Saves the webcam information to an XML file """
		doc = xml.dom.minidom.Document()
		webcamEl = self.convertToXmlElement()
		doc.appendChild(webcamEl)
		
		saveXmlFile(doc, xmlFilename)
			 
class WebcamDatabase:
	""" Represents an array of webcam sequences, which can itself be read/written to XML """
	
	def __init__(self, webcamList=[]):
		self.webcamList = webcamList
		
	def __getitem__(self, i):
#		return WebcamDatabase(self.webcamList[i])
		if isinstance(i, slice):
			return WebcamDatabase(self.webcamList[i])
		else:
			return self.webcamList[i]
		
	def __setitem__(self, i, v):
		self.webcamList[i] = v
#		if isinstance(i, slice):
#			self.webcamList = v
#		else:
#			self.webcamList[i] = v

	def __len__(self):
		return len(self.webcamList)
	
	def append(self, webcam):
		self.webcamList.append(webcam)
	
	def loadFromXMLFiles(self, xmlFilenames):
		for xmlFilename in xmlFilenames:
			xmlDocument = xml.dom.minidom.parse(xmlFilename)
			webcam = Webcam()
			webcam.loadFromXMLElement(xmlDocument.getElementsByTagName('webcam')[0])
			self.webcamList.append(webcam)
			xmlDocument.unlink()
				
	def loadFromXMLFile(self, xmlFilename):
		if len(self.webcamList) > 0:
			raise RuntimeError('Webcam database already loaded')
		
		xmlDocument = xml.dom.minidom.parse(xmlFilename)
		
		for webcamEl in xmlDocument.getElementsByTagName('webcam'):
			webcam = Webcam()
			webcam.loadFromXMLElement(webcamEl)
			self.webcamList.append(webcam)
			
		xmlDocument.unlink()
		
	def saveToXMLFile(self, xmlFilename):
		""" Saves the webcam database to an XML file """
		doc = xml.dom.minidom.Document()
		dbEl = doc.createElement('database')
		# append all webcam elements
		for webcam in self.webcamList:
			dbEl.appendChild(webcam.convertToXmlElement())
			
		doc.appendChild(dbEl)
		
		# Save to file
		saveXmlFile(doc, xmlFilename)
