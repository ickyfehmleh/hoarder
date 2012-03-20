from imdb import IMDb
from . import MovieProvider
from ..log import HoarderLogger
import string

# keys for a provided movie:
#	name
#	year
#	tagline
#	plot
#	rating
#	genres (List<string>)	
#####

class ImdbProvider(MovieProvider):
	def __init__(self):
		self.imdb = IMDb()
		self.logger=HoarderLogger(__name__)

	def getPersonWithId(self,id):
		rv = None
		p = self.imdb.get_person(id)
		if p:
			rv = self._convertPerson(p)
		return rv

	def _convertPerson(self,person):
		rv = dict()
		#self.imdb.update(person,'all') ## makes things unbearably slow
		rv['id'] = person.personID
		rv['imdbId'] = person.personID
		rv['name'] = person['name']
		self.logger.debug( '_convertPerson(): converting %s' % person['name'] )
		## not sure how to fetch these from imdb, they're always null
		rv['imageUrl'] = person.get('headshot', None )
		rv['fullImageUrl'] = person.get( 'full-size headshot', None )
		return rv

	def _convertCastMember(self,castMember):
		rv = dict()
		self.logger.debug( '_convertCastMember(): Converting %s ' % str(castMember) )
		rv['roleId'] = castMember.roleID
		rv['person'] = self._convertPerson( castMember )

		try:
			rv['role'] = castMember.currentRole.get('name','UNKNOWN')
		except:
			## FIXME: account for imdb.utils.RolesList
			roleNames = []
			for cr in castMember.currentRole:
				if cr.has_key('name'):
					roleNames.append( cr['name'] )
			rv['role'] = string.join( roleNames, ', ' )
		return rv

	def _movieFromImdbMovie(self,movie,deepConvert=True):
		rv = dict()

		# figure out best name
		for name in ('title', 'smart long imdb canonical name', 'long imdb canonical title' ):
			if movie.has_key(name):
				rv['name'] = movie[name]
				break

		if movie.has_key('plot outline' ):
			rv['plot'] = movie['plot outline']
		else:
			if movie.has_key('plot'):
				## FIXME plot has ::<username>
				plot = movie['plot'][0]
				rv['plot']	= plot
			else:
				rv['plot'] = None

		rv['year']	= movie.get('year',None)
		rv['tagline']	= movie.get('tagline',None)
		rv['rating']	= movie.get('rating', None)
		rv['genres']	= movie.get('genres', None)
		rv['imdbId']	= movie.movieID
		rv['id']	= movie.movieID
		rv['mpaaRating']= movie.get('mpaa','')

		if deepConvert:
			# tell imdb to fetch details
			self.imdb.update(movie)
			#self.imdb.update(movie, 'taglines')
			coverUrls = []

			for key in ('cover url', 'full-size cover url'):
				if movie.has_key(key):
					coverUrls.append( movie[key] )
			rv['coverUrls']	= coverUrls

			# process cast
			cast = []
			for castMember in movie['cast']:
				cm = self._convertCastMember( castMember )
				cast.append( cm )
			rv['cast'] = cast

			# director(s)
			director = []
			if movie.has_key('director'):
				for dir in movie['director']:
					dirp = self._convertPerson( dir )
					director.append( dirp )
			rv['director'] = director

			# writer(s)
			writer = []
			if movie.has_key('writer'):
				for wr in movie['writer']:
					wp = self._convertPerson( wr )
					writer.append( wp )
			rv['writer'] = writer
		return rv

	def findMoviesWithName(self,name,year=None):
		rv = []
		if year is not None:
			year = int(year)
		results = self.imdb.search_movie(name)
		for r in results:
			if r['kind'] != 'movie':
				continue
			if year is not None and r.has_key('year') and r['year'] != year:
				continue
			print '### found movie %s' % r['title']
			movie = self._movieFromImdbMovie( r, deepConvert=False )
			rv.append( movie )
		return rv

	def getMovieWithId(self,id):
		rv = None
		m = self.imdb.get_movie(id)
		if m is not None:
			rv = self._movieFromImdbMovie( m )
		return rv

	def getMovieWithImdbId(self, id):
		return self.getMovieWithId(id)
