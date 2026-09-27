from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import HallRental, JobApplication, UserProfile, ItemComment  # добавили ItemComment
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment', 'dishes', 'food_rating', 'service_rating', 'atmosphere_rating']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о вашем визите...'}),
            'dishes': forms.CheckboxSelectMultiple(),
            'food_rating': forms.RadioSelect(),
            'service_rating': forms.RadioSelect(),
            'atmosphere_rating': forms.RadioSelect(),
        }
        labels = {
            'comment': 'Ваш отзыв',
            'dishes': 'Какие блюда попробовали?',
            'food_rating': 'Оценка еды',
            'service_rating': 'Оценка обслуживания',
            'atmosphere_rating': 'Оценка атмосферы',
        }

    def clean_comment(self):
        text = self.cleaned_data.get('comment', '')
        lower_text = text.lower()
        for word in BAD_WORDS:
            if word in lower_text:
                raise ValidationError(f'Текст содержит запрещённое слово: "{word}". Пожалуйста, удалите его.')
        return text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Сделаем звёзды в виде символов
        for field in ['food_rating', 'service_rating', 'atmosphere_rating']:
            self.fields[field].choices = [(i, '★' * i + '☆' * (5 - i)) for i in range(1, 6)]

import re

# Список запрещённых слов (можно дополнить)
BAD_WORDS = [
   r'ху[ейёяю]',r'хул[ию]',r'пизд',r'пи[зс]д',r'[eё]б',r'ебу',r'бля',r'сук[аи]'
]
PATTERN = re.compile(r'\b(?:' + '|'.join(BAD_WORDS) + r')\w*',re.IGNORECASE | re.UNICODE)

class HallRentalForm(forms.ModelForm):
    class Meta:
        model = HallRental
        fields = ['full_name', 'phone', 'email', 'event_type', 'guests_count', 
                  'start_datetime', 'end_datetime', 'comment']
        labels = {
            'full_name': 'Ваше имя *',
            'phone': 'Телефон *',
            'email': 'Email *',
            'event_type': 'Тип мероприятия',
            'guests_count': 'Количество гостей',
            'start_datetime': 'Начало аренды',
            'end_datetime': 'Конец аренды',
            'comment': 'Комментарий',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        pass

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'age', 'phone', 'email', 'position', 'experience', 'available_interview', 'comment']
        labels = {
            'full_name': 'ФИО *',
            'age': 'Возраст',
            'phone': 'Телефон *',
            'email': 'Email *',
            'position': 'Желаемая должность',
            'experience': 'Опыт работы',
            'available_interview': 'Удобное время для собеседования',
            'comment': 'Дополнительная информация',
        }
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 4}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Логин *',
            'password1': 'Пароль *',
            'password2': 'Подтверждение пароля *',
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', '')
            )
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'birth_date']
        labels = {
            'phone': 'Телефон',
            'address': 'Адрес',
            'birth_date': 'Дата рождения',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
class CommentForm(forms.ModelForm):
    class Meta:
        model = ItemComment
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ваш комментарий...'}),
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
        }
        labels = {
            'text': 'Комментарий',
            'rating': 'Ваша оценка',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [(0, '⭐ Без оценки')] + [(i, '★' * i + '☆' * (5 - i)) for i in range(1, 6)]

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        lower_text = text.lower()
        for word in BAD_WORDS:
            if word in lower_text:
                raise ValidationError(f'Текст содержит запрещённое слово: "{word}". Пожалуйста, удалите его.')
        return text