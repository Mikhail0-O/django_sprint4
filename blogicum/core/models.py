from django.db import models


class PublishedModel(models.Model):
    """Абстрактная модель для флага is_published"""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class CreatedAtModel(models.Model):
    """Абстрактная модель для флага created_at"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True
