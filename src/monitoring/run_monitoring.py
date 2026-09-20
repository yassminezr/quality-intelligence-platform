from __future__ import annotations

import os
from datetime import date

import psycopg2

from src.monitoring.audit import MonitoringAuditLogger
from src.monitoring.notifications.llm_writer import (
    DeterministicFallbackWriter,
    OpenAIAlertWriter,
)
from src.monitoring.notifications.notification_config import (
    build_email_sender,
    build_recipient_resolver,
)
from src.monitoring.notifications.notification_service import (
    NotificationService,
)
from src.monitoring.notifications.service import (
    AlertPreparationService,
)
from src.monitoring.notifications.writing_service import (
    AlertWritingService,
)
from src.monitoring.repository import CorrectiveActionRepository
from src.monitoring.run_audit import MonitoringRunLogger
from src.monitoring.service import CorrectiveActionMonitoringService


def create_database_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv(
            "POSTGRES_DB",
            "quality_intelligence",
        ),
        user=os.getenv(
            "POSTGRES_USER",
            "qip_user",
        ),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def run_monitoring() -> None:
    connection = create_database_connection()

    run_logger = MonitoringRunLogger(connection)

    run_id = run_logger.start_run()

    try:
        repository = CorrectiveActionRepository(
            connection=connection,
        )

        audit_logger = MonitoringAuditLogger(
            connection=connection,
        )

        monitoring_service = CorrectiveActionMonitoringService(
            repository=repository,
            audit_logger=audit_logger,
        )

        current_date = date.today()

        results, events = monitoring_service.run(
            current_date=current_date,
        )

        alert_service = AlertPreparationService()

        messages = alert_service.prepare_messages(
            events=events,
        )

        llm_enabled = (
            os.getenv(
                "LLM_ENABLED",
                "false",
            ).lower()
            == "true"
        )

        if llm_enabled:
            writer = OpenAIAlertWriter()
        else:
            writer = DeterministicFallbackWriter()

        writing_service = AlertWritingService(
            writer=writer,
        )

        final_messages = writing_service.rewrite_messages(
            messages=messages,
        )

        email_enabled = (
            os.getenv(
                "EMAIL_NOTIFICATIONS_ENABLED",
                "false",
            ).lower()
            == "true"
        )

        delivery_results = []

        if email_enabled and events:
            recipient_resolver = build_recipient_resolver()
            email_sender = build_email_sender()

            notification_service = NotificationService(
                recipient_resolver=recipient_resolver,
                email_sender=email_sender,
            )

            delivery_results = (
                notification_service.send_notifications(
                    events=events,
                    messages=final_messages,
                )
            )

        successful_emails = sum(
            1
            for result in delivery_results
            if result.success
        )

        failed_emails = sum(
            1
            for result in delivery_results
            if not result.success
        )

        run_logger.finish_success(
            run_id=run_id,
            actions_evaluated=len(results),
            events_detected=len(events),
            messages_prepared=len(final_messages),
            emails_sent=successful_emails,
            emails_failed=failed_emails,
        )

        print(
            f"Monitoring terminé : "
            f"{len(results)} action(s) évaluée(s), "
            f"{len(events)} événement(s), "
            f"{len(final_messages)} message(s), "
            f"{successful_emails} email(s) envoyé(s), "
            f"{failed_emails} échec(s)."
        )

        for delivery in delivery_results:
            if not delivery.success:
                print(
                    f"Échec email - "
                    f"action={delivery.action_id} - "
                    f"destinataire={delivery.recipient} - "
                    f"erreur={delivery.error}"
                )

    except Exception as exc:
        run_logger.finish_failed(
            run_id=run_id,
            error_message=str(exc),
        )

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    run_monitoring()