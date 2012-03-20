from ..dbobjects.file import DBArchiveDisk
from basedao import AbstractDAO
from ..import log
import os.path
import time
import os
import uuid

class DiskDAO(AbstractDAO):
	logger = log.HoarderLogger(__name__)

	def getDiskCount(self):
		session = self.getDatabaseSession()
		rv = session.query(DBArchiveDisk).count()
		return rv

	def getAvailableDiskCount(self):
		rv = 0
		allDisks = self.getAllDisks()
		for disk in allDisks:
			if disk.available:
				rv += 1
		return rv

	def refreshAvailableDisks(self):
		disks = self.getAllDisks()
		for currentDisk in disks:
			if currentDisk.available:
				self._updateDiskFreeSpace( currentDisk )
				self.getDatabaseSession().commit()

	def createNewDiskWithPath(self,rootPath,name=None):
		rv = None
		if os.path.exists( rootPath ) and os.path.isdir( rootPath ):
			id = uuid.uuid1().hex
			rv = DBArchiveDisk(rootPath,id)
			if not rv.tagged:
				rv.createDiskIdentifier()
				rv.name=name
				self._updateDiskFreeSpace( rv, setTotal=True )
				session = self.getDatabaseSession()
				session.add( rv )
				session.commit()
		return rv

	def _getDiskSpace( self, path ):
		st = os.statvfs( path )
		freeSpace = (st.f_frsize * st.f_bavail)
		totalSpace = (st.f_frsize * st.f_blocks)
		return freeSpace, totalSpace

	def _updateDiskFreeSpace(self, dbdisk,setTotal=False):
		path = dbdisk.path
		free, total = self._getDiskSpace( dbdisk.path )
		dbdisk.freeSpace = free
		if setTotal:
			dbdisk.totalSpace = total
		dbdisk.lastIndexed = time.time()

	def getAllDisks(self):
		session = self.getDatabaseSession()
		rv = session.query(DBArchiveDisk).all()
		self.logger.info( 'Fetched %d disks' % len( rv ) )
		return rv

	def _getDiskWithArgs(self,**kwargs):
		rv = None
		try:
			rv = self.getDatabaseSession().query(DBArchiveDisk).filter_by(**kwargs).one()
		except:
			pass
		return rv

	def getDiskWithId(self,id):
		return self._getDiskWithArgs( id=id )

	def getDiskForPath(self,path):
		return self._getDiskWithArgs( path=path )
