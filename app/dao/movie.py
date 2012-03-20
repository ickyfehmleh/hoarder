# movie dao

from basedao import AbstractDAO
from ..log import HoarderLogger
from ..providers.imdbmovie import ImdbProvider
from ..dbobjects.file import DBFileMetadata,DBFile
from ..dbobjects.movie import DBMovie, DBPerson, DBRole
import urlparse
import os.path
from sqlalchemy.orm.exc import NoResultFound

class MovieDAO(AbstractDAO):
	provider = ImdbProvider()
	logger = HoarderLogger(__name__)

	def searchMoviesWithName(self,name,year=None):
		args = dict()
		args['name'] = name  ## how to account for case insensitivity?
		if year is not None:
			args['year'] = year
		return self._getMoviesWithArgs( args )

	def getMovieCount(self):
		session = self.getDatabaseSession()
		rv = session.query(DBMovie).count()
		return rv

	def getMoviePersonCount(self):
		session = self.getDatabaseSession()
		rv = session.query(DBPerson).count()
		return rv

	def getAllImdbUrls(self):
		rv = []
		session = self.getDatabaseSession()
		metadata = session.query(DBFileMetadata).filter(DBFileMetadata.imdbUrl != None).all()
		for m in metadata:
			d = dict()
			d['imdbUrl'] = m.imdbUrl
			d['file'] = m.file
			rv.append( d )
		return rv

	def _getSingleMovieWithArgs(self,**kwargs):
		rv = None
		all = self._getMoviesWithArgs(**kwargs)
		if all is not None and len(all) >= 1:
			rv = all[0]
		return rv

	def _getMoviesWithArgs(self,**kwargs):
		rv = None
		session = self.getDatabaseSession()
		try:
			rv = session.query(DBMovie).filter_by(**kwargs).all()
		except:
			pass
		return rv

	def getMovieWithId(self,id):
		return self._getSingleMovieWithArgs( id=id )

	def getMovieWithName(self,name):
		return self._getSingleMovieWithArgs( name=name )

	def cleanImdbId(self,imdbId):
		imdbId=str(imdbId)
		if imdbId.startswith('tt'):
			imdbId=imdbId[2:]
		return int(imdbId)

	def getMovieWithImdbId(self,imdbId):
		rv = None
		imdbId = self.cleanImdbId( imdbId )
		return self._getSingleMovieWithArgs( imdbId=imdbId )

	def convertProvidedMovie(self,pm,deepCopy=True):
		rv = DBMovie()
		rv.name		= pm['name']
		rv.year		= str(pm['year'])
		rv.mpaaRating	= pm['mpaaRating']
		rv.plot		= pm['plot']
		rv.imdbId	= pm['imdbId']

		if deepCopy:
			if pm.has_key('imageUrl'):
				urls = pm['imageUrl']
				rv.imageUrl	= urls[0]

			# directors
			if pm.has_key('director'):
				directors = pm['director']
				for cd in directors:
					director = self.convertProvidedPerson(cd)
					rv.directors.append( director )

			# writers
			if pm.has_key('writer'):
				writers = pm['writer']
				for cw in writers:
					writer = self.convertProvidedPerson(cw)
					rv.writers.append( writer )

			# cast
			if pm.has_key('cast'):
				cast = pm['cast']
				for currRole in cast:
					role = self.convertProvidedRole(currRole )
					print '### Adding role %s to movie %s' % (role.role, rv.name)
					role.movie = rv
					#rv.cast.append( role )
		return rv

	def getPersonWithImdbId(self,personId):
		rv = None
		session = self.getDatabaseSession()
		try:
			rv = session.query(DBPerson).filter_by(imdbId=personId).one()
		except NoResultFound, nrf:
			pass
		return rv

	def convertProvidedRole(self,role):
		dbr = DBRole(role['role'])
		providedPerson = role['person']
		dbperson = self.convertProvidedPerson( providedPerson )
		dbr.person = dbperson
		return dbr

	def convertProvidedPerson(self,person):
		dbp = None
		imdbId = person.get('imdbId', None)
		if imdbId is not None:
			self.logger.debug( 'convertProvidedPerson(): trying to fetch where ImdbID == %s' % imdbId )
			dbp = self.getPersonWithImdbId(imdbId)

		if dbp is None:
			self.logger.debug( 'convertProvidedPerson(): Creating new person with IMDB ID == \'%s\'' % imdbId )
			dbp = DBPerson()
			dbp.name = person['name']
			dbp.imdbId = person.get('imdbId', None)
			dbp.imageUrl = person.get('imageUrl', None)
			dbp.fullImageUrl = person.get('fullImageUrl', None)
			## if we dont add the person now, future calls to getPersonWithImdbId() will fail and produce
			## multiple records
			session = self.getDatabaseSession()
			session.add( dbp )
			session.commit()
		return dbp

	def findMovieWithImdbUrl(self,url):
		r = urlparse.urlsplit( url )
		(title,imdbId) = os.path.split( os.path.dirname( r.path ) )
		return self.findMovieWithImdbId( imdbId )

	def findMovieWithImdbId(self,imdbId):
		imdbId = self.cleanImdbId( imdbId )
		fetchedMovie = self.getMovieWithImdbId( imdbId )
		if fetchedMovie is None:
			m = self.provider.getMovieWithImdbId( imdbId )
			if m is not None:
				fetchedMovie = self.convertProvidedMovie(m)
		return fetchedMovie

	def createMovie( self, dbmovie ):
		insert = True
		session = self.getDatabaseSession()
		if dbmovie in session:
			insert = False
		else:
			if dbmovie.imdbId is not None:
				existingMovie = self.getMovieWithImdbId( dbmovie.imdbId )
				if existingMovie is not None:
					insert = False
		if insert:
			session.add( dbmovie )
		session.commit()

	def findMovieWithName(self,name,year=None):
		rv = []
		matches = self.provider.findMoviesWithName(name,year=year)
		for match in matches:
			m = self.convertProvidedMovie( match, deepCopy=False )
			rv.append( m )
		return rv
