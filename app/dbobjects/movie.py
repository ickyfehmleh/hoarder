#
# database objects
#
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import backref, relationship
from .file import DBFile
from . import Base

class DBRole(Base):
	__tablename__ = 'movie_person_role'
	movieId		= Column( 'movie_id', Integer, ForeignKey('movie.movie_id' ) )
	personId	= Column( 'person_id', Integer, ForeignKey('person.person_id' ) )
	role		= Column('role', String, nullable=False )
	#
	movie		= relationship('DBMovie', uselist=False, backref=backref('cast') )
	person		= relationship('DBPerson', uselist=False, backref=backref('roles') )
	#
	__mapper_args__ = { 'primary_key': [movieId,personId] }

	@hybrid_property
	def roleName(self):
		return self.role

	def __init__(self,role):
		self.role = role

	def __repr__(self):
		mn = 'UNKNOWN MOVIE'
		pn = 'UNKNOWN PERSON'
		if self.movie is not None:
			mn = self.movie.name
		if self.person is not None:
			pn = self.person.name
		return "<DBRole('%s','%s','%s')>" % (pn, self.role, mn)

class DBPerson(Base):
	__tablename__ = 'person'
	id		= Column('person_id', Integer, primary_key=True)
	imdbId		= Column('imdb_id', String )
	name		= Column('name', String)
	imageUrl	= Column('img_url', String )
	fullImageUrl	= Column('full_img_url', String)

	def __repr__(self):
		return "<DBPerson('%s')>" % self.name


movieFileAssociation_table = Table('movie_file', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movie.movie_id')),
    Column('file_id', Integer, ForeignKey('file.file_id'))
)

movieDirectorAssociation_table = Table('movie_director', Base.metadata,
	Column( 'movie_id', Integer, ForeignKey('movie.movie_id' ) ),
	Column( 'person_id', Integer, ForeignKey('person.person_id') )
)

movieWriterAssociation_table = Table('movie_writer', Base.metadata,
	Column( 'movie_id', Integer, ForeignKey('movie.movie_id' ) ),
	Column( 'person_id', Integer, ForeignKey('person.person_id') )
)

class DBMovie(Base):
	__tablename__ = 'movie'
	id		= Column('movie_id', Integer, primary_key=True)
	name		= Column('name', String, nullable=False)
	year		= Column('year', String)
	mpaaRating	= Column('mpaa_rating', String)
	tagline		= Column('tagline', String)
	plot		= Column('plot', String)
	imdbId		= Column('imdb_id', String)
	imageUrl	= Column('img_url', String)
	#cast: handled in DBRole
	writers		= relationship('DBPerson', secondary=movieWriterAssociation_table, backref='writtenMovies')
	directors	= relationship('DBPerson', secondary=movieDirectorAssociation_table, backref='directedMovies')
	#genres
	##CAUSES ERROR???##
	files		= relationship(DBFile, secondary=movieFileAssociation_table, backref=backref('movie',uselist=False))

	@hybrid_property
	def imdbID(self):
		return self.imdbId

	@hybrid_property
	def imdbURL(self):
		return self.imdbUrl

	def __repr__(self):
		return "<DBMovie('%s', '%s', '%s')>" % (self.name, self.year, self.imdbId)
