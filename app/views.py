from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
from dbobjects import *
import os.path

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

	def renderResponse(self,resp, page=None):
		if not page.endswith( '.tmpl' ):
			page += '.tmpl'
		tmpl = self._templateWithName( page )
		return tmpl.render( **resp )

##########################################################################

class HomeController(AbstractController):
	@cherrypy.expose
	def index(self,response=None):
		resp = response
		if resp is None:
			resp = dict()
		allPaths = self.appContext.fileDAO.getAllMonitoredPaths()
		fileTypes = self.appContext.fileDAO.getAllFileTypes()
		resp['lst'] = allPaths
		resp['fileTypes'] = fileTypes
		return self.renderResponse( resp, page='home' )

	@cherrypy.expose
	def addExtension(self,ext=None):
		resp = dict()
		rv = None
		pageName = 'error'
		if ext:
			self.appContext.fileDAO.addExtension( ext )
			rv = self.index()
		else:
			resp['errorMsg'] = 'Please enter an extension to add!'
			rv = self.renderResponse( resp, page='error' )
		return rv

	@cherrypy.expose
	def detailFile(self,fileid=None):
		rv = None
		resp = dict()
		pageName='error'
		fileid=int(fileid)
		fetchedFile = self.appContext.fileDAO.getFileWithFileId(fileid)
		resp['selectedFile'] = fetchedFile
		resp['fileMetadata'] = fetchedFile.fileMetadata
		rv = self.renderResponse( resp, page='detailFile' )
		return rv

	@cherrypy.expose
	def listdir(self,path=None):
		resp = dict()
		p = self.appContext.fileDAO.getMonitoredPath(path)
		resp['path'] = p
		return self.renderResponse(resp, page='adddir')

	@cherrypy.expose
	def addDir(self, name=None,type=None):
		resp = dict()
		rv = None
		if name and type:
			# verify path doesnt exist already
			if os.path.exists( name ):
				p = self.appContext.fileDAO.createNewMonitoredPath( name,type )
				resp['name'] = name
				resp['msg'] = 'Directory %s added' % name
				resp['path'] = p
				rv = self.renderResponse(resp, page='adddir')
			else:
				resp['errorMsg'] = 'Please enter a directory that exists!'
				rv = self.renderResponse( resp, page='error' )
		else:
			resp['errorMsg'] = 'Enter a directory name!'
			rv = self.renderResponse( resp, page='error' )
		return rv

##########################################################################

class HelloController(AbstractController):
	@cherrypy.expose
	def default( self, name ):
		resp = {'hello':name}
		return self.renderResponse( resp, page='hello.tmpl' )
