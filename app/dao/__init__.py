import os.path
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper, relation, scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import joinedload
import threading

from file import FileDAO
from movie import MovieDAO
from metadata import FileMetadataDAO
from disk import DiskDAO

def initDatabase(debug=False):
	dbPath = os.path.abspath( 'test.db' )
	engine = create_engine( 'sqlite:///' + dbPath,echo=debug )
	Session = scoped_session( sessionmaker( bind=engine ) )
	return Session

def initDAO(appContext):
	dbSession = appContext.dbSession

	appContext.fileDAO = FileDAO(dbSession)
	appContext.movieDAO = MovieDAO(dbSession)
	appContext.fileMetadataDAO = FileMetadataDAO(dbSession)
	appContext.diskDAO = DiskDAO(dbSession)
