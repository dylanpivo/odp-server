from sqlalchemy import ARRAY, Boolean, Enum, Column, ForeignKey, ForeignKeyConstraint, Identity, Index, Integer, \
    Numeric, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import deferred, relationship

from odp.db import Base
from odp.const.db import SubmissionStatus
from odp.const import ODPMetadataSchema


class Submission(Base):
    """Represents a public catalog providing access to published
    digital object records."""

    __tablename__ = 'submission'

    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(String, nullable=False)
    data = Column(JSONB, nullable=False)
    status = Column(Enum(SubmissionStatus), nullable=False)
    dataset_file_name = Column(String, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True))
    collection_id = Column(String, ForeignKey('collection.id'), nullable=True)
    schema_id = Column(String, nullable=True)

    collection = relationship('Collection')

    _repr_ = 'id', 'status'
