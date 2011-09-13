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


def findOnlineHosts(hostList):
    """ Determines which host is accessible through ssh """
    # Maintain kerberos ticket
    retCode = subprocess.call(['kinit', '--renew', '--forwardable'])

    # Start a process for each host
    processList = []
    for host in hostList:
        try:            
            cmd = 'ssh -o GSSAPIDelegateCredentials=yes jlalonde@%s \'exit\'' % host
            processList.append(subprocess.Popen(cmd, shell=True))
        except:
            # Just output and skip
            print 'Could not start process with host %s' % host
        
    # Wait for a bit to make sure they all complete
    time.sleep(25)
    
    # Look at the threads which are still active, kill them, remove them from the list
    onlineHostList = []
    for processId, process in enumerate(processList):        
        # make sure it's not running
        if process.poll() == None:
            # still running! kill it
            process.kill()
        elif process.poll() == 0:
            # keep the host
            onlineHostList.append(hostList[processId])
        else:
            # process encountered a problem, don't keep it either
            print 'Ssh could not connect to host %s' % host

    return onlineHostList

class HostConnection():
    """ Manages the connections to remote hosts"""
    
    def __init__(self, processName, useWarp=False, useThreads=False, logger=None):
        """ Constructor: initializes the running process list """
        self.processList = []
        self.hostList = []
        self.useWarp = useWarp
        self.warpBaseOutputPath = '/lustre/jlalonde/outputs/'
        self.warpOutputPath = os.path.join(self.warpBaseOutputPath, 'webcamDownload')
        self.warpBackupOutputPath = os.path.join(self.warpBaseOutputPath, 'backup')
        self.warpExecPath = '/tmp'
        
        self.useThreads = useThreads
        
        self.processName = processName
   
        if logger == None:
            self.logger = logging.getLogger('HostConnection')
            self.logger.addHandler(NullHandler())
        else:
            self.logger = logger
            
    def clearLogs(self, logPath):
        """ Clears the current logs to avoid pile-up """
        
        if self.useWarp:
            try:
                # Delete path
                shutil.rmtree(self.warpOutputPath)
            except:
                # Didn't work... notify and forget about it
                self.logger.error('Could not delete log path')
                
            # Create the directory
            os.mkdir(self.warpOutputPath)
        
        elif self.useThreads:
            logPath = os.path.dirname(logPath)
            logFiles = glob.glob(os.path.join(logPath, 'tmp_*.log'))
            for file in logFiles:
                os.remove(file)
            
            
        
    def backupLogs(self, logPath):
        """ Create a backup of the logs """
        curDate = datetime.datetime.now()
        dirName = 'backup-%04d%02d%02d_%02d%02d' % (curDate.year, curDate.month, curDate.day, curDate.hour, curDate.minute)

        if self.useWarp:
            shutil.copytree(self.warpOutputPath, os.path.join(self.warpBackupOutputPath, dirName))
            
        elif self.useThreads:
            logPath = os.path.dirname(logPath)
            logFiles = glob.glob(os.path.join(logPath, 'tmp_*.log'))
            
            outputDir = os.path.join(logPath, dirName)
            os.mkdir(outputDir)
            
            for file in logFiles:
                shutil.copy(file, outputDir)

    
    def runningProcesses(self):
        """ Returns the list of processes that are still running """
        stillRunning = []
        
        if self.useWarp:
            # Get processes on warp
            cmd = 'qstat | grep %s' % self.processName
            self.logger.debug('Checking for running processes using %s' % cmd)
            procId = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            
            # retrieve the first entry of each returned line
            outputBuf, errBuf = procId.communicate()
            
            lines = outputBuf.splitlines()
            
            for line in lines:
                processId = line[0:line.find('.warp')]
                if len(processId) > 0:
                    stillRunning.append(processId)
                    self.logger.debug('Found running process %s... ' % processId)
                    
        elif self.useThreads:
            # Get threads on localhost
            threadList = threading.enumerate()
            
            # Make sure they're our download threads
            for thread in threadList:
                if thread.name.find('ImageDownloader') == 0:
                    stillRunning.append(thread)
                        
        else:
            for processId, process in enumerate(self.processList):            
                if process.poll() == None:
                    stillRunning.append(self.hostList[processId])
                
        return stillRunning

    def startCmdOnHost(self, host, cmd):
        """ Launches a process on a remote host """
        sshCmd = 'ssh -o GSSAPIDelegateCredentials=yes jlalonde@%s \'%s\'' % (host, cmd) 
        newProcess = subprocess.Popen(sshCmd, shell=True)
        
        self.processList.append(newProcess)
        self.hostList.append(host)
        
    def startCmdOnWarp(self, cmd):
        """ Launches a process on warp """
          
        # create temporary script
        scriptPath = os.path.join(self.warpExecPath, 'warpExec.sh')
        scriptHandle = open(scriptPath, 'w')
        scriptHandle.write('#!/bin/sh\n\n')
        scriptHandle.write('# This script has been automatically-generated. DO NOT EDIT\n\n')
        scriptHandle.write(cmd)
        scriptHandle.close()
        
        # create qsub command
        warpCmd = 'qsub -N %s -l nodes=1:ppn=1 -e %s -o %s -j oe %s' % \
            (self.processName, self.warpOutputPath, self.warpOutputPath, scriptPath)
        
        self.logger.debug('Running command: %s' % warpCmd)
        
        # launch process
        subprocess.Popen(warpCmd, shell=True)
        
    def startThread(self, xmlFile, outputPath, logPath, threadNb, filterSunAltitude, filterExistingFile, filterJpg):
        # launch a thread!
        imageDownloaderThread = ImageDownloaderThread.ImageDownloaderThread('ImageDownloader-%d' % threadNb, xmlFile, outputPath, logPath, filterSunAltitude, filterExistingFile, filterJpg)
        imageDownloaderThread.start()
        
        
    def killAllProcesses(self):
        """ Kill all processes that are still running """
        if self.useWarp:
            # Stop all processes on warp
            curProc = self.runningProcesses()
            
            cmdStr = ''
            for id in curProc:
                cmdStr = cmdStr + '%d ' % int(id)
            
            cmd = 'qdel ' + cmdStr
            self.logger.debug('Killing processes: %s' % cmd)
            
            subprocess.Popen(cmd, shell=True)
            
            # Give time to write the logs, etc.
            time.sleep(2)
            
        elif self.useThreads:
            # You can't actually kill a thread in Python, let it run
            self.logger.debug('I''d like to kill threads but I can''t...')
            
        else:
            for processId, process in enumerate(self.processList):
                if process.poll() == None:
                    process.kill()
            
            # Re-initialize the lists
            self.processList = []
            self.hostList = []