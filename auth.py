import logging
import os


class Login:

    def __init__(self, loader, logger: logging.Logger, username):
        self.loader = loader
        self.logger = logger
        self.username = username

    @property
    def session_path(self):
        os.makedirs("sessions", exist_ok=True)
        return f"sessions/{self.username}"

    def login(self, password: str) -> bool:

        try:
            self.loader.load_session(self.username, self.session_path)
            self.logger.info(f"Session {self.username} has been loaded ✅")
            if self.loader.is_logged_in:
                self.logger.info(f"Session valid ✅")
                return True
            else:
                self.logger.error(f"Session expired!")
        except:
            self.logger.error("Failed to load session!")

        try:
            self.logger.info(f"Logging in as {self.username}")
            self.loader.login(self.username, password)
            self.logger.info(f"Logged in successfully ✅")
        except:
            self.logger.error(f"login failed!")
            return False

        try:
            self.logger.info(f"Saving session...")
            self.loader.save_session(self.session_path)
            self.logger.info(f"Session saved ✅")
            return True
        except:
            self.logger.error("Failed to save session!")
