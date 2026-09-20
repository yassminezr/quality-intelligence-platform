from src.monitoring.notifications.email_sender import SMTPEmailSender
from src.monitoring.notifications.formatter import AlertMessage


class FakeSMTP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tls_started = False
        self.login_credentials = None
        self.sent_message = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def starttls(self):
        self.tls_started = True

    def login(self, username, password):
        self.login_credentials = (
            username,
            password,
        )

    def send_message(self, message):
        self.sent_message = message


def test_smtp_email_sender(monkeypatch):
    created_clients = []

    def fake_smtp_factory(host, port):
        client = FakeSMTP(
            host=host,
            port=port,
        )

        created_clients.append(client)

        return client

    monkeypatch.setattr(
        "src.monitoring.notifications.email_sender.smtplib.SMTP",
        fake_smtp_factory,
    )

    sender = SMTPEmailSender(
        host="smtp.example.com",
        port=587,
        username="qip@example.com",
        password="secret",
        sender_email="qip@example.com",
        use_tls=True,
    )

    alert = AlertMessage(
        subject="[QIP] Action critique",
        body="Une action corrective nécessite une attention.",
    )

    sender.send(
        recipient="responsable@example.com",
        message=alert,
    )

    assert len(created_clients) == 1

    smtp = created_clients[0]

    assert smtp.host == "smtp.example.com"
    assert smtp.port == 587

    assert smtp.tls_started is True

    assert smtp.login_credentials == (
        "qip@example.com",
        "secret",
    )

    assert smtp.sent_message["From"] == "qip@example.com"
    assert smtp.sent_message["To"] == "responsable@example.com"

    assert (
        smtp.sent_message["Subject"]
        == "[QIP] Action critique"
    )

    assert (
        "Une action corrective nécessite une attention."
        in smtp.sent_message.get_content()
    )