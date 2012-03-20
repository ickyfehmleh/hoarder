#!/usr/bin/python2.6
#
#
#
from app import AppContext
from app.dao import initDatabase, initDAO
from app import human_readable as hr
from app.cron.movie import MovieScanner
from app.log import initLogging

initLogging()
Session = initDatabase(debug=True)
appContext = AppContext(session=Session,templateLookup=None)
initDAO(appContext)

scanner = MovieScanner( appContext )

scanner.process()
