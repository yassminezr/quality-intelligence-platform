from src.monitoring.notifications.formatter import AlertMessage
from src.monitoring.notifications.llm_writer import OpenAIAlertWriter


def main():
    original_message = AlertMessage(
        subject="[QIP] Action corrective - Critique - Min. Intérieur",
        body=(
            "Suivi d'une action corrective\n\n"
            "Action ID : 1\n"
            "Compte : Min. Intérieur\n"
            "Responsable : Mohamed\n"
            "Statut : En cours\n"
            "Âge : 67 jours\n"
            "Niveau : critique\n\n"
            "Action corrective :\n"
            "Formaliser le suivi des enjeux internes et externes."
        ),
    )

    writer = OpenAIAlertWriter()

    rewritten_message = writer.rewrite(original_message)

    print("\nMESSAGE ORIGINAL")
    print("=" * 70)
    print(original_message.subject)
    print(original_message.body)

    print("\nMESSAGE RÉDIGÉ PAR LE LLM")
    print("=" * 70)
    print(rewritten_message.subject)
    print(rewritten_message.body)


if __name__ == "__main__":
    main()