#
# provider for tvrage.com
#

import tvrage.api
from . import TvProvider

class TvRageProvider(TvProvider):
	__provider_name__ = 'tvrage'

	def _convertSeason(self,season):
		rv = []
		for ept in season.items():
			ep = ept[1]
			cep = self._convertEpisode( ep )
			rv.append( cep )
		return rv

	def _convertEpisode(self,ep):
		rv = dict()
		rv['episode'] = ep.number
		rv['name'] = ep.title
		rv['plot'] = ep.summary
		rv['airdate'] = ep.airdate # FIXME: datetime.date(YYYY,MM,DD)
		return rv

	def _convertShow(self,show):
		rv = dict()
		rv['plot'] = show.synopsis
		rv['name'] = show.name
		rv['year'] = show.started
		rv['isEnded'] = bool(show.ended)
		
		seasons = dict()
		for s in xrange(1, show.seasons+1):
			season = show.season(s)
			seasons[s] = self._convertSeason(season)
		rv['seasons'] = seasons
		return rv

	def searchShowsWithName(self,name,year=None):
		rv = None
		try:
			show = tvrage.api.Show(name)
			rv = self._convertShow( show )
		except:
			pass
		return rv

	def getShowWithId( self, id):
		pass

	def getEpisodeForShow( self, showId, seasonNumber, episodeNumber):
		
		pass
