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

movie = appContext.movieDAO.getMovieWithImdbId( '1100051' ) # Bereavement

if movie:
	print 'Name: %s' % movie.name
	print 'Directors:'
	for cd in movie.directors:
		print '-- Name: %s' % cd.name
	print 
	print 'Writers:'
	for cw in movie.writers:
		print '-- Name: %s' % cw.name
	print

	print 'Cast:'
	cast = movie.cast[:5]
	for cc in cast:
		print '-- %s as %s' % (cc.person.name, cc.role)
