"""Network security implementation for SEED agents.

Provides encryption, authentication, and secure message passing."""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from typing import Dict, Optional, Tuple
import base64
import json
import os

class NetworkSecurity:
    """Handles security aspects of agent communication.
    
    Features:
    - Message encryption/decryption
    - Agent authentication
    - Access token management
    - Secure key exchange
    """
    
    def __init__(self):
        self._encryption_key = Fernet.generate_key()
        self._fernet = Fernet(self._encryption_key)
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self._public_key = self._private_key.public_key()
        self._agent_keys: Dict[str, bytes] = {}
    
    def encrypt_message(self, data: Dict) -> bytes:
        """Encrypt message data.
        
        Args:
            data: Message data to encrypt
            
        Returns:
            Encrypted message bytes
        """
        message_bytes = json.dumps(data).encode()
        return self._fernet.encrypt(message_bytes)
    
    def decrypt_message(self, encrypted_data: bytes) -> Dict:
        """Decrypt message data.
        
        Args:
            encrypted_data: Encrypted message bytes
            
        Returns:
            Decrypted message data
        """
        decrypted_bytes = self._fernet.decrypt(encrypted_data)
        return json.loads(decrypted_bytes.decode())
    
    def create_agent_token(self, agent_id: str) -> str:
        """Create authentication token for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Authentication token
        """
        token = os.urandom(32)
        self._agent_keys[agent_id] = token
        return base64.b64encode(token).decode()
    
    def verify_agent_token(self, agent_id: str, token: str) -> bool:
        """Verify an agent's authentication token.
        
        Args:
            agent_id: ID of the agent
            token: Token to verify
            
        Returns:
            True if token is valid
        """
        stored_token = self._agent_keys.get(agent_id)
        if not stored_token:
            return False
            
        try:
            provided_token = base64.b64decode(token.encode())
            return stored_token == provided_token
        except:
            return False