import os
from typing import Optional
from friday.domain.pal import SecureStorage

class KeychainStorage(SecureStorage):
    def __init__(self):
        self._use_keyring = False
        try:
            import keyring
            self._use_keyring = True
        except ImportError:
            pass

    async def get_secret(self, service: str, account: str) -> Optional[str]:
        if self._use_keyring:
            import keyring
            return keyring.get_password(service, account)
        return os.getenv(f"{service.upper()}_{account.upper()}")

    async def set_secret(self, service: str, account: str, secret: str) -> None:
        if self._use_keyring:
            import keyring
            keyring.set_password(service, account, secret)
        else:
            os.environ[f"{service.upper()}_{account.upper()}"] = secret
