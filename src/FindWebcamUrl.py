'''
Created on August 3rd, 2009

@author: jflalonde
'''

import Webcam
import os
import os.path
import glob
import sys
import logging
import urllib2
import urlparse
import webbrowser
import re
import optparse
import random

# XXX video.cgi doesn't actually work with wget...

baseUrl = 'http://www.webcams.travel/webcam/'

searchTermRegex = [
	re.compile('web', re.IGNORECASE),
	re.compile('cam', re.IGNORECASE),
	re.compile('video', re.IGNORECASE),
]

class Action(object):
	ABORT = "a"
	SKIP = "s"
	MARK_CANNOT_FIND = "c"
	MARK_BAD = "b"
	MARK_DOWNLOAD = "d"
	USE_SUGGESTED = "u"
	regex = re.compile('^(?P<action>\w+?) *(?P<value>\d*?)$')

	ACTION_NAMES = [
		"Abort",
		"Skip",
		"mark Bad",
		"mark Cannot find",
		"mark Download",
		"Use suggested <index>",
	]

	ACTIONS = set([
		ABORT,
		SKIP,
		MARK_BAD,
		MARK_DOWNLOAD,
		USE_SUGGESTED,
		MARK_CANNOT_FIND
	])

# regex to find link to webcam site from main site
webcamLinkRegex = re.compile('Source: <a href="(?P<url>.*?)"')
webcamNewestRegex = re.compile('<a href="(?P<url>.*?)".*?Newest image</a>')
webcamImageRegex = re.compile('<img.*?src="(?P<url>.*?)"')

def usage():
	print 'Usage: \
		FindWebcamUrl.py webcamsDbPath outputDbPath'

def processWebcam(cam):

	print ''
	print 'Processing webcam', str(webcam.id)
	print cam.status

	if cam.status != Webcam.Status.READY:
		return False


	# Find the original URL
	origUrl = baseUrl + str(webcam.id)

	# Parse the html file for the image source
	try:
		webcamHtml = urllib2.urlopen(origUrl).read()
	except urllib2.URLError, e:
		print "Unable to find", origUrl
	else:
		match = webcamLinkRegex.search(webcamHtml)
		if match is None:
			print 'Error: No link found in', origUrl
			return False

		webcam.webUrl = match.group('url')

		match = webcamNewestRegex.search(webcamHtml)
		if match is not None and match.group('url') != webcam.webUrl:
			try:
				webbrowser.open(match.group('url'))
			except: pass

		# Show it to the user and ask for the url to the image
		try:
			webbrowser.open(webcam.webUrl)
		except: pass

		# find the potential links and print them
		potentialUrls = set()
		try:
			matches = [m.group('url') for m in webcamImageRegex.finditer(urllib2.urlopen(webcam.webUrl).read())]
			for url in matches:
				for s in searchTermRegex:
					m = s.search(url)
					if m is not None:
						potentialUrls.add(urlparse.urljoin(webcam.webUrl, url))
			potentialUrls = list(potentialUrls)
		except: pass

		if len(potentialUrls) != 0:
			print 'Suggested links for webcam at', webcam.webUrl + ':'
			for m in potentialUrls:
				print "\t" + m
			# if not too many links, open in webbrowser
			if len(potentialUrls) < 4:
				map(webbrowser.open, potentialUrls)
		else:
			print 'Could not find any suggested links for', webcam.webUrl

		# Also show the low-res webcam image for comparison
		webbrowser.open(origUrl)

	# Query next action
	while True:
		print "Action? {",
		for s in Action.ACTION_NAMES[0:-1]:
			print s, '|',
		print Action.ACTION_NAMES[-1], '}'
		actionMatch = Action.regex.match(raw_input('> '))

		if actionMatch is None:
			print "Invalid Syntax"
			continue

		action = actionMatch.group("action")
		value = actionMatch.group("value")

		if action not in Action.ACTIONS:
			print "Invalid Action"
			continue

		elif action == Action.ABORT:
			sys.exit(0)

		elif action == Action.SKIP:
			return False

		elif action == Action.MARK_BAD:
			webcam.status = Webcam.Status.BAD
			return True

		elif action == Action.MARK_CANNOT_FIND:
			webcam.status = Webcam.Status.CANNOT_FIND
			return True

		elif action == Action.MARK_DOWNLOAD:
			# Ask the user to look for the URL to the image
			url = raw_input("What is the URL to the image? >> ");
			# verify that this file can be accessed
			try:
				req = urllib2.urlopen(url)
			except urllib2.HTTPError, e:
				print "Invalid URL, code", e.code
				continue
			except urllib2.URLError, e:
				print "Invalid URL,", e.reason
				continue
			except:
				print "Invalid URL"
				continue
			else:
				webcam.imageUrl = url
				webcam.status = Webcam.Status.DOWNLOAD
				return True

		elif action == Action.USE_SUGGESTED:
			try:
				url = potentialUrls[int(value)]
				webcam.imageUrl = url
			except:
				print "Invalid image index"
				continue

			webcam.status = Webcam.Status.DOWNLOAD
			return True

		# repeat until valid action is performed

if __name__ == '__main__':

	"""
	# XXX test
	webcam = Webcam.Webcam()
	webcam.loadFromXMLFile(sys.argv[1])

	usage = "usage: %prog [options] input output-path"
	parser = optparse.OptionParser(usage=usage)
	(options, args) = parser.parse_args()

	"""

	# read arguments
	if len(sys.argv) < 2:
		usage()
		sys.exit()

	webcamsDbPath = sys.argv[1]
	if len(sys.argv) > 2:
		outputDbPath = sys.argv[2]
	else:
		outputDbPath = webcamsDbPath

	"""
	# Prepare the logger
	logger = logging.getLogger('FindWebcamUrl')
	logger.setLevel(logging.DEBUG)
	"""

	# Read input files
	fileList = glob.glob(os.path.join(webcamsDbPath, '*.xml'))
	random.shuffle(fileList)

	if len(sys.argv) >= 4:
		fileList = [sys.argv[3]]

	# Loop over all of them
	for file in fileList:
		webcam = Webcam.Webcam()
		webcam.loadFromXMLFile(file)

		outputFile = os.path.join(outputDbPath, os.path.basename(file))

		# process and save the XML file
		if (processWebcam(webcam)):
			webcam.saveToXMLFile(outputFile)

