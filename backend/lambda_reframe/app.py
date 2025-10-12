"""
Cognitive Reframer - Main Lambda Handler
Orchestrates the agent flow: memory recall → model selection → reframing → storage
"""

import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any, List
from botocore.exceptions import ClientError

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Environment configuration
MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-v2')
REFRAMES_TABLE = os.environ.get('REFRAMES_TABLE', 'CognitiveReframer-Reframes')
USERS_TABLE = os.environ.get('USERS_TABLE', 'CognitiveReframer-Users')

def lambda_handler(event, context):
    """
    Main Lambda handler for API Gateway requests
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Parse request
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        action = body.get('action', 'reframe')
        user_id = body.get('user_id', 'demo_user')
        
        # Route to appropriate handler
        if action == 'reframe':
            response = handle_reframe(user_id, body)
        elif action == 'history':
            response = handle_history(user_id)
        elif action == 'get_user':
            response = handle_get_user(user_id)
        else:
            return create_response(400, {'error': f'Unknown action: {action}'})
        
        return create_response(200, response)
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_response(500, {'error': str(e)})


def handle_reframe(user_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main reframing flow:
    1. Validate and sanitize input
    2. Check safety (self-harm detection)
    3. Recall relevant memories
    4. Invoke Bedrock with prompt
    5. Parse and validate JSON response
    6. Store reframe to memory
    7. Return formatted response
    """
    user_input = body.get('input', '').strip()
    tone = body.get('tone', 'gentle')
    
    # Validation
    if not user_input:
        raise ValueError("Input cannot be empty")
    
    if len(user_input) > 500:
        raise ValueError("Input too long (max 500 characters)")
    
    # Safety check
    if is_self_harm_risk(user_input):
        return {
            'safety_response': True,
            'message': 'Your message suggests you may be in distress. This tool is not a substitute for professional help.',
            'resources': [
                'National Suicide Prevention Lifeline: 988 (US)',
                'Crisis Text Line: Text HOME to 741741 (US)',
                'International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/'
            ]
        }
    
    # Step 1: Recall relevant memories (semantic search)
    memory_context = recall_memories(user_id, user_input)
    
    # Step 2: Build prompt with context
    system_prompt = build_system_prompt(tone, memory_context)
    
    # Step 3: Invoke Bedrock
    reframe_response = invoke_bedrock_reframe(system_prompt, user_input)
    
    # Step 4: Parse JSON response
    try:
        reframe_data = parse_reframe_response(reframe_response)
        reframe_data['input'] = user_input  # Ensure input is preserved
    except json.JSONDecodeError as e:
        print(f"Failed to parse Bedrock response as JSON: {reframe_response}")
        raise ValueError(f"Model returned invalid JSON: {str(e)}")
    
    # Step 5: Store reframe to memory and DynamoDB
    reframe_id = store_reframe(user_id, user_input, reframe_data)
    
    # Step 6: Return response
    return {
        'reframe_id': reframe_id,
        'user_id': user_id,
        'created_at': datetime.utcnow().isoformat(),
        **reframe_data
    }


def is_self_harm_risk(text: str) -> bool:
    """
    Basic safety check for self-harm indicators
    In production, use a more sophisticated model or AWS Comprehend
    """
    risk_keywords = [
        'kill myself', 'suicide', 'end my life', 'want to die',
        'better off dead', 'hurt myself', 'self harm'
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in risk_keywords)


def recall_memories(user_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve relevant past reframes from memory store
    For now, uses DynamoDB; will integrate AgentCore Memory in future
    """
    try:
        table = dynamodb.Table(REFRAMES_TABLE)
        response = table.query(
            IndexName='UserIdIndex',  # GSI on user_id
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,  # Most recent first
            Limit=top_k
        )
        return response.get('Items', [])
    except ClientError as e:
        print(f"Error recalling memories: {e}")
        return []


def build_system_prompt(tone: str, memory_context: List[Dict[str, Any]]) -> str:
    """
    Construct the system prompt with mental models and memory context
    """
    tone_guidance = {
        'gentle': 'Use warm, supportive language. Be encouraging and emphasize small wins.',
        'direct': 'Be concise and practical. Focus on actionable steps without extra encouragement.'
    }.get(tone, 'Be balanced and practical.')
    
    memory_section = ""
    if memory_context:
        memory_section = "\n\nPrevious reframes for this user:\n"
        for mem in memory_context[:2]:  # Include only 2 most recent
            memory_section += f"- Input: {mem.get('source_input', 'N/A')}\n"
            memory_section += f"  Models used: {mem.get('models_used', 'N/A')}\n"
    
    prompt = f"""You are "Cognitive Reframer" — a precise cognitive toolkit that helps users reframe stuck or stressful thoughts.

{tone_guidance}

MENTAL MODELS AVAILABLE:
1. Inversion - Think backward: what would guarantee failure? Avoid those things.
2. First Principles - Break down to fundamental truths; rebuild reasoning from scratch.
3. Dichotomy of Control - Separate what you control from what you don't; focus on the former.
4. 5 Whys - Ask "why" repeatedly to uncover root causes.
5. Outcome Forecasting - Project realistic best/worst/likely scenarios.
6. Cost-Benefit - Explicitly compare costs and benefits of different paths.
7. Scaling - Break big problems into smaller chunks or expand perspective.
8. Premortem - Imagine the project failed; work backward to identify risks now.
{memory_section}

TASK:
1. Identify the core belief or stuckness in the user's input
2. Select TWO distinct mental models that best address this belief
3. For each model, provide:
   - model_name (from list above)
   - reframe (one concise sentence reframing the thought)
   - explanation (1-2 sentences explaining why this reframe helps)
   - action_steps (array of 2-3 specific micro-tasks achievable in 10-30 minutes each)
4. Generate a positive summary (1 sentence)
5. Suggest a follow_up time window (e.g., "24 hours", "48 hours")

OUTPUT FORMAT (must be valid JSON only, no other text):
{{
  "input": "<user input echoed>",
  "model_selection": ["Model1", "Model2"],
  "reframes": [
    {{
      "model": "Model1",
      "reframe": "One-line reframe",
      "explanation": "Why this helps (1-2 sentences)",
      "action_steps": ["Step 1", "Step 2", "Step 3"]
    }},
    {{
      "model": "Model2",
      "reframe": "One-line reframe",
      "explanation": "Why this helps (1-2 sentences)",
      "action_steps": ["Step 1", "Step 2"]
    }}
  ],
  "summary": "Positive one-sentence summary",
  "follow_up": "48 hours"
}}

EXAMPLES:

Input: "I'm sure the launch will fail and it'll be a disaster."
Output:
{{
  "input": "I'm sure the launch will fail and it'll be a disaster.",
  "model_selection": ["Inversion", "Dichotomy of Control"],
  "reframes": [
    {{
      "model": "Inversion",
      "reframe": "Instead of imagining failure, list the fastest ways to fail and stop doing those things.",
      "explanation": "Inversion helps identify avoidable errors by thinking backward from worst outcomes.",
      "action_steps": [
        "List top 3 actions that would guarantee launch failure",
        "Assign a mitigation plan for each failure mode",
        "Schedule 30-minute check-in to review mitigations"
      ]
    }},
    {{
      "model": "Dichotomy of Control",
      "reframe": "Separate what you control (your task list) from what you don't (external dependencies). Focus on the controllables first.",
      "explanation": "This reduces anxiety by directing energy toward elements you can directly change.",
      "action_steps": [
        "Block 2 hours to complete 1 high-impact task you control",
        "Email stakeholders for clarity on external blockers"
      ]
    }}
  ],
  "summary": "Focus on what you can directly change and remove known failure paths.",
  "follow_up": "48 hours"
}}

Input: "I'll embarrass myself in the meeting."
Output:
{{
  "input": "I'll embarrass myself in the meeting.",
  "model_selection": ["Premortem", "Scaling"],
  "reframes": [
    {{
      "model": "Premortem",
      "reframe": "Imagine the meeting went badly—what specifically happened? Prepare for those scenarios now.",
      "explanation": "Premortem identifies concrete risks ahead of time so you can address them proactively.",
      "action_steps": [
        "List 3 things that could go wrong in the meeting",
        "Rehearse responses to each scenario for 10 minutes",
        "Prepare a fallback line if you lose your place"
      ]
    }},
    {{
      "model": "Scaling",
      "reframe": "Zoom out: how important will this meeting feel in 6 months? Focus on learning, not perfection.",
      "explanation": "Scaling helps reduce emotional weight by expanding time perspective.",
      "action_steps": [
        "Write down one learning goal for the meeting (not perfection)",
        "Remind yourself of a past meeting that felt scary but turned out fine"
      ]
    }}
  ],
  "summary": "Prepare for realistic scenarios and remember this is one step in a longer journey.",
  "follow_up": "24 hours"
}}

Now process the user's input below. Output ONLY valid JSON, nothing else.
"""
    return prompt


def invoke_bedrock_reframe(system_prompt: str, user_input: str) -> str:
    """
    Invoke Amazon Bedrock to generate reframes
    Returns raw model output (should be JSON string)
    """
    # Construct the full prompt
    full_prompt = f"{system_prompt}\n\nUser input: {user_input}\n\nJSON output:"
    
    # Bedrock API call structure varies by model
    # For Claude v2 (Anthropic), use this format:
    request_body = {
        "prompt": f"\n\nHuman: {full_prompt}\n\nAssistant:",
        "max_tokens_to_sample": 1024,
        "temperature": 0.3,
        "top_p": 0.9,
        "stop_sequences": ["\n\nHuman:"]
    }
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        # Extract text based on model type
        if 'anthropic' in MODEL_ID.lower():
            output_text = response_body.get('completion', '')
        elif 'amazon.titan' in MODEL_ID.lower():
            output_text = response_body.get('results', [{}])[0].get('outputText', '')
        else:
            # Fallback: try common response keys
            output_text = response_body.get('completion') or response_body.get('outputText') or str(response_body)
        
        print(f"Bedrock raw response: {output_text}")
        return output_text.strip()
        
    except ClientError as e:
        print(f"Bedrock invocation error: {e}")
        raise Exception(f"Failed to invoke Bedrock: {str(e)}")


def parse_reframe_response(response_text: str) -> Dict[str, Any]:
    """
    Parse and validate the JSON response from Bedrock
    """
    # Try to extract JSON if model added extra text
    response_text = response_text.strip()
    
    # Find JSON boundaries
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')
    
    if start_idx == -1 or end_idx == -1:
        raise ValueError("No JSON object found in response")
    
    json_str = response_text[start_idx:end_idx + 1]
    data = json.loads(json_str)
    
    # Validate required fields
    required_fields = ['model_selection', 'reframes', 'summary', 'follow_up']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field in response: {field}")
    
    # Validate reframes structure
    if not isinstance(data['reframes'], list) or len(data['reframes']) < 2:
        raise ValueError("Response must contain at least 2 reframes")
    
    for reframe in data['reframes']:
        required_reframe_fields = ['model', 'reframe', 'explanation', 'action_steps']
        for field in required_reframe_fields:
            if field not in reframe:
                raise ValueError(f"Reframe missing required field: {field}")
    
    return data


def store_reframe(user_id: str, user_input: str, reframe_data: Dict[str, Any]) -> str:
    """
    Store reframe to DynamoDB (and eventually AgentCore Memory)
    """
    try:
        table = dynamodb.Table(REFRAMES_TABLE)
        
        reframe_id = f"{user_id}_{int(datetime.utcnow().timestamp() * 1000)}"
        
        item = {
            'reframe_id': reframe_id,
            'user_id': user_id,
            'source_input': user_input,
            'models_used': reframe_data.get('model_selection', []),
            'reframes': reframe_data.get('reframes', []),
            'summary': reframe_data.get('summary', ''),
            'follow_up': reframe_data.get('follow_up', ''),
            'created_at': datetime.utcnow().isoformat(),
            'ttl': int(datetime.utcnow().timestamp()) + (90 * 24 * 60 * 60)  # 90 days
        }
        
        table.put_item(Item=item)
        print(f"Stored reframe {reframe_id} for user {user_id}")
        
        return reframe_id
        
    except ClientError as e:
        print(f"Error storing reframe: {e}")
        raise


def handle_history(user_id: str) -> Dict[str, Any]:
    """
    Retrieve user's reframe history
    """
    try:
        table = dynamodb.Table(REFRAMES_TABLE)
        response = table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,
            Limit=20
        )
        
        return {
            'user_id': user_id,
            'history': response.get('Items', [])
        }
    except ClientError as e:
        print(f"Error retrieving history: {e}")
        return {'user_id': user_id, 'history': []}


def handle_get_user(user_id: str) -> Dict[str, Any]:
    """
    Get or create user profile
    """
    try:
        table = dynamodb.Table(USERS_TABLE)
        response = table.get_item(Key={'user_id': user_id})
        
        if 'Item' in response:
            return response['Item']
        else:
            # Create new user
            user = {
                'user_id': user_id,
                'display_name': f"User {user_id[-6:]}",
                'created_at': datetime.utcnow().isoformat(),
                'preferences': {
                    'default_tone': 'gentle',
                    'timezone': 'UTC'
                }
            }
            table.put_item(Item=user)
            return user
            
    except ClientError as e:
        print(f"Error getting user: {e}")
        return {
            'user_id': user_id,
            'display_name': 'Guest',
            'preferences': {'default_tone': 'gentle'}
        }


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create API Gateway response with CORS headers
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }

