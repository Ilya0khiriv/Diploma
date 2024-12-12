from django.db import models

class Conversation(models.Model):
    user_message = models.TextField()
    ai_message = models.TextField()
    user_id = models.IntegerField(default=0)

    def __str__(self):
        return self.user_message

class AmountOfMessagesShown(models.Model):
    shown_messages = models.IntegerField(default=5)
    user_id = models.IntegerField()


    def __int__(self):
        return self.shown_messages


