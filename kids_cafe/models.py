# kids_cafe/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.CharField(max_length=200, blank=True, verbose_name="Адрес")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return self.user.username


class MenuItem(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.IntegerField(verbose_name="Цена (₽)")
    image = models.ImageField(upload_to='menu/', blank=True, null=True, verbose_name="Изображение")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    def avg_rating(self):
        comments_with_rating = self.comments.filter(rating__gt=0)
        if not comments_with_rating:
            return 0
        total = sum(c.rating for c in comments_with_rating)
        return round(total / comments_with_rating.count(), 1)

    def stars_display(self):
        avg = self.avg_rating()
        full = int(avg)
        return '★' * full + '☆' * (5 - full)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"

    def __str__(self):
        return self.title

class HallRental(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
        ('completed', 'Завершена'),
    ]
    full_name = models.CharField(max_length=150, verbose_name="Ваше имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    event_type = models.CharField(max_length=100, verbose_name="Тип мероприятия",
                                  choices=[('birthday', 'День рождения'),
                                           ('holiday', 'Праздник'),
                                           ('masterclass', 'Мастер-класс'),
                                           ('other', 'Другое')])
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    guests_count = models.PositiveSmallIntegerField(verbose_name="Количество гостей")
    start_datetime = models.DateTimeField(verbose_name="Начало аренды")
    end_datetime = models.DateTimeField(verbose_name="Конец аренды")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Аренда зала"
        verbose_name_plural = "Аренды зала"
        ordering = ['-start_datetime']

    def __str__(self):
        return f"{self.full_name} - {self.start_datetime.strftime('%d.%m.%Y %H:%M')}"

    def is_past(self):
        """Помечает аренду как прошедшую (относительно текущей даты)"""
        from django.utils import timezone
        return self.end_datetime < timezone.now()
    is_past.boolean = True
    is_past.short_description = "Прошедшая"


class JobApplication(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="ФИО")
    age = models.PositiveSmallIntegerField(verbose_name="Возраст")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    position = models.CharField(max_length=100, verbose_name="Желаемая должность",
                                choices=[('waiter', 'Официант'),
                                         ('cook', 'Повар'),
                                         ('animator', 'Аниматор'),
                                         ('admin', 'Администратор'),
                                         ('cleaner', 'Уборщик')])
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    experience = models.TextField(verbose_name="Опыт работы")
    available_interview = models.DateTimeField(verbose_name="Удобное время для собеседования")
    comment = models.TextField(blank=True, verbose_name="Дополнительная информация")
    status = models.CharField(max_length=20, choices=[('new', 'Новая'), ('viewed', 'Просмотрена'), ('rejected', 'Отклонена'), ('hired', 'Принят')], default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Анкета соискателя"
        verbose_name_plural = "Анкеты соискателей"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.position}"
    
class ItemComment(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    text = models.TextField(verbose_name="Текст комментария")
    rating = models.PositiveSmallIntegerField(
        default=0,
        choices=[(0, 'Без оценки')] + [(i, f'{i} звезд') for i in range(1, 6)],
        verbose_name="Оценка"
    )
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Комментарий от {self.author.username} к {self.menu_item.title}"


class Feedback(models.Model):
    RATING_CHOICES = [(i, f'{i} ★') for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    comment = models.TextField(verbose_name="Комментарий")
    dishes = models.ManyToManyField(MenuItem, blank=True, verbose_name="Попробованные блюда")

    # Оценки по направлениям
    food_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Качество еды")
    service_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Обслуживание")
    atmosphere_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Атмосфера")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def average_rating(self):
        """Средняя оценка (ос)"""
        return round((self.food_rating + self.service_rating + self.atmosphere_rating) / 3, 1)

    def stars_average(self):
        """Возвращает звёзды для средней оценки"""
        avg = self.average_rating()
        full = int(avg)
        half = 1 if avg - full >= 0.5 else 0
        return '★' * full + '½' * half + '☆' * (5 - full - half)

    def __str__(self):
        return f"Отзыв от {self.user.username} - {self.created_at.date()}"