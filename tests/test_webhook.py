import json

def test_webhook_success(client):
    """
    Test successful processing of a valid 'account_created' webhook.
    """
    payload = {
        "event_id": "evt_001",
        "event_type": "account_created",
        "timestamp": "2026-06-08T12:00:00Z",
        "account": {
            "account_id": "ACC12345",
            "user_id": "USR001",
            "user_name": "Umar Shaikh",
            "broker": "Tradovate",
            "platform": "TradingView",
            "account_type": "Funded",
            "balance": 100000,
            "status": "Active"
        }
    }
    
    response = client.post('/webhook', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code == 201
    assert response.get_json()['status'] == 'success'
    assert response.get_json()['event_id'] == 'evt_001'

def test_webhook_duplicate_detection(client):
    """
    Test that sending the same event_id twice returns a success response 
    without processing it again (idempotency).
    """
    payload = {
        "event_id": "evt_002",
        "event_type": "account_created",
        "timestamp": "2026-06-08T12:00:00Z",
        "account": {
            "account_id": "ACC999",
            "user_id": "USR999",
            "user_name": "Test User"
        }
    }
    
    # First request
    response1 = client.post('/webhook', 
                            data=json.dumps(payload),
                            content_type='application/json')
    assert response1.status_code == 201
    
    # Second request (duplicate)
    response2 = client.post('/webhook', 
                            data=json.dumps(payload),
                            content_type='application/json')
    
    assert response2.status_code == 200
    assert "Duplicate" in response2.get_json()['message']
    assert response2.get_json()['event_id'] == 'evt_002'

def test_webhook_invalid_json(client):
    """
    Test handling of invalid JSON payloads.
    """
    response = client.post('/webhook', 
                           data="not a json string",
                           content_type='application/json')
    
    # Flask typically returns 400 for malformed JSON before it hits our route
    assert response.status_code == 400

def test_webhook_missing_fields(client):
    """
    Test handling of missing required fields in the payload.
    """
    payload = {
        "event_id": "evt_003",
        # "event_type" is missing
        "timestamp": "2026-06-08T12:00:00Z"
    }
    
    response = client.post('/webhook', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code == 400
    assert "Missing required field" in response.get_json()['error']

def test_webhook_unhandled_event(client):
    """
    Test handling of an event type that we don't support yet.
    """
    payload = {
        "event_id": "evt_004",
        "event_type": "payout_requested",
        "timestamp": "2026-06-08T12:00:00Z"
    }
    
    response = client.post('/webhook', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code == 201 # Still return success but log unhandled
    assert response.get_json()['status'] == 'success'
