from database.create_db import initialize_database
from gui.views.login_view import login_window

if __name__ == "__main__":
    initialize_database()
    login_window()