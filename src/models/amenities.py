from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.property import Property

class PropertyAmenity(Base):
    __tablename__ = "property_amenities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_id: Mapped[str] = mapped_column(
        String(255), 
        ForeignKey("properties.property_id"), 
        unique=True
    )
    
    amenities: Mapped[dict] = mapped_column(JSONB)

    # Link back
    property: Mapped["Property"] = relationship("Property", back_populates="amenity_data")