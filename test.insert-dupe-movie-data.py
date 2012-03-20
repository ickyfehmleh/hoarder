#!/usr/bin/python2.6
#
#
#
from app import AppContext
from app.dao import initDatabase, initDAO
from app import human_readable as hr

Session = initDatabase(debug=True)
appContext = AppContext(session=Session,templateLookup=None)
initDAO(appContext)

imdbUrl = 'http://www.imdb.com/title/tt1341167/'

print 'IMDB URL: %s' % imdbUrl

movie = appContext.movieDAO.findMovieWithImdbUrl( imdbUrl )

print 'Movie Name: %s' % movie.name

appContext.movieDAO.createMovie( movie )
