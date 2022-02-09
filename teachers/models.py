from django.db import models


# Create your models here.
class Subjects(models.Model):
    subject_name = models.CharField(max_length=50)

    class Meta:
        db_table = "subjects"


class Teachers(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    profile_pic = models.ImageField(upload_to="profile_images/")
    email_address = models.EmailField(unique=True, max_length=100)
    phone_number = models.CharField(max_length=100)
    room_number = models.CharField(max_length=100)
    subjects_taught = models.ManyToManyField(Subjects, related_name="avail_subjects")

    class Meta:
        db_table = "Teachers"

    def __str__(self):
        return f"Name:{self.last_name}, Email:{self.email_address}"
