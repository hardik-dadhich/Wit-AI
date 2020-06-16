# Create your models here.
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models


# class AudioFile(models.Model):
#     audio_file = models.FileField(
#         storage=FileSystemStorage(location=settings.MEDIA_ROOT)
#     )

count = 0


class Recording(models.Model):
    count += 1
    name = models.CharField(default=f'latest{count}', max_length=20)
    audiofile = models.FileField(upload_to=f'recordings/{name}')

    # def __unicode__(self):
    #     return unicode(self.name)

    def __str__(self):
        return self.name

    def is_from_today(self):
        path_comp = self.audiofile._get_path().split('/')
        date_path = path_comp[-4:-1]  # Y/m/d
        date_comp = map(int, date_path)
        file_date = date(*date_comp)
        return file_date == date.today()
