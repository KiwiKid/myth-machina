from django.contrib.gis.db import models as gis_models

from django.db import models

from user.models import NoteUser


class Search(models.Model):
   # id = models.AutoField()
    location = gis_models.PointField()
    # author = models.ForeignKey(NoteUser, on_delete=models.CASCADEm )


# Create your models here.
class Place(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    author = models.ForeignKey(NoteUser, on_delete=models.CASCADE,
                               related_name='notes')
    wiki_title: models.TextField(blank=True)
    wiki_url: models.TextField(blank=True)
    wiki_summary = models.TextField(blank=True)
    completed_at = models.DateTimeField(
        help_text="None if the note isn't completed. Contain datetime when the note was completed", blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = gis_models.PointField(blank=True, null=True)

    def __str__(self):
        return f'{self.title}: {self.title}'

    @property
    def is_completed(self):
        '''check if note completed'''
        if self.completed_at is not None:
            return True
        return False
