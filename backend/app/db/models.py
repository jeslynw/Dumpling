'''
define tables with classes (SQLAlchemy ORM)
'''

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.database import Base