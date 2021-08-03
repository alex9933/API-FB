from django.db import models

class Account(models.Model):
    login = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

    def list(self):
        return [self.login, self.password]
