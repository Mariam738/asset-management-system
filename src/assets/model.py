import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Enum, DateTime, JSON, UniqueConstraint, Index
from src.utils.db import Base
from src.assets.enums import AssetStatus, AssetType
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableDict

class AssetModel(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, unique=True)#, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(AssetType), nullable=False)
    value = Column(String, nullable=False)
    status = Column(Enum(AssetStatus), nullable=False)

    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    source = Column(String, nullable=False) # scan, import, maunal (string for flexibility)
    tags = Column(ARRAY(String), default=[], nullable=False)
    # meta = Column(JSON, default=dict, nullable=False) # metadata is reserved in sqlalchemy
    meta = Column(MutableDict.as_mutable(JSONB), default=dict, nullable=False) # metadata is reserved in sqlalchemy

    # Composite uniqueness constraint
    __table_args__ = (
        UniqueConstraint("type", "value", name="uq_asset_type_value"),
        # Indexes to speed up filtering
        Index("idx_asset_type", "type"),
        Index("idx_asset_status", "status"),
        Index("idx_asset_value", "value"),
        Index("idx_asset_tags_gin", "tags", postgresql_using="gin")  # gin for array filtering
    )