"""
Memory Tool Lambda
Implements AgentCore tool interface for memory operations
"""

import json
import os
import boto3
from typing import Dict, Any, List
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
REFRAMES_TABLE = os.environ.get('REFRAMES_TABLE', 'CognitiveReframer-Reframes')


def lambda_handler(event, context):
    """
    Tool handler for memory operations
    Supports: recall, store, search
    """
    print(f"Memory tool invoked: {json.dumps(event)}")
    
    try:
        # Parse AgentCore tool invocation format
        action = event.get('action', event.get('tool_name', 'recall'))
        parameters = event.get('parameters', event.get('tool_input', {}))
        
        if action == 'recall':
            result = memory_recall(parameters)
        elif action == 'store':
            result = memory_store(parameters)
        elif action == 'search':
            result = memory_search(parameters)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown action: {action}'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'result': result
            })
        }
        
    except Exception as e:
        print(f"Error in memory tool: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def memory_recall(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recall relevant memories for a user
    params: {user_id: str, query: str, top_k: int}
    """
    user_id = params.get('user_id')
    query = params.get('query', '')
    top_k = params.get('top_k', 3)
    
    if not user_id:
        raise ValueError("user_id is required")
    
    table = dynamodb.Table(REFRAMES_TABLE)
    
    # Simple query by user_id (in production, add semantic search via embeddings)
    response = table.query(
        IndexName='UserIdIndex',
        KeyConditionExpression='user_id = :uid',
        ExpressionAttributeValues={':uid': user_id},
        ScanIndexForward=False,
        Limit=top_k
    )
    
    items = response.get('Items', [])
    
    # Format for agent context
    memories = []
    for item in items:
        memories.append({
            'id': item.get('reframe_id'),
            'input': item.get('source_input'),
            'models': item.get('models_used', []),
            'summary': item.get('summary'),
            'created_at': item.get('created_at')
        })
    
    return memories


def memory_store(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store a new reframe to memory
    params: {user_id: str, reframe_data: dict}
    """
    user_id = params.get('user_id')
    reframe_data = params.get('reframe_data', {})
    
    if not user_id or not reframe_data:
        raise ValueError("user_id and reframe_data are required")
    
    table = dynamodb.Table(REFRAMES_TABLE)
    
    reframe_id = f"{user_id}_{int(datetime.utcnow().timestamp() * 1000)}"
    
    item = {
        'reframe_id': reframe_id,
        'user_id': user_id,
        'source_input': reframe_data.get('input', ''),
        'models_used': reframe_data.get('model_selection', []),
        'reframes': reframe_data.get('reframes', []),
        'summary': reframe_data.get('summary', ''),
        'follow_up': reframe_data.get('follow_up', ''),
        'created_at': datetime.utcnow().isoformat(),
        'ttl': int(datetime.utcnow().timestamp()) + (90 * 24 * 60 * 60)
    }
    
    table.put_item(Item=item)
    
    return {
        'stored': True,
        'reframe_id': reframe_id
    }


def memory_search(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Semantic search across memories (placeholder for vector search)
    In production: integrate with AgentCore Memory or OpenSearch
    """
    user_id = params.get('user_id')
    query = params.get('query', '')
    
    # For now, fallback to recall
    # TODO: Implement vector similarity search with embeddings
    return memory_recall({'user_id': user_id, 'query': query, 'top_k': 5})

