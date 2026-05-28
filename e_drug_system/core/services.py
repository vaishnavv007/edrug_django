import os
import json
import requests
from django.conf import settings
from datetime import datetime, timedelta


def analyze_assessment_with_groq(responses):
    """
    Send assessment responses to Groq API for analysis.
    
    Args:
        responses (dict): User responses to assessment questions
        
    Returns:
        dict: Parsed AI response with severity, readiness, mental_state, and recommendations
    """
    api_key = settings.GROQ_API_KEY
    
    if not api_key:
        return {
            'error': 'GROQ_API_KEY not configured',
            'severity_level': 'Moderate',
            'readiness_level': 'Thinking',
            'mental_state_summary': 'Unable to analyze - API key not configured',
            'recommendations': 'Please contact administrator to configure AI analysis.'
        }
    
    prompt = f"""You are an addiction assessment AI.

Analyze the following user responses.

Return:
1. Addiction Severity Level (Low, Moderate, High, Critical)
2. Readiness to Change (Not Ready, Thinking About Change, Preparing, Actively Recovering)
3. Mental & Physical State Summary
4. Personalized Recommendations (exercise, meditation, habit changes)

User Responses:
{json.dumps(responses, indent=2)}

Please format your response as JSON with the following structure:
{{
    "severity_level": "Low/Moderate/High/Critical",
    "readiness_level": "Not Ready/Thinking About Change/Preparing/Actively Recovering",
    "mental_state_summary": "summary text",
    "recommendations": "recommendations text"
}}"""
    
    try:
        api_url = "https://api.groq.com/openai/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "You are a professional addiction assessment AI. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        response = requests.post(f"{api_url}/chat/completions", headers=headers, json=data, timeout=30)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Body: {response.text}")
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"Assessment AI Content: {content}")
        
        # Try to parse JSON, handle cases where AI returns non-JSON
        try:
            ai_response = json.loads(content)
        except json.JSONDecodeError:
            # If AI didn't return JSON, extract values using regex
            import re
            severity_match = re.search(r'severity_level["\s:]+["\']?([\w\s]+)["\']?', content, re.IGNORECASE)
            readiness_match = re.search(r'readiness_level["\s:]+["\']?([\w\s]+)["\']?', content, re.IGNORECASE)
            mental_match = re.search(r'mental_state_summary["\s:]+["\']?([^"\']+)["\']?', content, re.IGNORECASE)
            rec_match = re.search(r'recommendations["\s:]+["\']?([^"\']+)["\']?', content, re.IGNORECASE)
            
            ai_response = {
                'severity_level': severity_match.group(1) if severity_match else 'Moderate',
                'readiness_level': readiness_match.group(1) if readiness_match else 'Thinking About Change',
                'mental_state_summary': mental_match.group(1) if mental_match else content[:500],
                'recommendations': rec_match.group(1) if rec_match else 'Continue tracking your progress.'
            }
        
        return {
            'severity_level': ai_response.get('severity_level', 'Moderate'),
            'readiness_level': ai_response.get('readiness_level', 'Thinking About Change'),
            'mental_state_summary': ai_response.get('mental_state_summary', 'No summary provided'),
            'recommendations': ai_response.get('recommendations', 'No recommendations provided'),
            'full_report': content
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'error': f'API request failed: {str(e)}',
            'severity_level': 'Moderate',
            'readiness_level': 'Thinking',
            'mental_state_summary': 'AI analysis temporarily unavailable. Your responses have been recorded.',
            'recommendations': 'Please try again later or contact support if the issue persists.'
        }
    except json.JSONDecodeError as e:
        return {
            'error': f'Failed to parse AI response: {str(e)}',
            'severity_level': 'Moderate',
            'readiness_level': 'Thinking',
            'mental_state_summary': 'AI analysis temporarily unavailable. Your responses have been recorded.',
            'recommendations': 'Please try again later or contact support if the issue persists.'
        }
    except Exception as e:
        return {
            'error': f'Unexpected error: {str(e)}',
            'severity_level': 'Moderate',
            'readiness_level': 'Thinking',
            'mental_state_summary': 'AI analysis temporarily unavailable. Your responses have been recorded.',
            'recommendations': 'Please try again later or contact support if the issue persists.'
        }


def analyze_rehabilitation_plan(plan_data):
    """
    Analyze rehabilitation plan and calculate risk level (0-100%).
    
    Args:
        plan_data (dict): Rehabilitation plan data including goals, activities, risk situations
        
    Returns:
        dict: Analysis result with risk level and AI insights
    """
    api_key = settings.GROQ_API_KEY
    
    if not api_key:
        # Fallback to simple risk calculation
        risk_level = calculate_simple_risk(plan_data)
        return {
            'risk_level': risk_level,
            'ai_analysis': 'AI analysis not available. Using basic risk calculation.',
            'recommendations': 'Consider increasing daily recovery activities and seeking support.'
        }
    
    prompt = f"""You are a rehabilitation assessment AI.

Analyze the following rehabilitation plan and calculate a risk level (0-100%).

Plan Data:
Primary Goal: {plan_data.get('primary_goal')}
Short-term Goal: {plan_data.get('short_term_goal')}
Long-term Goal: {plan_data.get('long_term_goal')}
Hours per Day: {plan_data.get('hours_per_day')}
Activities: {plan_data.get('activities')}
Activity Frequency: {plan_data.get('activity_frequency')}
Risk Situations: {plan_data.get('risk_situations')}

Return:
1. Risk Level (0-100%)
2. AI Analysis (comprehensive assessment of the plan)
3. Recommendations (specific suggestions to improve the plan)

Please format your response as JSON with the following structure:
{{
    "risk_level": 0-100,
    "ai_analysis": "detailed analysis text",
    "recommendations": "specific recommendations text"
}}"""
    
    try:
        api_url = "https://api.groq.com/openai/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "You are a professional rehabilitation assessment AI. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        response = requests.post(f"{api_url}/chat/completions", headers=headers, json=data, timeout=30)
        print(f"Plan Analysis API Response Status: {response.status_code}")
        print(f"Plan Analysis API Response Body: {response.text}")
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"Plan Analysis AI Content: {content}")
        
        # Try to parse JSON, handle cases where AI returns non-JSON
        try:
            ai_response = json.loads(content)
        except json.JSONDecodeError:
            # If AI didn't return JSON, extract values using regex
            import re
            risk_match = re.search(r'risk_level["\s:]+(\d+)', content, re.IGNORECASE)
            analysis_match = re.search(r'ai_analysis["\s:]+["\']([^"\']+)["\']', content, re.IGNORECASE)
            rec_match = re.search(r'recommendations["\s:]+["\']([^"\']+)["\']', content, re.IGNORECASE)
            
            ai_response = {
                'risk_level': int(risk_match.group(1)) if risk_match else 50,
                'ai_analysis': analysis_match.group(1) if analysis_match else content[:500],
                'recommendations': rec_match.group(1) if rec_match else 'Continue with your recovery plan.'
            }
        
        return {
            'risk_level': ai_response.get('risk_level', 50),
            'ai_analysis': ai_response.get('ai_analysis', 'No analysis provided'),
            'recommendations': ai_response.get('recommendations', 'No recommendations provided')
        }
        
    except Exception as e:
        # Fallback to simple calculation
        risk_level = calculate_simple_risk(plan_data)
        return {
            'risk_level': risk_level,
            'ai_analysis': f'AI analysis unavailable: {str(e)}. Using basic calculation.',
            'recommendations': 'Consider increasing daily recovery activities and seeking support.'
        }


def analyze_daily_progress(progress_data, plan_data=None):
    """
    Analyze daily progress and detect self-harm risks.
    
    Args:
        progress_data (dict): Daily progress data including mood, cravings, relapse status
        plan_data (dict, optional): Rehabilitation plan data for context
        
    Returns:
        dict: Analysis result including self-harm detection and recommendations
    """
    api_key = settings.GROQ_API_KEY
    
    # Check for self-harm indicators first
    self_harm_indicators = detect_self_harm_indicators(progress_data)
    
    if self_harm_indicators['detected']:
        return {
            'self_harm_detected': True,
            'self_harm_risk': self_harm_indicators['risk'],
            'ai_analysis': 'Self-harm indicators detected. Immediate attention required.',
            'recommendations': 'Please contact emergency services or your support network immediately.',
            'risk_level': 'high'
        }
    
    if not api_key:
        return {
            'self_harm_detected': False,
            'ai_analysis': 'AI analysis not available.',
            'recommendations': 'Continue tracking your progress daily.',
            'risk_level': progress_data.get('risk_level', 'low')
        }
    
    prompt = f"""You are a rehabilitation progress monitoring AI.

Analyze the following daily progress and provide insights.

Progress Data:
Date: {progress_data.get('date')}
Completed Activities: {progress_data.get('completed_activities')}
Mood Rating (1-5): {progress_data.get('mood_rating')}
Craving Intensity: {progress_data.get('craving_intensity')}
Relapsed: {progress_data.get('relapsed')}
Triggers: {progress_data.get('triggers')}
Confidence Rating (1-5): {progress_data.get('confidence_rating')}
Cravings Handling: {progress_data.get('cravings_handling')}
Self-reported Risk Level: {progress_data.get('risk_level')}

{f"Plan Context: {plan_data}" if plan_data else ""}

Return:
1. Self-harm detected (true/false)
2. Risk assessment (low/medium/high)
3. AI Analysis (comprehensive assessment of daily progress)
4. Recommendations (specific suggestions for improvement)

Please format your response as JSON with the following structure:
{{
    "self_harm_detected": true/false,
    "risk_assessment": "low/medium/high",
    "ai_analysis": "detailed analysis text",
    "recommendations": "specific recommendations text"
}}"""
    
    try:
        api_url = "https://api.groq.com/openai/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "You are a professional rehabilitation monitoring AI. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        response = requests.post(f"{api_url}/chat/completions", headers=headers, json=data, timeout=30)
        print(f"Daily Progress API Response Status: {response.status_code}")
        print(f"Daily Progress API Response Body: {response.text}")
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"Daily Progress AI Content: {content}")
        
        # Try to parse JSON, handle cases where AI returns non-JSON
        try:
            ai_response = json.loads(content)
        except json.JSONDecodeError:
            # If AI didn't return JSON, extract values using regex
            import re
            self_harm_match = re.search(r'self_harm_detected["\s:]+(true|false)', content, re.IGNORECASE)
            risk_match = re.search(r'risk_assessment["\s:]+["\']?([\w]+)["\']?', content, re.IGNORECASE)
            analysis_match = re.search(r'ai_analysis["\s:]+["\']?([^"\']+)["\']?', content, re.IGNORECASE)
            rec_match = re.search(r'recommendations["\s:]+["\']?([^"\']+)["\']?', content, re.IGNORECASE)
            
            ai_response = {
                'self_harm_detected': bool(self_harm_match) and self_harm_match.group(1).lower() == 'true',
                'risk_assessment': risk_match.group(1) if risk_match else 'low',
                'ai_analysis': analysis_match.group(1) if analysis_match else content[:500],
                'recommendations': rec_match.group(1) if rec_match else 'Continue tracking your progress.'
            }
        
        return {
            'self_harm_detected': ai_response.get('self_harm_detected', False),
            'risk_level': ai_response.get('risk_assessment', 'low'),
            'ai_analysis': ai_response.get('ai_analysis', 'No analysis provided'),
            'recommendations': ai_response.get('recommendations', 'No recommendations provided')
        }
        
    except Exception as e:
        return {
            'self_harm_detected': False,
            'risk_level': progress_data.get('risk_level', 'low'),
            'ai_analysis': 'AI analysis temporarily unavailable. Your progress has been recorded and will be analyzed later.',
            'recommendations': 'Continue tracking your progress daily. Contact support if this issue persists.'
        }


def detect_self_harm_indicators(progress_data):
    """
    Detect self-harm indicators in daily progress data.
    
    Args:
        progress_data (dict): Daily progress data
        
    Returns:
        dict: Detection result with detected flag and risk level
    """
    self_harm_keywords = [
        'suicide', 'kill myself', 'end it', 'hurt myself', 'self harm',
        'die', 'death', 'no point', 'hopeless', 'give up', 'end my life',
        'want to die', 'better off dead', 'can\'t go on'
    ]
    
    text_fields = [
        progress_data.get('triggers', ''),
        progress_data.get('cravings_handling', '')
    ]
    
    detected = False
    risk_level = 'low'
    
    for text in text_fields:
        if text:
            text_lower = text.lower()
            for keyword in self_harm_keywords:
                if keyword in text_lower:
                    detected = True
                    risk_level = 'high'
                    break
        if detected:
            break
    
    # Also check for extremely low mood and high risk
    mood = progress_data.get('mood_rating', 5)
    if mood <= 1 and progress_data.get('risk_level') == 'high':
        detected = True
        risk_level = 'high'
    
    return {
        'detected': detected,
        'risk': risk_level
    }


def calculate_simple_risk(plan_data):
    """
    Calculate a simple risk level based on plan data (fallback when AI is unavailable).
    
    Args:
        plan_data (dict): Rehabilitation plan data
        
    Returns:
        int: Risk level (0-100)
    """
    risk = 50  # Base risk
    
    # Adjust based on hours per day
    hours = plan_data.get('hours_per_day', 1)
    if hours >= 4:
        risk -= 20
    elif hours >= 2:
        risk -= 10
    else:
        risk += 10
    
    # Adjust based on number of activities
    activities = plan_data.get('activities', [])
    if len(activities) >= 3:
        risk -= 15
    elif len(activities) >= 2:
        risk -= 5
    
    # Adjust based on risk situations
    risk_situations = plan_data.get('risk_situations', '')
    if risk_situations:
        risk += 10
    
    # Ensure risk is within bounds
    return max(0, min(100, risk))
