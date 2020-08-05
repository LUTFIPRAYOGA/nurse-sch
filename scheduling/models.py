from django.db import models

# Create your models here.

class Ruangan(models.Model):
    id_ruangan = models.AutoField(primary_key=True)
    nama_ruangan = models.CharField(max_length=50)
    def __str__(self):
        return u'{0}'.format(self.nama_ruangan)
    class Meta:
        managed = True
        db_table = "ruangan"



class Perawat(models.Model):
    KA = "Kepala Ruangan"
    PR = "Perawat"

    CHOICES = [(KA, KA), (PR, PR) ]

    id_perawat = models.AutoField(primary_key=True)
    nama_perawat = models.CharField(max_length=50)
    email_perawat = models.TextField()
    jenis_kelamin = models.CharField(max_length=10)
    status = models.CharField(choices=CHOICES, default=PR, max_length=20)
    ruangan = models.ForeignKey(Ruangan, related_name='ruanganfk', on_delete=models.CASCADE)
    class Meta:
        managed = True
        db_table = "perawat"

