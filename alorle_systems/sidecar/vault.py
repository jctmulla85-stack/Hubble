import base64
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class LocalVault:
    def __init__(self, vault_path="sidecar/vault.enc", salt_path="sidecar/vault.salt"):
        self.vault_path = vault_path
        self.salt_path = salt_path

    def _get_or_create_salt(self) -> bytes:
        if os.path.exists(self.salt_path):
            with open(self.salt_path, "rb") as f:
                return f.read()
        else:
            salt = os.urandom(16)
            os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)
            with open(self.salt_path, "wb") as f:
                f.write(salt)
            os.chmod(self.salt_path, 0o600)
            return salt

    def _derive_key(self, passphrase: str) -> bytes:
        salt = self._get_or_create_salt()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    def store_credentials(self, passphrase: str, credentials: dict):
        key = self._derive_key(passphrase)
        f = Fernet(key)
        encrypted_data = f.encrypt(json.dumps(credentials).encode())
        
        with open(self.vault_path, "wb") as f_out:
            f_out.write(encrypted_data)
        os.chmod(self.vault_path, 0o600)
        print("[Vault] Credentials securely encrypted and stored locally.")

    def load_credentials(self, passphrase: str) -> dict:
        if not os.path.exists(self.vault_path):
            return {}
        
        key = self._derive_key(passphrase)
        f = Fernet(key)
        
        with open(self.vault_path, "rb") as f_in:
            encrypted_data = f_in.read()
            
        decrypted_data = f.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
