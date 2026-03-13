from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Номер телефона',
        blank=True,
        null=True,
        help_text='Формат: +7 (XXX) XXX-XX-XX'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name='Аватар',
        blank=True,
        null=True
    )
    bio = models.TextField(
        max_length=500,
        verbose_name='О себе',
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.phone if self.phone else 'без телефона'}"

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        ordering = ['user__username']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class FeedBack(models.Model):
    name = models.CharField(max_length=200, verbose_name="Тема")
    text = models.TextField(max_length=1000, verbose_name="Текст обращения")
    email = models.EmailField(max_length=200, verbose_name="E-mail")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратные связи"