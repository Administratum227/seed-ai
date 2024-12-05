from datetime import datetime
import pytest
from unittest.mock import patch
from seed_ai.capabilities.conversation import Conversation

def test_conversation_initialization(conversation, mock_config):
    """Verify conversation instance initializes with correct configuration."""
    assert conversation.config == mock_config
    assert len(conversation.history) == 0

def test_message_addition(conversation, mock_timestamp):
    """Test adding messages with timestamp validation."""
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = datetime.fromisoformat(mock_timestamp)
        
        # Add user message
        conversation.add_message('Hello', 'user')
        assert len(conversation.history) == 1
        message = conversation.history[0]
        assert message['content'] == 'Hello'
        assert message['role'] == 'user'
        assert message['timestamp'] == mock_timestamp

def test_history_limit(conversation):
    """Verify conversation history respects maximum length."""
    max_history = conversation.config['max_history']
    messages = [f'Message {i}' for i in range(max_history + 2)]
    
    for msg in messages:
        conversation.add_message(msg, 'user')
    
    assert len(conversation.history) == max_history
    assert conversation.history[-1]['content'] == messages[-1]

def test_response_generation(conversation):
    """Test response generation with history tracking."""
    input_text = 'Test input'
    response = conversation.generate_response(input_text)
    
    assert len(conversation.history) == 2  # Input and response
    assert conversation.history[0]['role'] == 'user'
    assert conversation.history[0]['content'] == input_text
    assert conversation.history[1]['role'] == 'assistant'
    assert conversation.history[1]['content'] == response

def test_context_retrieval(conversation):
    """Test context retrieval with different window sizes."""
    messages = ['First', 'Second', 'Third']
    for msg in messages:
        conversation.add_message(msg, 'user')
    
    # Full context
    full_context = conversation.get_context()
    assert len(full_context) == len(messages)
    
    # Limited context
    limited_context = conversation.get_context(2)
    assert len(limited_context) == 2
    assert limited_context[-1]['content'] == messages[-1]

def test_history_clearing(conversation):
    """Test history clearing functionality."""
    conversation.add_message('Test message', 'user')
    assert len(conversation.history) > 0
    
    conversation.clear_history()
    assert len(conversation.history) == 0

def test_invalid_role():
    """Test handling of invalid message roles."""
    conversation = Conversation()
    
    with pytest.raises(ValueError):
        conversation.add_message('Test', 'invalid_role')

def test_empty_message():
    """Test handling of empty messages."""
    conversation = Conversation()
    
    with pytest.raises(ValueError):
        conversation.add_message('', 'user')
    with pytest.raises(ValueError):
        conversation.add_message('   ', 'user')  # Whitespace only