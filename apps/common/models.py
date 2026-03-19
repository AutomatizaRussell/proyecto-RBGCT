from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserActivity(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50, default='login')
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date', 'activity_type')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.date}"
