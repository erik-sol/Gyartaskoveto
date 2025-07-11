from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Alkatresz(Base):
    __tablename__ = 'alkatreszek'
    id = Column(Integer, primary_key=True)
    hatarido = Column(DateTime)
    rogzitett_datum = Column(DateTime)
    nev = Column(String(100), nullable=False)
    statusz = Column(String(20), default='normál')
    a_oldal = Column(String(10))
    b_oldal = Column(String(10))
    c_oldal = Column(String(10))
    d_oldal = Column(String(10))
    gyartando_darab = Column(Integer, default=0)
    gyartando_tukrozott_darab = Column(Integer, default=0)
    lemezvastagsag = Column(String(10))
    anyag = Column(String(50))
    irodai_megjegyzes = Column(Text)
    tipus = Column(String(50))
    rajz_3d = Column(String(10))
    rajz_2d = Column(String(10))
    kiadva = Column(String(10))
    profil_hossz = Column(Float)
    felszin = Column(Float)
    tomeg = Column(Float)
    felulirt_statusz = Column(Boolean, default=False)
    projekt_alkatreszek = relationship("ProjektAlkatresz", back_populates="alkatresz")
    feladatok = relationship("Feladat", back_populates="alkatresz")

class Feladat(Base):
    __tablename__ = 'feladatok'
    id = Column(Integer, primary_key=True)
    alkatresz_id = Column(Integer, ForeignKey('alkatreszek.id'))
    technologia_tipus = Column(String(50))
    statusz = Column(String(20), default='normál')
    elkeszult_darab = Column(Integer, default=0)
    elkeszult_tukrozott_darab = Column(Integer, default=0)
    dolgozoi_megjegyzes = Column(Text)
    felulirt_statusz = Column(Boolean, default=False)

    alkatresz = relationship("Alkatresz", back_populates="feladatok")