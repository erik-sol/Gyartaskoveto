# Konfiguráció – pl. SQLite adatbázis elérési útja

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'gyartas.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"