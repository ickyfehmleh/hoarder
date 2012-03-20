# 
# cronned processes
#
import time
import multiprocessing
from threading import Thread, Event
import logging
from file import DirectoryScanner, DiskScanner

def initCron(appContext):
	appContext.threads = []

	directoryScanner = DirectoryScanner(appContext )
	appContext.threads.append( RepeatingTimer( delay=30.0, target=directoryScanner.process ) )

	diskScanner = DiskScanner(appContext)
	appContext.threads.append( RepeatingTimer( delay=30.0, target=diskScanner.process ) )

def startCron(appContext):
	for thr in appContext.threads:
		thr.start()

class RepeatingTimer(Thread):
	def __init__(self, delay=15, maxIterations=0, target=None):
		Thread.__init__(self)
		self.daemon = True
		self.delay = delay
		self.target = target
		self.maxIterations = maxIterations
		self.finished = Event()

	def run(self):
		currentIteration = 0
		while not self.finished.isSet() and (self.maxIterations <= 0 or currentIteration < self.maxIterations):
			self.finished.wait( self.delay)
			if not self.finished.isSet():
				self.target()
				currentIteration += 1

	def cancel(self):
		self.finished.set()
