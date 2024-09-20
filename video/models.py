from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    subtitle_file = models.TextField(blank=True)  # To store the extracted subtitles

    def __str__(self):
        return self.title
