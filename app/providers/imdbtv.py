from imdb import IMDb

class ImdbTvProvider(object):
	imdb = IMDb()

	def _convertProvidedShow(self,show):
		rv = dict()
		rv['name'] = show.get('title',None)
		rv['plot'] = show.get('plot outline', None)
		rv['year'] = show.get('year', None)
		return rv

	def searchShowsWithName(self,name,year=None):
		rv = []
		results = self.imdb.search_movie(name)
		for r in results:
			if r['kind'] != 'tv series':
				continue
			if year is not None and r.has_key('year') and r['year'] != year:
				continue
			show = self._convertProvidedShow( r )
			rv.append( show )
		return rv

	def getShowWithId( self, id):
		rv = None
		show = self.imdb.get_movie(id)
		if show:
			rv = self._convertProvidedShow( show )
		return rv

	def getEpisodeForShow( self, showId, seasonNumber, episodeNumber):
		rv = None
		show = self.imdb.get_movie(showId)
		if show:
			self.imdb.update(show,'episodes')
			# doesnt work!
		return rv
