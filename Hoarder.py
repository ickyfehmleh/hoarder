#!/usr/bin/python2.6
#
#
#

from multiprocessing import Process, Queue
from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy

from app.log import initLogging
from app.controller.home import HomeController
from app.controller.detailmovie import DetailMovieController
from app import AppContext
from app.dao import initDAO, initDatabase
from app.cron import initCron, startCron

import os
import os.path
import sys

#### push our path
sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )

#### setup logging
initLogging()

#logging.basicConfig(filename='hoarder.log', level=logging.DEBUG)

#### set up db access
Session = initDatabase(debug=True)

#### create tables
#Base.metadata.create_all( engine )

#### set up templating
templateLookup = TemplateLookup( directories = 'views',
		collection_size=500 )

### create app context
appContext = AppContext(session=Session, templateLookup=templateLookup)

#### set up DAOs
initDAO(appContext)

#### set up threads and queues
initCron(appContext)

#### set up controllers
root = HomeController(appContext)
#root.hello = HelloController(appContext)
root.movies = DetailMovieController(appContext)

### start background threads
startCron( appContext )

#### go!
cherrypy.tree.mount( root, '/' )
cherrypy.engine.start()
