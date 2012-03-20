from .. import log
from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
import os.path
from . import AbstractController
from .. import human_readable as hr

class HomeController(AbstractController):
	logger = log.HoarderLogger(__name__)

	@cherrypy.expose
	def index(self,response=dict()):
		# all monitored disks
		allDisks = self.appContext.diskDAO.getAllDisks()
		self.logger.info( 'Fetched %d disks' % len(allDisks) )
		response['allDisks'] = allDisks

		# file types
		fileTypes = self.appContext.fileDAO.getAllFileTypes()
		response['allFileTypes'] = fileTypes

		# last items added
		lastFiles = self.appContext.fileDAO.getLastFilesAdded(num=20)
		response['lastItems'] = lastFiles

		# render
		return self.renderResponse( response, page='home' )

	@cherrypy.expose
	def detail(self,response=dict()):
		response['msg'] = 'Worked!'
		return self.renderResponse( response, page='test' )
