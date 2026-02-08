"""
OpenCngsm MCP v3.0 - Pairing CLI Commands
CLI commands for managing DM pairing
"""
import click
from core.security.pairing import pairing_manager
from core.security.allowlist import allowlist_manager
from tabulate import tabulate


@click.group()
def pairing():
    """Manage DM pairing and allowlist"""
    pass


@pairing.command()
@click.argument('channel')
@click.argument('code')
def approve(channel: str, code: str):
    """
    Approve a pairing code
    
    Usage: opencngsm pairing approve telegram 123456
    """
    # Validate code
    pairing_info = pairing_manager.validate_code(code)
    
    if not pairing_info:
        click.echo(f"❌ Invalid or expired code: {code}")
        return
    
    # Check if channel matches
    if pairing_info['channel'] != channel:
        click.echo(f"❌ Code is for channel '{pairing_info['channel']}', not '{channel}'")
        return
    
    # Approve code
    if pairing_manager.approve_code(code):
        # Add user to allowlist
        user_id = pairing_info['user_id']
        if allowlist_manager.add_user(channel, user_id):
            click.echo(f"✅ Pairing approved!")
            click.echo(f"   Channel: {channel}")
            click.echo(f"   User: {user_id}")
            click.echo(f"   Code: {code}")
        else:
            click.echo(f"⚠️  Code approved but failed to add user to allowlist")
    else:
        click.echo(f"❌ Failed to approve code")


@pairing.command()
@click.option('--channel', help='Filter by channel')
def list(channel: str = None):
    """
    List pending pairing codes
    
    Usage: opencngsm pairing list
           opencngsm pairing list --channel telegram
    """
    codes = pairing_manager.get_pending_codes()
    
    if channel:
        codes = [c for c in codes if c['channel'] == channel]
    
    if not codes:
        click.echo("📭 No pending pairing codes")
        return
    
    # Format table
    table_data = []
    for code in codes:
        table_data.append([
            code['code'],
            code['channel'],
            code['user_id'],
            code['created_at'],
            code['expires_at']
        ])
    
    headers = ['Code', 'Channel', 'User ID', 'Created', 'Expires']
    click.echo("\n🔑 Pending Pairing Codes:\n")
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@pairing.command()
@click.argument('channel')
@click.argument('user_id')
def revoke(channel: str, user_id: str):
    """
    Revoke user access
    
    Usage: opencngsm pairing revoke telegram @username
    """
    if allowlist_manager.remove_user(channel, user_id):
        click.echo(f"✅ Access revoked for {channel}:{user_id}")
    else:
        click.echo(f"❌ Failed to revoke access (user may not be in allowlist)")


@pairing.command()
@click.option('--channel', help='Filter by channel')
def allowlist(channel: str = None):
    """
    List allowed users
    
    Usage: opencngsm pairing allowlist
           opencngsm pairing allowlist --channel telegram
    """
    users = allowlist_manager.list_users(channel)
    
    if not users:
        click.echo("📭 No users in allowlist")
        return
    
    # Format table
    table_data = []
    for user in users:
        table_data.append([
            user['channel'],
            user['user_id'],
            user['approved_by'],
            user['approved_at']
        ])
    
    headers = ['Channel', 'User ID', 'Approved By', 'Approved At']
    click.echo("\n✅ Allowed Users:\n")
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


if __name__ == '__main__':
    pairing()
