import os
import os.path
import re
from hashlib import md5 as md5

from ..import log
from ..dbobjects.file import DBFileMetadata
from basedao import AbstractDAO
from hachoir_parser import createParser
from hachoir_metadata import extractMetadata
from hachoir_core.cmd_line import unicodeFilename

class FileMetadataDAO(AbstractDAO):
	logger = log.HoarderLogger(__name__)
	processMdsums = False

	def createMetadataForFile(self,dbf):
		md = None
		try:
			info = self._parseMetadataForFile( dbf )
			if info is not None:
				md = self._convertInfoToMetadata( info, dbf )
		except:
			pass
		return md

	def _parseMetadataForFile( self, dbf ):
		info = None
		filename = str(dbf.absoluteFileName)
		filename, realname = unicodeFilename(filename), filename
		parser = createParser( filename, realname )
		try:
			metadata = extractMetadata( parser )
		except:
			pass
	
		if metadata is not None:
			metadata = metadata.exportPlaintext()
			info = self._convertMetadataToMap(metadata)
		return info

	def _convertInfoToMetadata( self, info, dbf ):
		rv = DBFileMetadata()
		rv.file		 = dbf
		rv.duration	 = self._getDuration( info )
		rv.videoWidth	 = self._getVideoWidth( info )
		rv.videoHeight	 = self._getVideoHeight( info )
		rv.videoCodec	 = self._getVideoCodec( info )
		rv.imdbUrl	 = self._getImdbUrlForFile( dbf )
		rv.audioCodec	 = self._getAudioCodec( info )
		rv.audioChannels = self._getAudioChannels( info )

		if self.processMdsums:
			self.logger.debug( 'Calculating md5 sum for %s' % dbf.absoluteFileName )
			rv.mdsum	 = self._getMdsumForFile( dbf )
		return rv
	
	def _convertMetadataToMap(self, metadata):
		info = dict()
		parentItem = None
		for item in metadata:
			if item.startswith('- '):
				if item.startswith( '- ' ):
					item = item[2:]
				idx = item.index(':')
				key = item[:idx].lstrip().rstrip()
				value = item [idx+2:].lstrip().rstrip()
				childDict = info[parentItem]
				childDict[key]=value
			else:
				parentItem = item
				info[parentItem] = dict()
		return info

	def _getMetaDataKey(self,info, key,parentKey=None):
		rv = None
		d = info
		if parentKey is not None:
			pk = parentKey+':'
			if info.has_key(pk):
				d = info[pk]
			else:
				d = dict()  ## FIXME leaky objects?
		rv = d.get(key,None)
		return rv

	def _getAudioChannels(self,info):
		return self._getMetaDataKey( info, 'Channel', parentKey='Audio stream' )

	def _getAudioCodec(self,info):
		return self._getMetaDataKey( info, 'Compression', parentKey='Audio stream' )

	def _getVideoCodec(self,info):
		return self._getMetaDataKey( info, 'Compression', parentKey='Video stream' )

	def _getVideoHeight(self,info):
		rv = None
		s = self._getMetaDataKey( info, 'Image height', parentKey='Video stream' )
		if s is not None:
			rv = s.replace(' pixels','' )
		return rv

	def _getVideoWidth(self,info):
		rv = None
		s = self._getMetaDataKey( info, 'Image width', parentKey='Video stream' )
		if s is not None:
			rv = s.replace(' pixels','' )
		return rv

	def _getDuration(self,info):
		rv = None
		s = self._getMetaDataKey( info, 'Duration', parentKey='Common' )
		if s is not None:
			rv = s
		return rv

	def _getImdbUrlFromFile(self, nfoFile):
		url = None
		f = open( nfoFile, 'r' )
		for line in f.readlines():
			idx = 0
			try:
				idx = line.index('imdb.com')
				m = re.search( 'http://([0-9A-Za-z\.\/]+)', line )
				url = m.group()
				break
			except:
				continue
		f.close()
		return url

	def _getMdsumForFile(self,dbf):
		fileName = dbf.filePath
		buf = None
		# calc md5sum
		m = md5()
		f = file( self._fileName )
		while '' != buf:
			buf = f.read(2048)  # might want to increase this?
			m.update( buf )
		f.close()
		self._mdsum = m.hexdigest()
		return mdsum

	def _findNfoFile(self,dirn):
		rv = None
		for root, dirs, files in os.walk( dirn ):
			for cf in files:
				if cf.endswith( '.nfo' ):
					rv = os.path.join( root, cf )
					break
		self.logger.debug( 'findNfoFile(%s): %s' % (dirn, rv) )
		return rv

	def _getImdbUrlForFile(self,dbf):
		self.logger.debug( '_getImdbUrlForFile(): checking %s' % dbf.fileName )
		imdbUrl = None
		nfoFile = None
		fileName = dbf.fileName
		# figure out if one level up is valid
		if dbf.path.pathName != dbf.path.monitoredPath.pathName:
			fullDir = dbf.path.pathName
			self.logger.debug( '_getImdbUrlForFile(): scanning %s' % fullDir )
			nfoFile = self._findNfoFile( fullDir )
		else:
			# guess that <file>.nfo exists
			(fn,ext) = os.path.splitext( fileName )
			nfoFile = fn+'.nfo'
		if nfoFile is not None and os.path.exists( nfoFile ):
			self.logger.debug( '_getImdbUrlForFile(%s): %s' % (dbf.fileName, nfoFile) )
			imdbUrl = self._getImdbUrlFromFile( nfoFile )
		self.logger.debug( '_getImdbUrlForFile(%s): returning %s' % (dbf.fileName, imdbUrl) )
		return imdbUrl
