from django.db import models
from utils import slugify
import tagging


class Repository(models.Model):
    pub_date = models.DateTimeField()
    version = models.IntegerField()
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=32) # meta id
    summary = models.CharField(max_length=255)
    description = models.TextField()
    urls = models.CharField(max_length=255)
    publications = models.CharField(max_length=255)
    license = models.CharField(max_length=255)
    is_public = models.BooleanField()

    class Meta:
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    def __unicode__(self):
        return unicode(self.name)

    def save(self):
        if not self.id:
            self.slug = slugify(self.name)
        super(Repository, self).save()


class Data(Repository):
    source = models.CharField(max_length=255)
    format = models.CharField(max_length=16) # CSV, ARFF, netCDF, HDF5, ODBC
    measurement_details = models.TextField()
    usage_scenario = models.TextField()
    file = models.FileField(upload_to='repository/data')

    def get_absolute_url(self):
        return self.file.url

tagging.register(Data)


class Task(Repository):
    format_input = models.CharField(max_length=255)
    format_output = models.CharField(max_length=255)
    performance_measure = models.CharField(max_length=255)
    data = models.ManyToManyField(Data)


class Solution(Repository):
    feature_processing = models.CharField(max_length=255)
    parameters = models.CharField(max_length=255)
    os = models.CharField(max_length=255)
    code = models.TextField()
    score = models.FileField(upload_to='repository/scores')
    task = models.ForeignKey(Task)


class Split(models.Model):
    data = models.ForeignKey(Data)
    task = models.ForeignKey(Task)
    splits = models.FileField(upload_to='repository/splits')

    def get_absolute_url(self):
        return self.splits.url

