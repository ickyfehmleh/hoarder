from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
import os.path
from .. import human_readable

class AbstractController(object):
	appContext = None

	def __init__(self,context):
		self.appContext=context

	def _templateWithName(self,filename):
		tmplLookup = self.appContext.templateLookup
		rv = tmplLookup.get_template( filename )
		return rv

	def getDatabaseSession(self):
		dbSession = self.appContext.dbSession
		s = dbSession()
		return s

	@property
	def fileDAO(self):
		return self.appContext.fileDAO

	@property
	def diskDAO(self):
		return self.appContext.diskDAO

	def renderResponse(self,response, page=None):
		# methods available to all responses
		response['human_readable'] = human_readable

		# wigets
		# count of files, movies people
		response['movieCount'] = self.appContext.movieDAO.getMovieCount()
		response['tvshowCount'] = 0 # FIXME
		response['tvshowEpisodeCount'] = 0 # FIXME
		response['fileCount'] = self.appContext.fileDAO.getFileCount()
		response['diskCount'] = self.appContext.diskDAO.getDiskCount()
		response['availableDiskCount'] = self.appContext.diskDAO.getAvailableDiskCount()
		# end widget_counts.tmpl requirements
		
		if not page.endswith( '.tmpl' ):
			page += '.tmpl'
		tmpl = self._templateWithName( page )
		return tmpl.render( **response )
