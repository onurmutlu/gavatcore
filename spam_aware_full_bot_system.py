class SpamAwareFullBotSystem:
    def __init__(self):
        self.spam_detected = False

    def check_spam(self, message: str) -> bool:
        spam_keywords = ["spam", "reklam", "kazan", "bedava", "ücretsiz"]
        return any(keyword in message.lower() for keyword in spam_keywords)

    def process_message(self, message: str) -> str:
        if self.check_spam(message):
            self.spam_detected = True
            return "Spam tespit edildi. Lütfen uygun mesajlar gönderin."
        return "Mesaj işlendi." 