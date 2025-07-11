from sqlalchemy.orm import Session
from models import Felhasznalo

# MVP: sima jelszó-összehasonlítás (később bcrypt hash lesz)
def bejelentkezes(session: Session, felhasznalonev: str, jelszo: str) -> Felhasznalo | None:
    felhasznalo = session.query(Felhasznalo).filter_by(felhasznalonev=felhasznalonev).first()
    if felhasznalo and felhasznalo.jelszo == jelszo:
        return felhasznalo
    return None