#
# keys for a provided movie:
#       name
#       year
#       tagline
#       plot
#       rating
#       genres (List<string>)
#####

class MovieProvider(object):
	def findMoviesWithName(self,name,year=None):pass
	def getMovieWithId(self,id):pass
	def getMovieWithImdbId(self,id):pass

class TvProvider(object):
	def searchShowsWithName(self,name,year=None):pass
	def getShowWithId(self, id):pass
	def getEpisodeForShow( self, showId, seasonNumber, episodeNumber):pass
