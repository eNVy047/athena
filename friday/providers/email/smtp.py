import time
import smtplib
import imaplib
from email.mime.text import MIMEText
from typing import List, Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.email.base import EmailProvider

class SmtpEmailProvider(EmailProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="email",
            name="smtp",
            version="1.0.0",
            capabilities=["send_email", "read_emails"]
        )
        super().__init__(metadata, config)
        self.smtp_host = config.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(config.get("SMTP_PORT", "587"))
        self.imap_host = config.get("IMAP_HOST", "imap.gmail.com")
        self.username = config.get("EMAIL_USERNAME", "")
        self.password = config.get("EMAIL_PASSWORD", "")

    async def initialize(self) -> None:
        pass

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.username and self.password)

    async def send_email(self, recipient: str, subject: str, body: str) -> None:
        start_t = time.time()
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = recipient
        
        try:
            # Run blocking SMTP in a thread or direct call
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, [recipient], msg.as_string())
            server.quit()
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_t) * 1000, error_msg=str(e))
            raise e

    async def read_emails(self, folder: str = "INBOX", limit: int = 5) -> List[Dict[str, Any]]:
        start_t = time.time()
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host)
            mail.login(self.username, self.password)
            mail.select(folder)
            
            # Simple retrieval of last N emails
            status, data = mail.search(None, "ALL")
            mail_ids = data[0].split()
            recent_ids = mail_ids[-limit:]
            
            emails = []
            for m_id in recent_ids:
                status, msg_data = mail.fetch(m_id, "(RFC822)")
                # Just mock-free parsing or stub values representing retrieved messages
                emails.append({"id": m_id.decode("utf-8"), "raw_length": len(msg_data[0][1])})
                
            mail.logout()
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_t) * 1000)
            return emails
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_t) * 1000, error_msg=str(e))
            raise e
