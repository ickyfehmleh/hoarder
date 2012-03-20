from ..dao.movie import MovieDAO
from ..dbobjects.file import PathType
from ..log import HoarderLogger

class MovieScanner(object):
	appContext = None

	def __init__(self,appContext):
		self.appContext = appContext
		self.logger = HoarderLogger(__name__)

	def _processPath(self,dbpath):
		for dbf in dbpath.files:
			self.logger.debug('Processing file %s' % dbf.absoluteFileName )	

			if dbf.fileMetadata is None:
				continue
			if dbf.fileMetadata.imdbUrl is None:
				continue
			if dbf.movie is not None:
				continue

			imdbUrl = dbf.fileMetadata.imdbUrl
			self.logger.debug( 'Trying to find imdb url %s' % imdbUrl )
			movie = self.appContext.movieDAO.findMovieWithImdbUrl( imdbUrl )

			if not dbf in movie.files:
				movie.files.append( dbf )
			else:
				self.logger.debug( 'Already have file %s associated with movie %s' % (str(dbf.id), str(movie.id) ) )

			self.appContext.movieDAO.createMovie( movie )
	
	def process(self):
		# get all files
		allMoviePaths = self.appContext.fileDAO.getAllMonitoredPaths( type=PathType.FILE_TYPE_MOVIE )
		
		for dbmpath in allMoviePaths:
			for dbpath in dbmpath.paths:
				self._processPath( dbpath )

################################################
class FileMovieScanner(object):
	appContext = None
	
	def process(self):
		# find all files where:
		#  * the monitored_dir is of type 'M'
		#  * there is no movie_file.file_id
		# best guess as to movie name
		# record guesses
		pass
