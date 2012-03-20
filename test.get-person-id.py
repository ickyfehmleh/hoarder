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

person = appContext.movieDAO.getPersonWithImdbId( '0000229' )  # spielberg

if person is not None:
	print 'Person Name: %s' % person.name
else:
	print 'ERROR: NO SUCH PERSON!'
