##
# database objects
#
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import backref, relationship
import os.path
import uuid
import time

from . import Base

class PathType(object):
	FILE_TYPE_IGNORE='I'
	FILE_TYPE_MOVIE='M'
	FILE_TYPE_TV='T'
	FILE_TYPES = [FILE_TYPE_IGNORE, FILE_TYPE_MOVIE, FILE_TYPE_TV]

	def __init__(self,type):
		if type in self.FILE_TYPES:
			self.fileInfoType=type
			name = None
			if type == self.FILE_TYPE_IGNORE:
				name = 'Ignore'
			elif type == self.FILE_TYPE_MOVIE:
				name = 'Movie'
			elif type == self.FILE_TYPE_TV:
				name = 'TV'
			self.name = name
		else:
			raise ValueError('%s is not a valid type' % type )

	def isIgnored(self):
		return self.FILE_TYPE_IGNORE == self.fileInfoType

	def isTV(self):
		return self.FILE_TYPE_TV == self.fileInfoType

	def isMovie(self):
		return self.FILE_TYPE_MOVIE == self.fileInfoType

	def __repr__(self):
		return "<PathType('%s')>" % self.name

class DBArchiveDisk(Base):
	UUID_FILE_NAME='.hoarder_uuid'
	__tablename__ = 'archive_disk'
	id		= Column( 'disk_id', Integer, primary_key=True )
	identifier	= Column( 'disk_uuid', String, nullable=False )
	name		= Column( 'name', String )
	path		= Column( 'disk_path', String, nullable=False )
	totalSpace	= Column( 'total_space', Integer, nullable=False )
	freeSpace	= Column( 'free_space', Integer )
	lastIndexed	= Column( 'dt_last_index', String, nullable=False )
	#
	monitoredPaths = relationship('DBMonitoredPath', backref=backref('archiveDisk',uselist=False) )

	def __init__(self,path,uid):
		self.path=path
		self.identifier=uid

	@property
	def dateLastIndexed(self):
		return time.ctime( self.lastIndexed )

	def __repr__(self):
		return "<DBArchiveDisk('%s','%s')>" % (self.path, self.identifier)

	@property
	def available(self):
		rv = False
		if self.identifier is not None:
			if self.tagged and os.path.isdir( self.path ):
				f = open( self.fileIdentifier )
				uid = f.read()
				f.close()
				uid=uid[:-1]
				if self.identifier == uid:
					rv = True
		return rv

	@property
	def fileIdentifier(self):
		return os.path.join( self.path, self.UUID_FILE_NAME )
		
	def createDiskIdentifier(self):
		if not self.tagged:
			f = open( self.fileIdentifier, 'w' )
			f.write( self.identifier )
			f.write( '\n' )
			f.close()
		else:
			# error out; disk is already monitored!
			raise ValueError( 'Disk already contains a tag!' )

	@property
	def tagged(self):
		return os.path.exists( self.fileIdentifier )

class DBMonitoredPath(Base):
	__tablename__ = 'monitored_path'
	id = Column( 'monitored_path_id', Integer, primary_key=True )
	pathName = Column( 'path_name', String(255) )
	fileTypeCode = Column( 'file_type', String(50) )
	status = Column( 'status', String(1) )
	fileType = None
	diskId = Column( 'disk_id', Integer, ForeignKey('archive_disk.disk_id') )
	#files = relationship('DBFile', backref='monitoredPath')

	def __init__(self, pathName, fileType):
		self.pathName = pathName
		self.fileTypeCode = fileType
		#self.fileType = PathType(self.fileTypeCode)
		self.status = 'Y' ## by default we'll refresh soon after adding

	def __repr__(self):
		return "<DBMonitoredPath('%s','%s')>" % (self.pathName, self.fileType)

	@hybrid_property
	def refreshing(self):
		return self.status == 'Y'

	@refreshing.setter
	def refreshing(self,value):
		if value:
			self.status='Y'
		else:
			self.status='N'

	@property
	def absolutePathName(self):
		return self.pathName
		##FIXME: start storing invidual files and paths all relative to one another
		#return os.path.join( self.archiveDisk.pathName, self.pathName )

	@property
	def absolutePath(self):
		return self.absolutePathName

	@property
	def fileType(self):
		if self.fileType is None:
			self.fileType = PathType(self.fileTypeCode)
		return self.fileType

	def containsPath(self,path):
		return self.findPath(path) is not None

	def findPath(self,path):
		rv = None
		for p in self.paths:
			if p.pathName == path:
				rv = p
				break
		return rv
		

class DBPath(Base):
	__tablename__='path'
	id = Column('path_id', Integer, primary_key=True)
	dateAdded = Column('dt_added', String, nullable=False)
	pathName = Column('path_name', String, nullable=False)
	monitoredPathId = Column( 'monitored_path_id', ForeignKey('monitored_path.monitored_path_id') )
	monitoredPath = relationship('DBMonitoredPath', uselist=False, backref=backref('paths'))

	@property
	def absolutePath(self):
		return os.path.join( self.monitoredPath.absolutePath, self.pathName )

	@property
	def absolutePathName(self):
		return self.absolutePath

	def __repr__(self):
		return "<DBPath('%s','%s')>" % (self.monitoredPath.pathName, self.pathName)

	def containsFileName(self,fn):
		return self.findFileWithName(fn) is not None

	def findFileWithName(self,fn):
		rv = None
		for dbfile in self.files:
			if dbfile.fileName == fn:
				rv = dbfile
				break
		return rv
		

class DBFileExtension(Base):
	__tablename__ = 'process_ext'
	id = Column( 'ext_id', Integer, primary_key=True )
	extension = Column('ext', String(5))

	def __init__(self,ext):
		self.extension = ext

	def __repr__(self):
		return "<DBFileExtension('%s')>" % self.extension

class DBFile(Base):
	__tablename__='file'
	id = Column('file_id', Integer, primary_key=True )
	pathId = Column( 'path_id', Integer, ForeignKey('path.path_id') )
	fileName = Column( 'file_name', String )
	fileExtension = Column( 'file_ext', String )
	dateAdded = Column( 'dt_added', Integer )
	fileSize = Column( 'file_size', Integer )
	path = relationship(DBPath, uselist=False, backref='files')
	fileMetadata = relationship('DBFileMetadata', uselist=False, backref=backref('file',uselist=False) )

	def __init__(self,fileName,path,fileSize=None):
		self.fileName = fileName
		self.path = path
		self.fileSize = fileSize
		self.fileExtension = os.path.splitext( fileName )[1]

	def __repr__(self):
		return "<DBFile('%s','%d')>" % (self.fileName, self.fileSize)

	@property
	def absoluteFileName(self):
		return os.path.join( self.path.absolutePathName, self.fileName )
	
	@property
	def baseFileName(self):
		basePath = self.path.pathName
		fn = self.fileName.replace(basePath,'')
		return fn[1:]

	@property
	def relativeFileName(self):
		rv = self.fileName.replace( self.path.pathName,'' )
		rv = rv[1:] ## drop '/' at beginning of filename
		return rv

class DBFileMetadata(Base):
	__tablename__='file_info'
	fileId		= Column('file_id', Integer, ForeignKey('file.file_id'), primary_key=True )
	mdsum		= Column( 'mdsum', String )
	videoHeight	= Column( 'video_height', String )
	videoWidth	= Column( 'video_width', String )
	videoCodec	= Column( 'video_codec', String )
	audioCodec	= Column( 'audio_codec', String )
	audioChannels	= Column( 'audio_channels', String )
	duration	= Column( 'duration', String )
	imdbUrl		= Column( 'imdb_url', String )

	def __repr__(self):
		return "<DBFileMetadata('%s')>" % (str(self.fileId))
