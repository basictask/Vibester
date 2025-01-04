import os
import pandas as pd
from typing import Optional
from config import VibesterConfig
from flask_login import UserMixin
from cryptography.fernet import Fernet


class User(UserMixin):
    """
    User model
    """
    def __init__(self, username: str, role: str):
        self.id = username
        self.role = role


class UserManager:
    """
    Manages user data stored in a Parquet file with encrypted passwords.
    """
    def __init__(self, filepath: str, key: str):
        """
        Initializes the UserManager with the file path and encryption key.
        """
        if not key.endswith("="):
            key += "="

        self.filepath = filepath
        self.cipher = Fernet(key.encode('utf-8'))
        self.users = self._load_users()

    def _load_users(self) -> pd.DataFrame:
        """
        Loads user data from the Parquet file or initializes an empty DataFrame if the file doesn't exist.
        """
        if os.path.exists(self.filepath):
            return pd.read_parquet(self.filepath)  # Load users from Parquet file
        else:
            return pd.DataFrame(columns=["username", "password", "role"])  # Create empty DataFrame

    def _save_users(self) -> None:
        """
        Saves the current user data to the Parquet file.
        """
        self.users.to_parquet(self.filepath, index=False)  # Save users to Parquet file

    def add_user(self, username: str, password: str, role: str = "player") -> None:
        """
        Encrypts and adds a new user to the Parquet file if the username does not already exist.
        """
        encrypted_password = self.cipher.encrypt(password.encode('utf-8')).decode('utf-8')  # Encrypt password
        if username in self.users["username"].values:
            print(f"Error: User {username} already exists.")
            return
        self.users = pd.concat(
            [
                self.users,
                pd.DataFrame({"username": [username], "password": [encrypted_password], "role": [role]}),
            ],
            ignore_index=True
        )
        self._save_users()

    def remove_user(self, username: str) -> bool:
        """
        Removes a user by username from the Parquet file if they exist.
        """
        if self.user_exists(username=username):
            self.users = self.users[self.users["username"] != username]
            self._save_users()
            return True
        return False

    def verify_user(self, username: str, password: str) -> bool:
        """
        Verifies a user's password by decrypting the stored password and comparing it.
        """
        user_row = self.users[self.users["username"] == username]
        if not user_row.empty:
            stored_password = user_row["password"].iloc[0]
            try:
                decrypted_password = self.cipher.decrypt(stored_password.encode('utf-8')).decode('utf-8')
                return decrypted_password == password  # Check if decrypted password matches input
            except Exception as e:
                print(e)
                return False
        return False

    def user_exists(self, username: str) -> bool:
        """
        Returns whether a user exists in the Parquet file or not.
        """
        return username in self.users["username"].values

    def get_role(self, username: str) -> Optional[str]:
        """
        Returns the string form of the role of a user from the local database.
        """
        if self.user_exists(username=username):
            return self.users[self.users["username"] == username]["role"].iloc[0]
        return None


if __name__ == "__main__":
    # Sample instantiation for testing
    user_manager = UserManager(filepath=VibesterConfig.path_user, key=os.getenv("APP_USERS_ENCRYPTION_KEY"))
