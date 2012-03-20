import cherrypy
import os.path
from xml.dom import minidom, Node
import string
import tempfile
import shutil

class KeyedDict(object):
	d = dict()
	def __getattr__(self,name):
		return self.d.get(name,None)
	def __setattr__(self,name,value):
		self.d[name]=value

class AppContext(object):
	daoDict = dict()
	
	def __init__(self, session=None, templateLookup=None):
		self.dbSession = session
		self.templateLookup = templateLookup

	def __getattr__(self,name):
		rv = None
		if self.daoDict.has_key( name ):
			rv = self.daoDict[name]
		if rv is None:
			raise KeyError( 'No such key %s' % name )
		return rv

	def __setattr__(self,name,value ):
		try:
			# we cant set appContext for a dict or list,
			# and this should be fixed to be nicer
			# and not so hackish
			value.appContext=self
		except:
			pass
		self.daoDict[name] = value

class SafeWriteFile(object):
	def __init__(self,fileName,perms=0640):
		self._fileName=str(fileName)
		self._tempFile=str(tempfile.mktemp())
		self._fileHandle = open( self._tempFile, 'w' )
		self._permissions=perms

	def write(self,s):
		self._fileHandle.write( s )
		self._fileHandle.flush()

	def writeline(self,s):
		self.write( s+'\n' )

	def println(self,s):
		self.writeline(s)

	def close(self):
		self._fileHandle.close()
		shutil.move(self._tempFile, self._fileName)
		os.chmod( self._fileName, self._permissions )

######################################################################

def hours(n):
	if n == 0:
		return 'complete!'
	try:
		n = int(n)
		assert n >= 0 and n < 5184000  # 60 days
	except:
		return 'unknown'
	m, s = divmod(n, 60)
	h, m = divmod(m, 60)
	if h > 0:
		return '%d hour %02d min %02d sec' % (h, m, s)
	else:
		return '%d min %02d sec' % (m, s)
######################################################################
def human_readable(n):
	n = long(n)
	unit = [' B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
	i = 0
	if (n > 999):
		i = 1
		while i + 1 < len(unit) and (n >> 10) >= 999:
			i += 1
			n >>= 10
		n = float(n) / (1 << 10)
	if i > 0:
		size = '%.1f' % n + '%s' % unit[i]
	else:
		size = '%.0f' % n + '%s' % unit[i]
	return size
######################################################################
def escapeFilename(s):
	return re.sub("[^A-Za-z0-9\.]", "_", s)
######################################################################
def findNodeName(parentNode, name):
	rv = None
	for childNode in parentNode.childNodes:
		if name == childNode.nodeName:
			rv = childNode
			break
	return rv

def textForNode(parentNode):
	s = ''
	for childNode in parentNode.childNodes:
		content = []
		for textNode in childNode.childNodes:
			content.append( textNode.nodeValue )
		s= string.join( content )
	return s
