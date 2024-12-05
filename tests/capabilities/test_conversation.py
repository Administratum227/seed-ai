import pytest
from datetime import datetime
from seed_ai.capabilities.conversation import Conversation

@pytest.fixture
def conversation():
    """Create a basic conversation instance with default settings."""
    return Conversation()

@pytest.fixture
def custom_conversation():
    """Create a conversation instance with custom configuration."""
    return Conversation({
        'max_history': 5,
        'max_response_length': 500,
        'keep_timestamps': True
    })

def test_conversation_initialization(conversation):
    """Verify conversation instance initializes with correct defaults."""
    assert conversation.config['max_history'] == 10
    assert conversation.config['max_response_length'] == 1000
    assert conversation.config['keep_timestamps'] is True
    assert len(conversation.history) == 0

def test_message_addition(conversation):
    """Test adding messages to conversation history."""
    # Add user message
    conversation.add_message('Hello', 'user')
    assert len(conversation.history) == 1
    assert conversation.history[0]['content'] == 'Hello'
    assert conversation.history[0]['role'] == 'user'
    assert 'timestamp' in conversation.history[0]
    
    # Add assistant message
    conversation.add_message('Hi there!', 'assistant')
    assert len(conversation.history) == 2
    assert conversation.history[1]['role'] == 'assistant'

def test_history_limit(custom_conversation):
    """Verify conversation history respects maximum length."""
    # Add more messages than the limit
    for i in range(7):
        custom_conversation.add_message(f'Message {i}', 'user')
    
    # Check that only the most recent messages are kept
    assert len(custom_conversation.history) == 5
    assert custom_conversation.history[-1]['content'] == 'Message 6'

def test_response_generation(conversation):
    """Test basic response generation functionality."""
    response = conversation.generate_response('Test input')
    
    # Verify response was generated and added to history
    assert response.startswith('Processed response to:')
    assert len(conversation.history) == 2  # Input and response
    assert conversation.history[0]['role'] == 'user'
    assert conversation.history[1]['role'] == 'assistant'

def test_context_retrieval(conversation):
    """Test getting conversation context."""
    # Add some messages
    messages = ['First', 'Second', 'Third']
    for msg in messages:
        conversation.add_message(msg, 'user')
    
    # Test full context retrieval
    context = conversation.get_context()
    assert len(context) == 3
    
    # Test limited context retrieval
    recent = conversation.get_context(2)
    assert len(recent) == 2
    assert recent[-1]['content'] == 'Third'

def test_history_clearing(conversation):
    """Test clearing conversation history."""
    conversation.add_message('Test message', 'user')
    assert len(conversation.history) > 0
    
    conversation.clear_history()
    assert len(conversation.history) == 0