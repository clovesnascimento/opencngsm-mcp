"""
Example: OpenCngsm + N8N Integration
Demonstrates bidirectional communication
"""
import asyncio
from skills.n8n.n8n_skill import N8NSkill
from skills.telegram.telegram_skill import TelegramSkill


async def example_1_execute_workflow():
    """Example 1: Execute N8N workflow from OpenCngsm"""
    print("📋 Example 1: Execute N8N Workflow")
    print("-" * 50)
    
    n8n = N8NSkill()
    
    # Execute workflow
    result = await n8n.execute_workflow(
        workflow_id='your-workflow-id',
        data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'action': 'send_welcome_email'
        }
    )
    
    print(f"✅ Workflow executed!")
    print(f"Execution ID: {result['id']}")
    print(f"Status: {result['status']}")
    print()


async def example_2_trigger_webhook():
    """Example 2: Trigger N8N webhook"""
    print("🔗 Example 2: Trigger N8N Webhook")
    print("-" * 50)
    
    n8n = N8NSkill()
    
    # Trigger webhook
    result = await n8n.trigger_webhook(
        webhook_path='opencngsm-trigger',
        data={
            'message': 'Hello from OpenCngsm!',
            'timestamp': '2024-01-01T12:00:00Z',
            'source': 'telegram'
        }
    )
    
    print(f"✅ Webhook triggered!")
    print(f"Response: {result}")
    print()


async def example_3_list_workflows():
    """Example 3: List and manage workflows"""
    print("📋 Example 3: List Workflows")
    print("-" * 50)
    
    n8n = N8NSkill()
    
    # List all workflows
    workflows = await n8n.list_workflows()
    
    print(f"Found {len(workflows)} workflows:")
    for workflow in workflows:
        status = "✅ Active" if workflow['active'] else "⏸️ Inactive"
        print(f"  {workflow['id']}: {workflow['name']} - {status}")
    
    print()


async def example_4_monitor_execution():
    """Example 4: Monitor workflow execution"""
    print("🔍 Example 4: Monitor Execution")
    print("-" * 50)
    
    n8n = N8NSkill()
    
    # Execute workflow
    result = await n8n.execute_workflow(
        workflow_id='your-workflow-id',
        data={'test': 'data'}
    )
    
    execution_id = result['id']
    print(f"Execution started: {execution_id}")
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Check status
    execution = await n8n.get_execution(execution_id)
    
    print(f"Status: {execution['status']}")
    print(f"Started: {execution['startedAt']}")
    if execution.get('finishedAt'):
        print(f"Finished: {execution['finishedAt']}")
    print()


async def example_5_telegram_to_n8n():
    """Example 5: Telegram → N8N → Email"""
    print("📱 Example 5: Telegram → N8N → Email")
    print("-" * 50)
    
    n8n = N8NSkill()
    telegram = TelegramSkill(
        bot_token='your-bot-token',
        chat_id='your-chat-id'
    )
    
    # Simulate receiving Telegram message
    telegram_message = "Send report to client@example.com"
    
    print(f"Received Telegram: {telegram_message}")
    
    # Trigger N8N workflow to send email
    result = await n8n.execute_workflow(
        workflow_id='email-sender',
        data={
            'to': 'client@example.com',
            'subject': 'Monthly Report',
            'body': 'Please find attached the monthly report.',
            'source': 'telegram'
        }
    )
    
    # Send confirmation back to Telegram
    await telegram.send_message(
        f"✅ Email sent via N8N!\nExecution ID: {result['id']}"
    )
    
    print("✅ Complete!")
    print()


async def example_6_scheduled_task():
    """Example 6: N8N scheduled task → OpenCngsm webhook"""
    print("⏰ Example 6: N8N Scheduled Task")
    print("-" * 50)
    
    print("""
    N8N Workflow Setup:
    
    1. Create workflow in N8N:
       - Trigger: Cron (0 9 * * *) - Daily at 9 AM
       - Action: HTTP Request
         - Method: POST
         - URL: http://localhost:18789/webhooks/n8n/daily-report
         - Body: {"report": "Daily metrics", "date": "{{$now}}"}
    
    2. OpenCngsm receives webhook:
    """)
    
    # This would be in your webhook handler
    example_payload = {
        'report': 'Daily metrics',
        'date': '2024-01-01T09:00:00Z',
        'metrics': {
            'users': 1000,
            'revenue': 5000
        }
    }
    
    print(f"Received webhook payload: {example_payload}")
    
    # Send to Telegram
    telegram = TelegramSkill(
        bot_token='your-bot-token',
        chat_id='your-chat-id'
    )
    
    await telegram.send_message(
        f"📊 Daily Report\n"
        f"Users: {example_payload['metrics']['users']}\n"
        f"Revenue: ${example_payload['metrics']['revenue']}"
    )
    
    print("✅ Report sent to Telegram!")
    print()


async def example_7_complex_automation():
    """Example 7: Complex multi-step automation"""
    print("🔄 Example 7: Complex Automation")
    print("-" * 50)
    
    n8n = N8NSkill()
    
    # Step 1: Trigger data collection workflow
    print("Step 1: Collecting data...")
    collection_result = await n8n.execute_workflow(
        workflow_id='data-collection',
        data={'source': 'api.example.com'}
    )
    
    # Step 2: Wait for completion
    await asyncio.sleep(3)
    
    # Step 3: Trigger processing workflow
    print("Step 2: Processing data...")
    processing_result = await n8n.execute_workflow(
        workflow_id='data-processing',
        data={'execution_id': collection_result['id']}
    )
    
    # Step 4: Trigger notification workflow
    print("Step 3: Sending notifications...")
    await n8n.execute_workflow(
        workflow_id='multi-channel-notification',
        data={
            'message': 'Data processing complete!',
            'channels': ['slack', 'discord', 'email']
        }
    )
    
    print("✅ Complex automation complete!")
    print()


async def main():
    """Run all examples"""
    print("🚀 OpenCngsm + N8N Integration Examples")
    print("=" * 50)
    print()
    
    # Test connection first
    n8n = N8NSkill()
    if not await n8n.test_connection():
        print("❌ Cannot connect to N8N. Please check:")
        print("  1. N8N is running")
        print("  2. N8N_API_URL is correct")
        print("  3. N8N_API_KEY is valid")
        return
    
    print("✅ Connected to N8N!")
    print()
    
    # Run examples
    try:
        await example_3_list_workflows()
        # await example_1_execute_workflow()
        # await example_2_trigger_webhook()
        # await example_4_monitor_execution()
        # await example_5_telegram_to_n8n()
        # await example_6_scheduled_task()
        # await example_7_complex_automation()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 50)
    print("Examples complete!")


if __name__ == "__main__":
    asyncio.run(main())
