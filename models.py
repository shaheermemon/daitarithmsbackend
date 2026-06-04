from sqlalchemy import Column, Integer, String
from database import Base


# =========================
# FEATURES
# =========================

class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)


# =========================
# MENUS
# =========================

class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String)
    position = Column(Integer)