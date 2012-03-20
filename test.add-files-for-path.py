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

pathname = '/share/expired'

p = appContext.fileDAO.getMonitoredPath( pathname )

appContext.fileDAO.populateFilesForPath( p )

print 'Path: ', p.absolutePath
