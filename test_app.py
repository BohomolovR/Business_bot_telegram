import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app import BusinessBot
from database import DatabaseManager
from encryption import MessageEncryptor
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_db():
    return MagicMock(spec=DatabaseManager)

@pytest.fixture
def mock_encryptor():
    return MagicMock(spec=MessageEncryptor)

@pytest.fixture
def bot(monkeypatch, mock_db, mock_encryptor):
    with patch("app.TelegramClient") as MockClient:
        instance = BusinessBot("api_id", "api_hash", "api_token")
        instance.db = mock_db
        instance.encryptor = mock_encryptor
        return instance

def test_generate_key(mock_encryptor):
    key = MessageEncryptor().generate_key(12345)
    assert isinstance(key, bytes)
    assert len(key) == 16

@pytest.mark.asyncio
async def test_encrypt_decrypt_message():
    encryptor = MessageEncryptor()
    owner_id = 12345
    message = "test message"
    encrypted = encryptor.encrypt_message(message, owner_id)
    decrypted = encryptor.decrypt_message(encrypted, owner_id)
    assert decrypted == message

def test_db_methods(mock_db):
    mock_db.save_message.return_value = None
    mock_db.get_message_by_id.return_value = (1, "user", "text", "msg")
    assert mock_db.get_message_by_id(1)[1] == "user"
    mock_db.save_owner_id.assert_not_called()
    mock_db.save_owner_id(1, 2)
    mock_db.save_owner_id.assert_called_once_with(1, 2)