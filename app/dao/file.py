from ..dbobjects.file import DBFile, DBMonitoredPath, DBFileExtension, DBPath, PathType
from basedao import AbstractDAO
from ..import log
import os.path
import time
from sqlalchemy.orm import joinedload

class FileDAO(AbstractDAO):
	_fileTypes = None
	_possibleTypes = ['I','M','T']
	logger = log.HoarderLogger(__name__)

	def filterProcessableFiles(self,dbfiles):
		rv = []
		extensions = self.getAllFileExtensions()
		for dbfile in dbfiles:
			if self.isProcessable( dbfile, extensions ):
				rv.append( dbfile )
		return rv

	def isProcessable(self,dbfile,extensions=None):
		if extensions is None:
			extensions = self.getAllFileExtensions()
		(fileName,fileExt) = os.path.splitext( dbfile.fileName )
		return fileExt in extensions

	def getAllFiles(self):
		rv = []
		session = self.getDatabaseSession()
		rv = session.query(DBFile).all()
		return rv

	def getFileCount(self):
		session = self.getDatabaseSession()
		rv = session.query(DBFile).count()
		return rv

	def saveFile(self,dbf):
		self.getDatabaseSession().commit()

	def refreshAllMonitoredPaths(self,disk=None):
		paths = None
		session = self.getDatabaseSession()
		if disk is not None:
			paths = disk.monitoredPaths
		else:
			paths = self.getAllMonitoredPaths()

		for path in paths:
			path.refreshing = True
		session.commit()

	def getAllRefreshablePaths(self):
		session = self.getDatabaseSession()
		return session.query(DBMonitoredPath).filter_by(refreshing=True).all()

	def getFileWithFileId(self,fileId):
		rv = None
		fileId=int(fileId)
		session = self.getDatabaseSession()
		#rv = session.query(DBFile).options(joinedload('fileMetadata')).filter_by(id=fileId).one()
		rv = session.query(DBFile).filter_by(id=fileId).one()
		return rv

	def getFileWithFileName(self,absFileName):
		rv = None
		session = self.getDatabaseSession()
		(path,fileName) = os.path.split( absFileName )
		p = self.getPathWithName(path)
		if p is not None:
			rv = p.findFileWithName( fileName )
		return rv

	def getPathWithName(self,absPathName):
		rv = None
		session = self.getDatabaseSession()
		try:
			rv = session.query(DBPath).filter_by(pathName=absPathName).one()
		except:
			pass
		return rv

	def getAllFileTypes(self):
		rv = None
		if self._fileTypes is None:
			rv = []
			for currType in self._possibleTypes:
				rv.append( PathType( currType ) )
			self._fileTypes = rv
		else:
			rv = self._fileTypes
		return rv

	def getFileTypeForPath(self,path):
		pass

	def _createFileFromFilesystem(self,fn,dbpath):
		fileName = os.path.basename( fn )
		dbf = DBFile(fileName,dbpath)
		dbf.fileSize = os.path.getsize( fn )
		dbf.dateAdded = time.time()
		self.appContext.fileMetadataDAO.createMetadataForFile( dbf )
		self.logger.info( '_createFileFromFilesystem(): got metadata' )
		return dbf

	def _createDirectoryFromFilesystem(self, dirname, monitoredPath ):
		dbp = DBPath()
		dbp.pathName = dirname
		dbp.dateAdded = time.time()
		monitoredPath.paths.append( dbp )
		return dbp

	def _createFilesFromDirectory( self, dbpath, monitoredPath ):
		session = self.getDatabaseSession()
		contents = os.listdir( dbpath.absolutePath )
		for c in contents:
			fp = os.path.join( dbpath.absolutePath, c )
			if os.path.isdir( fp ):
				if not monitoredPath.containsPath( fp ):
					self._createDirectoryFromFilesystem( fp, monitoredPath )
			else:
				if not dbpath.containsFileName( c ):
					#if self._findFileInPath( dbpath, c ) is None:
					self._createFileFromFilesystem( fp, dbpath )

	## step1: add new path for the monitoredPath
	##        yes this means there will be a path for every monitoredPath
	##	  otherwise DBFile would need a pointer to DBMonitoredPath AND DBPath
	##	  when there's a file in the root with no subdir
	## step2: os.walk( path )
	## step3: add dirs discovered in os.walk( path )
	## step4: for each dir, self._createFilesFromDirectory( path )
	def _createFilesFromMonitoredDirectory(self,monitoredPath):
		session = self.getDatabaseSession()
		exts = self.getAllFileExtensions()
		path = monitoredPath.pathName

		addDir = True
		# step1: add new path for the monitoredPath
		if not monitoredPath.containsPath( monitoredPath.pathName ):
			self._createDirectoryFromFilesystem( path, monitoredPath )

		# step2: find files and dirs
		for root, dirs, files in os.walk( path ):
			for dir in dirs:
				currDir = os.path.join( root, dir )
				# step3: add dirs
				dbp = monitoredPath.findPath( currDir )
				#dbp = self._findPathInMonitoredPath( currDir, monitoredPath )
				if dbp is None:
					dbp = self._createDirectoryFromFilesystem( currDir, monitoredPath )
				self._createFilesFromDirectory( dbp, monitoredPath )

	def populateFilesForPath( self, p ):
		session = self.getDatabaseSession()
		self._createFilesFromMonitoredDirectory( p )
		p.refreshing=False  # no longer refreshing
		session.commit()

	def createMonitoredPath(self,path,type,disk):
		if os.path.exists( path ):
			#relpath = path.replace(disk.path,'')[1:]
			#p = DBMonitoredPath(relpath,type)
			p = DBMonitoredPath(path,type)
			session = self.getDatabaseSession()
			disk.monitoredPaths.append( p )
			session.commit()
			return p
		else:
			raise ValueError( 'Path %s does not exist' % path )

	def getMonitoredPath(self,path):
		session = self.getDatabaseSession()
		#rv = session.query(DBMonitoredPath).options(joinedload('files')).filter_by(pathName=path).one()
		rv = session.query(DBMonitoredPath).filter_by(pathName=path).one()
		return rv

	def getAllMonitoredPaths(self,type=None):
		rv = None
		session = self.getDatabaseSession()
		if type is None:
			rv = session.query(DBMonitoredPath).all()
		else:
			rv = session.query(DBMonitoredPath).filter_by(fileTypeCode=type).all()
		return rv

	def getAllFileExtensions(self):
		allExts = self._getAllExtensions()
		exts = [] 
		for ext in allExts:
			exts.append( ext.extension )
		return exts

	def _getAllExtensions(self):
		session = self.getDatabaseSession()
		rv = session.query(DBFileExtension).all()
		return rv

	def addNewExtension(self,ext):
		## FIXME make sure extension does not already exist
		o = DBFileExtension(ext)
		session = self.getDatabaseSession()
		session.add( o )
		session.commit()
		return o

	def getLastFilesAdded(self,num=20):
		session = self.getDatabaseSession()
		exts = self.getAllFileExtensions()
		rv = session.query(DBFile).order_by(DBFile.dateAdded.desc()).limit(num).all()
		#fileExtFilter = 
		#rv = session.query(DBFile).order_by(DBFile.dateAdded.desc()).filter(DBFile.fileExtension in exts).limit(num).all()
		return rv

