import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from scripts.startup.handle_login import LoginHandler
# from function.handle_boothid import BoothIDHandler
# from function.handle_session import HeartbeatWorker

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()

def main():
    app = QApplication(sys.argv)

    # Show login window first
    login_handler = LoginHandler()

    if login_handler.exec():  # Wait for login to complete
        # booth_handler = BoothIDHandler(login_handler.get_cookies())
        # if booth_handler.exec():
        #     # Both login and booth ID verification successful
        #     booth_id = booth_handler.get_booth_id()
        #     heartbeat_worker = HeartbeatWorker(boothId=booth_id)
        #     # heartbeat_worker.connection_lost.connect(handleConnectionLost)
        #     heartbeat_worker.start()
            # Continue with the main application
        main_window = MainUI()
        main_window.show()
        sys.exit(app.exec())  # Start the application loop


if __name__ == "__main__":
    main()
