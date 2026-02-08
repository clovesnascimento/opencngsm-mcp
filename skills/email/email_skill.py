"""
OpenCngsm v3.0 - Email Skill
Native Python implementation using smtplib and imaplib (stdlib)
"""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class EmailSkill:
    """
    Email skill using Python's built-in libraries
    
    Features:
    - Send emails via SMTP (Gmail, Outlook, custom)
    - Receive emails via IMAP
    - HTML and plain text support
    - Attachments support
    - No external dependencies!
    """
    
    def __init__(
        self,
        smtp_host: str = 'smtp.gmail.com',
        smtp_port: int = 587,
        imap_host: str = 'imap.gmail.com',
        imap_port: int = 993,
        email_address: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize Email skill
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (587 for TLS, 465 for SSL)
            imap_host: IMAP server hostname
            imap_port: IMAP server port (993 for SSL)
            email_address: Your email address
            password: Your email password (use app password for Gmail)
        
        Gmail setup:
        1. Enable 2FA in Google Account
        2. Generate App Password: https://myaccount.google.com/apppasswords
        3. Use app password instead of regular password
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.email_address = email_address
        self.password = password
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send email via SMTP
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            html: If True, body is treated as HTML
            cc: List of CC recipients
            bcc: List of BCC recipients
            attachments: List of file paths to attach
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Add body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type, 'utf-8'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={file_path.split("/")[-1]}'
                            )
                            msg.attach(part)
                    except Exception as e:
                        logger.warning(f"Failed to attach {file_path}: {e}")
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.password)
                
                # Build recipient list
                recipients = [to]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    async def get_unread_emails(
        self,
        limit: int = 10,
        mark_as_read: bool = False
    ) -> List[Dict]:
        """
        Get unread emails via IMAP
        
        Args:
            limit: Maximum number of emails to fetch
            mark_as_read: If True, mark emails as read
        
        Returns:
            List of email dictionaries with keys:
            - from: Sender email
            - subject: Email subject
            - date: Email date
            - body: Email body (plain text)
        """
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.email_address, self.password)
            mail.select('INBOX')
            
            # Search for unread
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            emails = []
            
            for email_id in email_ids[:limit]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                # Parse email
                msg = email.message_from_bytes(msg_data[0][1])
                
                emails.append({
                    'from': msg['From'],
                    'subject': msg['Subject'],
                    'date': msg['Date'],
                    'body': self._get_email_body(msg)
                })
                
                # Mark as read if requested
                if mark_as_read:
                    mail.store(email_id, '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            
            logger.info(f"✅ Retrieved {len(emails)} unread emails")
            return emails
        
        except Exception as e:
            logger.error(f"❌ Failed to get emails: {e}")
            return []
    
    async def send_template_email(
        self,
        to: str,
        template: str,
        variables: Dict[str, str]
    ) -> bool:
        """
        Send email using a template
        
        Args:
            to: Recipient email
            template: Template name ('welcome', 'reset_password', 'notification')
            variables: Dict of variables to replace in template
        
        Returns:
            True if successful
        """
        templates = {
            'welcome': {
                'subject': f"Bem-vindo, {variables.get('name', 'Usuário')}!",
                'body': f"""
                <h1>Olá {variables.get('name', 'Usuário')}!</h1>
                <p>Seja bem-vindo à nossa plataforma.</p>
                <p>Seu email: {variables.get('email', '')}</p>
                """
            },
            'reset_password': {
                'subject': 'Redefinição de Senha',
                'body': f"""
                <h1>Redefinir Senha</h1>
                <p>Clique no link abaixo para redefinir sua senha:</p>
                <a href="{variables.get('reset_link', '#')}">Redefinir Senha</a>
                <p>Este link expira em 1 hora.</p>
                """
            },
            'notification': {
                'subject': variables.get('subject', 'Notificação'),
                'body': f"""
                <h2>{variables.get('title', 'Notificação')}</h2>
                <p>{variables.get('message', '')}</p>
                """
            }
        }
        
        if template not in templates:
            logger.error(f"Template '{template}' not found")
            return False
        
        template_data = templates[template]
        
        return await self.send_email(
            to=to,
            subject=template_data['subject'],
            body=template_data['body'],
            html=True
        )
    
    def _get_email_body(self, msg) -> str:
        """Extract email body from message"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == 'text/html':
                        # Fallback to HTML if no plain text
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Failed to extract email body: {e}")
            return ""


# Skill metadata
SKILL_NAME = "email"
SKILL_CLASS = EmailSkill
SKILL_DESCRIPTION = "Send and receive emails using Python stdlib (smtplib/imaplib)"


# Auto-register
from . import register_skill
register_skill(SKILL_NAME, SKILL_CLASS, SKILL_DESCRIPTION)
