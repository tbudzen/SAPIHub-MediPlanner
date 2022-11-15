import configparser
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from recommendation.model.dbModels import base

config = configparser.RawConfigParser()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = ROOT_DIR + '/DbConfig.properties'

# db = create_engine(config.get('DatabaseSection', 'database.connectionString'))
db = create_engine("postgres://mediplanr:medi999@localhost:5432/mediplan")
Session = sessionmaker(db)
session = Session()
base.metadata.create_all(db)
