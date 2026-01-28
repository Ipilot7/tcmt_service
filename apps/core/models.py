from django.db import models

# Legacy Status model removed in favor of StatusChoices in choices.py

class AppUpdate(models.Model):
    title = models.CharField(max_length=255, verbose_name="Версия (заголовок)")
    version = models.CharField(max_length=50, unique=True, verbose_name="Версия (1.0.1+2)")
    description = models.TextField(verbose_name="Список изменений (HTML)")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    file = models.FileField(upload_to='updates/%Y/%m/', verbose_name="Файл инсталлятора")
    length = models.BigIntegerField(blank=True, null=True, verbose_name="Размер файла (байты, заполнится само)")
    file_type = models.CharField(max_length=100, default='application/octet-stream', verbose_name="MIME-тип")
    os_type = models.CharField(max_length=50, default='windows', verbose_name="ОС")

    class Meta:
        verbose_name = "Обновление ПО"
        verbose_name_plural = "Обновления ПО"
        ordering = ['-pub_date']

    def save(self, *args, **kwargs):
        if self.file and not self.length:
            self.length = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.version})"
