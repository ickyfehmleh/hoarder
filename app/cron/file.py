# 
# cronned processes
#
import logging

class DirectoryScanner(object):
	# handles populating files for newly inserted directories
	appContext = None
	logger = None

	def __init__(self,appContext):
		self.appContext = appContext
		self.logger = logging.getLogger()
		self.logger.info('DirectoryScanner init!' )

	def process(self):
		self.logger.info( '@@@ Starting processing!' )
		paths = self.appContext.fileDAO.getAllRefreshablePaths()
			
		for p in paths:
			self.logger.info( 'Operating on %s' % p.pathName )
			self.appContext.fileDAO.populateFilesForPath( p )

########################################################################
# update disk free space for mounted disks
class DiskScanner(object):
	appContext = None
	logger = None

	def __init__(self,appContext):
		self.appContext=appContext

	def process(self):
		self.appContext.diskDAO.refreshAvailableDisks()

########################################################################

class FileScanner(object):
	appContext = None
	fileQueue = None
	logger = None

	def __init__(self,appContext,fileQueue):
		self.appContext = appContext
		self.fileQueue = fileQueue
		self.logger = logging.getLogger()
		self.logger.info('FileScanner MEH init!' )

	def process(self):
		self.logger.info( '@@@ Starting processing!' )
