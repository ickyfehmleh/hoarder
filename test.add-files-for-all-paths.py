#!/usr/bin/python2.6
#
#
#
from app import AppContext
from app.dao import initDatabase, initDAO
from app import human_readable as hr

Session = initDatabase()
appContext = AppContext(session=Session,templateLookup=None)
initDAO(appContext)

paths = appContext.fileDAO.getAllMonitoredPaths()
for p in paths:
	appContext.fileDAO.populateFilesForPath( p )
	print 'Path %s refreshed' % p.pathName
