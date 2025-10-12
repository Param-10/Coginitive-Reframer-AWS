"""
Schedule Tool Lambda
Implements follow-up reminder scheduling
"""

import json
import os
import boto3
from typing import Dict, Any
from datetime import datetime, timedelta

sns = boto3.client('sns', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
eventbridge = boto3.client('events', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

REMINDERS_TABLE = os.environ.get('REMINDERS_TABLE', 'CognitiveReframer-Reminders')


def lambda_handler(event, context):
    """
    Tool handler for scheduling follow-ups
    """
    print(f"Schedule tool invoked: {json.dumps(event)}")
    
    try:
        parameters = event.get('parameters', event.get('tool_input', {}))
        
        result = schedule_followup(parameters)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'result': result
            })
        }
        
    except Exception as e:
        print(f"Error in schedule tool: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def schedule_followup(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Schedule a follow-up reminder
    params: {
        user_id: str,
        reframe_id: str,
        hours_from_now: int (default from follow_up field, e.g., "48 hours"),
        method: str ('email' or 'calendar')
    }
    """
    user_id = params.get('user_id')
    reframe_id = params.get('reframe_id')
    hours_from_now = params.get('hours_from_now', 48)
    method = params.get('method', 'notification')
    
    if not user_id or not reframe_id:
        raise ValueError("user_id and reframe_id are required")
    
    # Calculate reminder time
    reminder_time = datetime.utcnow() + timedelta(hours=hours_from_now)
    
    # Store reminder in DynamoDB
    table = dynamodb.Table(REMINDERS_TABLE)
    reminder_id = f"{user_id}_{reframe_id}_{int(datetime.utcnow().timestamp())}"
    
    item = {
        'reminder_id': reminder_id,
        'user_id': user_id,
        'reframe_id': reframe_id,
        'scheduled_time': reminder_time.isoformat(),
        'method': method,
        'status': 'scheduled',
        'created_at': datetime.utcnow().isoformat()
    }
    
    table.put_item(Item=item)
    
    # For demo: return scheduled confirmation
    # In production: integrate with EventBridge scheduled events or SNS
    return {
        'scheduled': True,
        'reminder_id': reminder_id,
        'scheduled_time': reminder_time.isoformat(),
        'hours_from_now': hours_from_now,
        'message': f"Follow-up reminder scheduled for {reminder_time.strftime('%Y-%m-%d %H:%M UTC')}"
    }


def parse_follow_up_window(follow_up_str: str) -> int:
    """
    Parse follow_up string like "48 hours" into hours integer
    """
    try:
        parts = follow_up_str.lower().split()
        if 'hour' in follow_up_str.lower():
            return int(parts[0])
        elif 'day' in follow_up_str.lower():
            return int(parts[0]) * 24
        else:
            return 48  # default
    except:
        return 48

