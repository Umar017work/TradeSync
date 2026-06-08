import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template_string
from .database import db
from .models import WebhookEvent, Account

webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

@webhook_bp.route('/', methods=['GET'])
def index():
    """
    Dashboard endpoint showing live service statistics and recent activity.
    Designed for visual appeal in portfolio demonstrations.
    """
    try:
        event_count = WebhookEvent.query.count()
        account_count = Account.query.count()
        duplicate_count = WebhookEvent.query.filter_by(status='duplicate').count()
        last_event = WebhookEvent.query.order_by(WebhookEvent.received_at.desc()).first()
        recent_events = WebhookEvent.query.order_by(WebhookEvent.received_at.desc()).limit(10).all()
        
        last_event_time = last_event.received_at.strftime('%H:%M:%S') if last_event else "Never"
        db_status = "Connected"
        status_color = "#10b981" # Green
    except Exception as e:
        status_color = "#ef4444" # Red
        db_status = "Error"
        event_count = account_count = duplicate_count = 0
        last_event_time = "Error"
        recent_events = []
        logger.error(f"Dashboard data fetch failed: {str(e)}")

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TradeSync Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --bg: #0f172a;
                --card-bg: #1e293b;
                --text: #f8fafc;
                --text-muted: #94a3b8;
                --success: #10b981;
                --error: #ef4444;
                --warning: #f59e0b;
                --border: rgba(255, 255, 255, 0.05);
            }
            body {
                font-family: 'Outfit', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 2rem;
                min-height: 100vh;
            }
            .container {
                width: 100%;
                max-width: 900px;
            }
            .header {
                text-align: center;
                margin-bottom: 3rem;
                animation: fadeIn 0.8s ease-out;
            }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            .logo {
                font-size: 3rem;
                font-weight: 600;
                background: linear-gradient(to right, #818cf8, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }
            .status-badge {
                display: inline-flex;
                align-items: center;
                padding: 0.5rem 1rem;
                background: rgba(16, 185, 129, 0.1);
                color: var(--success);
                border-radius: 99px;
                font-size: 0.875rem;
                font-weight: 500;
            }
            .dot {
                height: 8px; width: 8px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-bottom: 3rem;
            }
            .metric-card {
                background: var(--card-bg);
                padding: 1.5rem;
                border-radius: 20px;
                border: 1px solid var(--border);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
            }
            .metric-card:hover { transform: translateY(-5px); }
            .metric-label { font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem; }
            .metric-value { font-size: 1.75rem; font-weight: 600; }
            
            .content-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 2rem;
            }
            .section-card {
                background: var(--card-bg);
                padding: 2rem;
                border-radius: 24px;
                border: 1px solid var(--border);
            }
            .section-title { font-size: 1.25rem; font-weight: 600; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; }
            
            table { width: 100%; border-collapse: collapse; text-align: left; }
            th { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; padding: 1rem; border-bottom: 1px solid var(--border); }
            td { padding: 1rem; border-bottom: 1px solid var(--border); font-size: 0.875rem; }
            .status-tag { padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
            .status-processed { background: rgba(16, 185, 129, 0.1); color: var(--success); }
            .status-duplicate { background: rgba(245, 158, 11, 0.1); color: var(--warning); }
            .status-error { background: rgba(239, 68, 68, 0.1); color: var(--error); }
            
            .demo-btn {
                background: linear-gradient(to right, var(--primary), #818cf8);
                color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 12px;
                font-family: 'Outfit', sans-serif; font-weight: 600; cursor: pointer;
                transition: all 0.3s ease; width: 100%; margin-top: 1rem;
            }
            .demo-btn:hover { filter: brightness(1.1); transform: scale(1.02); }
            .nav-links { margin-top: 2rem; display: flex; gap: 1rem; justify-content: center; }
            .nav-link { color: var(--text-muted); text-decoration: none; font-size: 0.875rem; }
            .nav-link:hover { color: var(--primary); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TradeSync</div>
                <div class="status-badge">
                    <span class="dot" style="background-color: {{ status_color }}; box-shadow: 0 0 10px {{ status_color }};"></span>
                    Portfolio Release v1.0 &bull; Webhook Service Online
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Events</div>
                    <div class="metric-value">{{ event_count }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Accounts Created</div>
                    <div class="metric-value">{{ account_count }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Duplicates Prevented</div>
                    <div class="metric-value" style="color: var(--warning)">{{ duplicate_count }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Last Activity</div>
                    <div class="metric-value">{{ last_event_time }}</div>
                </div>
            </div>

            <div class="content-grid">
                <div class="section-card">
                    <div class="section-title">
                        Recent Activity
                        <span style="font-size: 0.75rem; color: var(--text-muted)">Latest 10 Events</span>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Event ID</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for event in recent_events %}
                            <tr>
                                <td style="font-family: monospace">{{ event.event_id[:12] }}...</td>
                                <td>{{ event.event_type }}</td>
                                <td>
                                    <span class="status-tag status-{{ event.status }}">
                                        {{ event.status.upper() }}
                                    </span>
                                </td>
                                <td>{{ event.received_at.strftime('%H:%M:%S') }}</td>
                            </tr>
                            {% endfor %}
                            {% if not recent_events %}
                            <tr><td colspan="4" style="text-align: center; color: var(--text-muted)">No events found. Use the generator below.</td></tr>
                            {% endif %}
                        </tbody>
                    </table>
                    
                    <button class="demo-btn" onclick="generateDemoEvent()">Generate Sample Event</button>
                    <div id="demo-status" style="text-align: center; margin-top: 1rem; font-size: 0.75rem; min-height: 1rem;"></div>
                </div>
            </div>

            <div class="nav-links">
                <a href="/docs" class="nav-link">API Documentation</a>
                <a href="/health" class="nav-link">Health Status</a>
                <a href="/api/accounts" class="nav-link">Raw Accounts</a>
            </div>
        </div>

        <script>
            async function generateDemoEvent() {
                const btn = document.querySelector('.demo-btn');
                const status = document.getElementById('demo-status');
                btn.disabled = true;
                btn.textContent = 'Processing...';

                const isDuplicate = Math.random() < 0.2; // 20% chance to send a duplicate
                const demoId = isDuplicate ? 'demo_duplicate' : 'demo_' + Math.floor(Math.random() * 1000000);
                
                const payload = {
                    "event_id": demoId,
                    "event_type": "account_created",
                    "timestamp": new Date().toISOString(),
                    "account": {
                        "account_id": "ACC-" + (isDuplicate ? "DUP" : demoId.split('_')[1]),
                        "user_id": "USR-DEMO",
                        "user_name": "Demo Trader (Generated)",
                        "broker": "TradeSync Simulator",
                        "platform": "Demo-Mode",
                        "account_type": "Portfolio Demo",
                        "balance": 100000,
                        "status": "Active"
                    }
                };

                try {
                    const response = await fetch('/webhook', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (response.ok) {
                        status.textContent = 'Success! Webhook processed.';
                        status.style.color = 'var(--success)';
                        setTimeout(() => window.location.reload(), 1000);
                    }
                } catch (err) {
                    status.textContent = 'Error sending webhook.';
                    status.style.color = 'var(--error)';
                    btn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, 
                                 event_count=event_count, 
                                 account_count=account_count,
                                 duplicate_count=duplicate_count,
                                 last_event_time=last_event_time,
                                 recent_events=recent_events,
                                 status_color=status_color)

@webhook_bp.route('/docs', methods=['GET'])
def documentation():
    """
    Internal documentation page for recruiters.
    """
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>TradeSync API Documentation</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Outfit', sans-serif; background: #0f172a; color: #f8fafc; padding: 4rem; line-height: 1.6; }
            .container { max-width: 800px; margin: auto; }
            h1 { color: #818cf8; }
            h2 { border-bottom: 1px solid #1e293b; padding-bottom: 0.5rem; margin-top: 3rem; }
            code { background: #1e293b; padding: 0.2rem 0.4rem; border-radius: 4px; color: #c084fc; font-family: monospace; }
            pre { background: #1e293b; padding: 1.5rem; border-radius: 12px; overflow-x: auto; border: 1px solid rgba(255,255,255,0.05); }
            .method { font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 4px; margin-right: 0.5rem; }
            .post { background: rgba(16, 185, 129, 0.1); color: #10b981; }
            .get { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" style="color: #6366f1; text-decoration: none;">&larr; Back to Dashboard</a>
            <h1>API Documentation</h1>
            <p>Welcome to the TradeSync Portfolio Release v1.0. This API is designed for robustness and scale.</p>
            
            <h2>Endpoints</h2>
            
            <div>
                <h3><span class="method post">POST</span> /webhook</h3>
                <p>Receives platform events with idempotency tracking.</p>
                <p><strong>Example Request:</strong></p>
                <pre>{
    "event_id": "evt_unique_123",
    "event_type": "account_created",
    "timestamp": "2026-06-08T12:00:00Z",
    "account": {
        "account_id": "ACC123",
        "user_name": "Umar Shaikh",
        "balance": 100000
    }
}</pre>
            </div>
            
            <div>
                <h3><span class="method get">GET</span> /health</h3>
                <p>System health diagnostic endpoint.</p>
                <pre>{ "status": "healthy" }</pre>
            </div>
            
            <div>
                <h3><span class="method get">GET</span> /api/accounts</h3>
                <p>Returns a high-level summary of all accounts in the database.</p>
            </div>

            <h2>Architecture Overview</h2>
            <pre>Trading Platform → [Webhook] → TradeSync (Flask) → [SQLAlchemy] → Database (SQLite/PostgreSQL)</pre>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy"
    }), 200

@webhook_bp.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Returns a list of all trading accounts."""
    accounts = Account.query.all()
    return jsonify([{
        "account_id": a.account_id,
        "user_name": a.user_name,
        "broker": a.broker,
        "balance": a.balance,
        "status": a.status,
        "created_at": a.created_at.isoformat()
    } for a in accounts]), 200

@webhook_bp.route('/api/audit', methods=['GET'])
def get_audit():
    """Returns a list of all received webhook events."""
    events = WebhookEvent.query.all()
    return jsonify([{
        "event_id": e.event_id,
        "event_type": e.event_type,
        "status": e.status,
        "received_at": e.received_at.isoformat(),
        "payload": e.payload
    } for e in events]), 200

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Main endpoint for receiving webhooks.
    Handles idempotency and delegates event processing.
    """
    # 1. Basic validation
    if not request.is_json:
        logger.error("Received non-JSON payload")
        return jsonify({"error": "Payload must be JSON"}), 400
    
    data = request.get_json()
    logger.info(f"Received webhook: {data.get('event_type')} (ID: {data.get('event_id')})")

    # 2. Check for required top-level fields
    required_fields = ['event_id', 'event_type', 'timestamp']
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return jsonify({"error": f"Missing required field: {field}"}), 400

    event_id = data['event_id']
    event_type = data['event_type']

    # 3. Idempotency Check
    existing_event = WebhookEvent.query.filter_by(event_id=event_id).first()
    if existing_event:
        logger.warning(f"Duplicate event detected: {event_id}")
        return jsonify({
            "status": "success",
            "message": "Duplicate event ignored",
            "event_id": event_id
        }), 200

    # 4. Record the event (initial status: pending)
    new_event = WebhookEvent(
        event_id=event_id,
        event_type=event_type,
        payload=data,
        status='pending'
    )
    db.session.add(new_event)
    
    try:
        # 5. Process based on event type
        if event_type == 'account_created':
            process_account_created(data)
        else:
            logger.info(f"Unhandled event type: {event_type}")
            # We still record it as success if we don't handle it yet, 
            # but mark it appropriately
            new_event.status = 'unhandled'
        
        # 6. Update event status and commit
        if new_event.status == 'pending':
            new_event.status = 'processed'
        
        new_event.processed_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Successfully processed event: {event_id}")
        return jsonify({
            "status": "success",
            "message": "Webhook processed successfully",
            "event_id": event_id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing webhook {event_id}: {str(e)}")
        
        # Mark event as error if it was partially created
        new_event.status = 'error'
        db.session.commit()
        
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

def process_account_created(data):
    """
    Handles the 'account_created' event.
    """
    account_data = data.get('account')
    if not account_data:
        raise ValueError("Missing 'account' data in payload")

    # Validate required account fields
    required_account_fields = ['account_id', 'user_id', 'user_name']
    for field in required_account_fields:
        if field not in account_data:
            raise ValueError(f"Missing required account field: {field}")

    # Create or update the account
    account_id = account_data['account_id']
    account = Account.query.filter_by(account_id=account_id).first()

    if not account:
        account = Account(account_id=account_id)
        db.session.add(account)
        logger.info(f"Creating new account: {account_id}")
    else:
        logger.info(f"Updating existing account: {account_id}")

    # Map fields from payload to model
    account.user_id = account_data['user_id']
    account.user_name = account_data['user_name']
    account.broker = account_data.get('broker')
    account.platform = account_data.get('platform')
    account.account_type = account_data.get('account_type')
    account.balance = account_data.get('balance')
    account.status = account_data.get('status')
