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

data = appContext.movieDAO.getAllImdbUrls()[0]

imdbUrl = data['imdbUrl']
dbfile = data['file']

print 'IMDB URL: %s' % imdbUrl

movie = appContext.movieDAO.findMovieWithImdbUrl( imdbUrl )

print 'File: %s' % dbfile.fileName
print 'Movie Name: %s' % movie.name

appContext.movieDAO.createMovie( movie )
