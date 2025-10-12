"""
Unit tests for Cognitive Reframer Lambda functions
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend/lambda_reframe'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend/tools'))

import app
import memory_tool
import schedule_tool


class TestReframeHandler:
    """Test main reframe handler"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.valid_input = {
            'body': json.dumps({
                'action': 'reframe',
                'user_id': 'test_user',
                'input': 'I am worried about the presentation',
                'tone': 'gentle'
            })
        }
        
        self.mock_bedrock_response = {
            "input": "I am worried about the presentation",
            "model_selection": ["Premortem", "Scaling"],
            "reframes": [
                {
                    "model": "Premortem",
                    "reframe": "Imagine it went badly—what happened? Prepare for that now.",
                    "explanation": "Premortem helps identify risks proactively.",
                    "action_steps": [
                        "List 3 things that could go wrong",
                        "Rehearse for 10 minutes",
                        "Prepare a fallback"
                    ]
                },
                {
                    "model": "Scaling",
                    "reframe": "How important is this in 6 months?",
                    "explanation": "Scaling reduces emotional weight.",
                    "action_steps": [
                        "Write one learning goal",
                        "Remember a past success"
                    ]
                }
            ],
            "summary": "Prepare for scenarios and keep perspective.",
            "follow_up": "24 hours"
        }
    
    @patch('app.invoke_bedrock_reframe')
    @patch('app.store_reframe')
    @patch('app.recall_memories')
    def test_successful_reframe(self, mock_recall, mock_store, mock_bedrock):
        """Test successful reframe generation"""
        mock_recall.return_value = []
        mock_bedrock.return_value = json.dumps(self.mock_bedrock_response)
        mock_store.return_value = 'test_reframe_id'
        
        response = app.lambda_handler(self.valid_input, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'reframe_id' in body
        assert 'reframes' in body
        assert len(body['reframes']) == 2
        assert body['model_selection'] == ["Premortem", "Scaling"]
    
    def test_empty_input_validation(self):
        """Test that empty input is rejected"""
        event = {
            'body': json.dumps({
                'action': 'reframe',
                'user_id': 'test_user',
                'input': '',
                'tone': 'gentle'
            })
        }
        
        response = app.lambda_handler(event, None)
        assert response['statusCode'] == 500  # Error expected
    
    def test_input_length_validation(self):
        """Test that overly long input is rejected"""
        event = {
            'body': json.dumps({
                'action': 'reframe',
                'user_id': 'test_user',
                'input': 'x' * 600,  # Exceeds 500 char limit
                'tone': 'gentle'
            })
        }
        
        response = app.lambda_handler(event, None)
        assert response['statusCode'] == 500
    
    def test_self_harm_detection(self):
        """Test that self-harm keywords trigger safety response"""
        assert app.is_self_harm_risk("I want to kill myself") == True
        assert app.is_self_harm_risk("I am stressed") == False
        assert app.is_self_harm_risk("I want to hurt myself") == True
        assert app.is_self_harm_risk("end my life") == True
    
    @patch('app.invoke_bedrock_reframe')
    @patch('app.store_reframe')
    @patch('app.recall_memories')
    def test_self_harm_input_returns_safety_message(self, mock_recall, mock_store, mock_bedrock):
        """Test safety message returned for self-harm input"""
        event = {
            'body': json.dumps({
                'action': 'reframe',
                'user_id': 'test_user',
                'input': 'I want to kill myself',
                'tone': 'gentle'
            })
        }
        
        response = app.lambda_handler(event, None)
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'safety_response' in body
        assert body['safety_response'] == True
        assert 'resources' in body
    
    def test_json_parsing_extracts_valid_json(self):
        """Test JSON extraction from text with surrounding content"""
        text_with_json = '''
        Here is some text before
        {
            "model_selection": ["Test"],
            "reframes": [],
            "summary": "Test",
            "follow_up": "24 hours"
        }
        And some text after
        '''
        
        result = app.parse_reframe_response(text_with_json)
        assert 'model_selection' in result
        assert result['model_selection'] == ["Test"]
    
    def test_json_parsing_validates_required_fields(self):
        """Test that missing required fields raise error"""
        invalid_json = '{"model_selection": ["Test"]}'  # Missing other required fields
        
        with pytest.raises(ValueError, match="Missing required field"):
            app.parse_reframe_response(invalid_json)


class TestMemoryTool:
    """Test memory tool functions"""
    
    @patch('memory_tool.dynamodb')
    def test_memory_recall(self, mock_dynamodb):
        """Test memory recall functionality"""
        mock_table = Mock()
        mock_table.query.return_value = {
            'Items': [
                {
                    'reframe_id': 'test_id',
                    'source_input': 'test input',
                    'models_used': ['Test'],
                    'summary': 'test summary',
                    'created_at': '2025-01-01T00:00:00Z'
                }
            ]
        }
        mock_dynamodb.Table.return_value = mock_table
        
        result = memory_tool.memory_recall({
            'user_id': 'test_user',
            'query': 'test',
            'top_k': 3
        })
        
        assert len(result) == 1
        assert result[0]['id'] == 'test_id'
        assert result[0]['input'] == 'test input'
    
    @patch('memory_tool.dynamodb')
    def test_memory_store(self, mock_dynamodb):
        """Test memory storage functionality"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        result = memory_tool.memory_store({
            'user_id': 'test_user',
            'reframe_data': {
                'input': 'test input',
                'model_selection': ['Test'],
                'reframes': [],
                'summary': 'test',
                'follow_up': '24 hours'
            }
        })
        
        assert result['stored'] == True
        assert 'reframe_id' in result
        mock_table.put_item.assert_called_once()


class TestScheduleTool:
    """Test schedule tool functions"""
    
    @patch('schedule_tool.dynamodb')
    def test_schedule_followup(self, mock_dynamodb):
        """Test follow-up scheduling"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        result = schedule_tool.schedule_followup({
            'user_id': 'test_user',
            'reframe_id': 'test_reframe',
            'hours_from_now': 48
        })
        
        assert result['scheduled'] == True
        assert 'reminder_id' in result
        assert result['hours_from_now'] == 48
        mock_table.put_item.assert_called_once()
    
    def test_parse_follow_up_window(self):
        """Test parsing of follow-up time strings"""
        assert schedule_tool.parse_follow_up_window("24 hours") == 24
        assert schedule_tool.parse_follow_up_window("2 days") == 48
        assert schedule_tool.parse_follow_up_window("invalid") == 48  # default


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_create_response_has_cors_headers(self):
        """Test that API responses include CORS headers"""
        response = app.create_response(200, {'test': 'data'})
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        assert 'Content-Type' in response['headers']
    
    def test_build_system_prompt_includes_models(self):
        """Test that system prompt includes all mental models"""
        prompt = app.build_system_prompt('gentle', [])
        
        models = ['Inversion', 'First Principles', 'Dichotomy of Control', 
                  '5 Whys', 'Outcome Forecasting', 'Cost-Benefit', 
                  'Scaling', 'Premortem']
        
        for model in models:
            assert model in prompt
    
    def test_build_system_prompt_includes_memory_context(self):
        """Test that system prompt includes memory context"""
        memory_context = [
            {
                'source_input': 'previous thought',
                'models_used': ['Test Model']
            }
        ]
        
        prompt = app.build_system_prompt('gentle', memory_context)
        assert 'Previous reframes' in prompt
        assert 'previous thought' in prompt


class TestIntegration:
    """Integration tests"""
    
    @patch('app.bedrock_runtime')
    @patch('app.dynamodb')
    def test_end_to_end_reframe_flow(self, mock_dynamodb, mock_bedrock):
        """Test complete reframe flow from input to storage"""
        # Mock DynamoDB
        mock_table = Mock()
        mock_table.query.return_value = {'Items': []}
        mock_table.put_item.return_value = {}
        mock_dynamodb.Table.return_value = mock_table
        
        # Mock Bedrock response
        mock_bedrock.invoke_model.return_value = {
            'body': Mock(read=lambda: json.dumps({
                'completion': json.dumps({
                    "input": "test input",
                    "model_selection": ["Test1", "Test2"],
                    "reframes": [
                        {
                            "model": "Test1",
                            "reframe": "Test reframe 1",
                            "explanation": "Test explanation 1",
                            "action_steps": ["Step 1", "Step 2"]
                        },
                        {
                            "model": "Test2",
                            "reframe": "Test reframe 2",
                            "explanation": "Test explanation 2",
                            "action_steps": ["Step A", "Step B"]
                        }
                    ],
                    "summary": "Test summary",
                    "follow_up": "48 hours"
                }).encode()
            }).encode())
        }
        
        event = {
            'body': json.dumps({
                'action': 'reframe',
                'user_id': 'test_user',
                'input': 'test input',
                'tone': 'gentle'
            })
        }
        
        response = app.lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'reframes' in body
        assert len(body['reframes']) == 2


# Test fixtures
@pytest.fixture
def mock_bedrock_response():
    """Fixture providing mock Bedrock response"""
    return json.dumps({
        "input": "test input",
        "model_selection": ["Model1", "Model2"],
        "reframes": [
            {
                "model": "Model1",
                "reframe": "Test reframe",
                "explanation": "Test explanation",
                "action_steps": ["Step 1", "Step 2"]
            },
            {
                "model": "Model2",
                "reframe": "Test reframe 2",
                "explanation": "Test explanation 2",
                "action_steps": ["Step A", "Step B"]
            }
        ],
        "summary": "Test summary",
        "follow_up": "24 hours"
    })


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=app', '--cov=memory_tool', '--cov=schedule_tool'])

