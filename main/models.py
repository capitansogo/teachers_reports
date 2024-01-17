from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


def set_password(self, raw_password):
    self.password = make_password(raw_password)


class Post(models.Model):
    name = models.CharField(max_length=150, verbose_name='Должность', help_text='Введите должность')
    name_rod = models.CharField(max_length=150, verbose_name='Должность в родительном падеже',
                                help_text='Введите должность в родительном падеже')

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class Division(models.Model):
    name = models.CharField(max_length=150, verbose_name='Подразделение', help_text='Введите подразделение')

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = ['name']

    def __str__(self):
        return str(self.name)


# Create your models here.
class User(AbstractUser):
    patronymic = models.CharField(max_length=150, verbose_name='Отчество', null=True, blank=True,
                                  help_text='Введите отчество')
    id_teacher = models.IntegerField(verbose_name='ID преподавателя', null=True, blank=True, help_text='Введите ID')
    post = models.ForeignKey('Post', verbose_name='Должность', on_delete=models.CASCADE, null=True, blank=True,
                             help_text='Выберите должность')
    division = models.ForeignKey('Division', verbose_name='Подразделение', on_delete=models.CASCADE, null=True,
                                 blank=True, help_text='Выберите подразделение')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id_teacher']

    def __str__(self):
        return f'{self.id_teacher} {self.last_name} {self.first_name} {self.patronymic} {self.post} {self.division}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_password(self.password)
        super().save(*args, **kwargs)
