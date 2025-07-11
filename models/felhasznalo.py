from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Jogosultsag(Base):
    __tablename__ = 'jogosultsagok'
    id = Column(Integer, primary_key=True)
    nev = Column(String(50), nullable=False)
    leiras = Column(Text)
    felhasznalok = relationship("Felhasznalo", back_populates="jogosultsag")

class Felhasznalo(Base):
    __tablename__ = 'felhasznalok'
    id = Column(Integer, primary_key=True)
    nev = Column(String(100), nullable=False)
    felhasznalonev = Column(String(50), unique=True, nullable=False)
    jelszo = Column(String(128), nullable=False)
    munkakor = Column(String(50))
    jogosultsag_id = Column(Integer, ForeignKey('jogosultsagok.id'))
    jogosultsag = relationship("Jogosultsag", back_populates="felhasznalok")
    projektek = relationship("Projekt", back_populates="projektvezeto")