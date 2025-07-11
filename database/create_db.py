from models import Base, Jogosultsag, Felhasznalo
from config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def initialize_database():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    if session.query(Jogosultsag).count() == 0:
        admin = Jogosultsag(nev="Admin", leiras="Teljes hozzáférés")
        pm = Jogosultsag(nev="Projektmenedzser", leiras="Projekt kezelés")
        tech = Jogosultsag(nev="Technológus", leiras="Technológiai adatok")
        op = Jogosultsag(nev="Operátor", leiras="Státuszfrissítés")
        session.add_all([admin, pm, tech, op])
        session.commit()

    if session.query(Felhasznalo).count() == 0:
        admin_user = Felhasznalo(
            nev="Admin",
            felhasznalonev="admin",
            jelszo="admin123",
            munkakor="Admin",
            jogosultsag_id=1  # Feltételezve, hogy az Admin az első bejegyzés
        )
        session.add(admin_user)
        session.commit()

    print("✅ Adatbázis inicializálva.")
