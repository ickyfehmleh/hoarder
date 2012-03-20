import os.path
import time
import threading

class AbstractDAO(object):
	dbSession = None

	def __init__(self,dbSession):
		self.dbSession = dbSession
		self.local = threading.local()

	def getDatabaseSession(self):
		d = self.local.__dict__
		if not d.has_key('currentSession'):
			d['currentSession'] = self.dbSession()
		return d['currentSession']
