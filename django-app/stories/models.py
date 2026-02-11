from django.db import models
from django.contrib.auth.models import User

class Play(models.Model):
    story_id = models.IntegerField()  
    ending_page_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Level 16
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Play of story {self.story_id} - Ending {self.ending_page_id}"

class PlaySession(models.Model):
    session_key = models.CharField(max_length=40)
    story_id = models.IntegerField()
    current_page_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        unique_together = ['session_key', 'story_id']

