from src.utils.db import Base
from sqlalchemy import Column, String, Integer, Enum, UniqueConstraint, ForeignKey
from src.relationships.enums import RelationshipsType

class RelationshipModel(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True)
    from_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    to_id = Column(String, ForeignKey("assets.id",  ondelete="CASCADE"), nullable=False) 
    type = Column(Enum(RelationshipsType), nullable=False)

    # Composite uniqueness constraint
    __table_args__ = (
        UniqueConstraint("from_id", "to_id", name="uq_relationship_from_to"),
    )