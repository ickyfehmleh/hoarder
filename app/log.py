from cherrypy import _cperror
from logging import handlers
import cherrypy
import datetime
import logging
import os

def initLogging(path=os.getcwd() ):
	log = HoarderLogger()
	log.config( path )

# mostly ripped from CouchPotato
class HoarderLogger(object):
	className = None

	def __init__(self, className=None):
		self.className = className
		self.logger = cherrypy.log

	def info( self, m ):
		self.log( m, severity=logging.INFO )

	def debug( self, m ):
		self.log( m, severity=logging.DEBUG )

	def error( self, m ):
		self.log( m, severity=logging.ERROR )

	def log( self, message='', severity=logging.INFO ):
		self.logger.error( msg=message, context=self.className, severity=severity )

	def time(self):
		now = datetime.datetime.now()
		return ('%02d:%02d:%02d]' % (now.hour, now.minute, now.second))

	def access(self):
		pass

	def config( self, logPath, debug=False):
		level = logging.DEBUG if debug else logging.INFO

		# overwrite functions from cherrypy logger
		self.logger.time = self.time
		self.logger.access = self.access

		# set screen and level
		self.logger.screen = debug
		self.logger.error_log.setLevel( level )

		if not os.path.isdir( logPath ):
			os.mkdir( logPath )

		self.logger.error_file = ''

		# rotating file handler
		h = handlers.RotatingFileHandler( os.path.join( logPath, 'Hoarder.log' ),
			'a', 500000, 4 )
		h.setLevel( level )
		h.setFormatter( logging.Formatter( '%(asctime)s %(levelname)-5.5s %(message)s', '%H:%M:%S'))
		self.logger.error_log.addHandler( h )

	def logError( self, msg='', context='', severity=logging.INFO, traceback=False):
		if traceback:
			msg += _cperror.format_exc()

		self.logger.error_log.log( severity, '[%+25.25s] %s' % (context[-25:], msg))
