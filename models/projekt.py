from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Projekt(Base):
    __tablename__ = 'projektek'
    id = Column(Integer, primary_key=True)
    munkaszam = Column(String(50))
    projekt_sorszam = Column(String(50))
    projekt_megnevezes = Column(String(100))
    projektvezeto_id = Column(Integer, ForeignKey('felhasznalok.id'))
    statusz = Column(String(20), default='aktív')
    utalt_ido = Column(Float)
    alakado_felszin = Column(Float)
    projektvezeto = relationship("Felhasznalo", back_populates="projektek")
    projekt_alkatreszek = relationship("ProjektAlkatresz", back_populates="projekt")

class ProjektAlkatresz(Base):
    __tablename__ = 'projekt_alkatresz'
    id = Column(Integer, primary_key=True)
    projekt_id = Column(Integer, ForeignKey('projektek.id'))
    alkatresz_id = Column(Integer, ForeignKey('alkatreszek.id'))
    projekt = relationship("Projekt", back_populates="projekt_alkatreszek")
    alkatresz = relationship("Alkatresz", back_populates="projekt_alkatreszek")
