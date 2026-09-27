# kids_cafe/admin.py
import csv
import io
from datetime import datetime, timedelta
import base64 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth
from .models import MenuItem, Feedback, ItemComment,HallRental,JobApplication

# Обычная регистрация моделей
admin.site.register(MenuItem)
admin.site.register(HallRental)
admin.site.register(JobApplication)
admin.site.register(Feedback)
admin.site.register(ItemComment)

# ---------- Графики ----------
def plot_popular_dishes():
    """График: 10 самых популярных блюд по упоминаниям в отзывах"""
    dishes = MenuItem.objects.annotate(cnt=Count('feedback')).filter(cnt__gt=0).order_by('-cnt')[:10]
    if not dishes:
        return None
    names = [d.title for d in dishes]
    counts = [d.cnt for d in dishes]
    plt.figure(figsize=(10, 6))
    plt.barh(names, counts, color='#ffa502')
    plt.xlabel('Количество упоминаний')
    plt.title('Самые популярные блюда')
    plt.gca().invert_yaxis()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer

def plot_ratings_distribution():
    """Распределение оценок по комментариям"""
    ratings = ItemComment.objects.exclude(rating=0).values('rating').annotate(cnt=Count('id')).order_by('rating')
    if not ratings:
        return None
    labels = [f'{r["rating"]} ★' for r in ratings]
    values = [r['cnt'] for r in ratings]
    plt.figure(figsize=(8, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ffa502', '#ff6b6b', '#3742fa', '#2ed573', '#ff4757'])
    plt.title('Распределение оценок в комментариях')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer

def plot_feedback_trend():
    """Динамика количества отзывов по месяцам (работает с PostgreSQL и SQLite)"""
    now = datetime.now()
    six_months_ago = now - timedelta(days=180)
    
    # Группировка по месяцам с помощью TruncMonth (кросс-БД)
    trends = (Feedback.objects
              .filter(created_at__gte=six_months_ago)
              .annotate(month=TruncMonth('created_at'))
              .values('month')
              .annotate(cnt=Count('id'))
              .order_by('month'))
    
    if not trends:
        return None
    
    months = [t['month'].strftime('%Y-%m') for t in trends]
    counts = [t['cnt'] for t in trends]
    
    plt.figure(figsize=(10, 5))
    plt.plot(months, counts, marker='o', linestyle='-', color='#ff6b6b')
    plt.xlabel('Месяц')
    plt.ylabel('Количество отзывов')
    plt.title('Динамика отзывов за последние 6 месяцев')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer
# ---------- Выгрузка CSV ----------
def export_feedback_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="feedback.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Пользователь', 'Комментарий', 'Еда', 'Обслуживание', 'Атмосфера', 'Средняя', 'Дата'])
    for fb in Feedback.objects.select_related('user').all():
        avg = fb.average_rating() if hasattr(fb, 'average_rating') else 0
        writer.writerow([fb.id, fb.user.username, fb.comment, fb.food_rating, fb.service_rating, fb.atmosphere_rating, avg, fb.created_at])
    return response

def export_comments_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comments.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Блюдо', 'Автор', 'Текст', 'Оценка', 'Лайки', 'Дата'])
    for cm in ItemComment.objects.select_related('menu_item', 'author'):
        writer.writerow([cm.id, cm.menu_item.title, cm.author.username, cm.text, cm.rating, cm.total_likes(), cm.created_at])
    return response

def export_popular_dishes_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="popular_dishes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Блюдо', 'Упоминания в отзывах', 'Средний рейтинг (комментарии)'])
    dishes = MenuItem.objects.annotate(feedback_count=Count('feedback'), avg_rating=Avg('comments__rating')).filter(feedback_count__gt=0).order_by('-feedback_count')
    for d in dishes:
        writer.writerow([d.title, d.feedback_count, d.avg_rating or 0])
    return response

# ---------- Главная страница статистики ----------
def statistics_view(request):
    popular_plot = plot_popular_dishes()
    ratings_plot = plot_ratings_distribution()
    trend_plot = plot_feedback_trend()
    context = {
        'title': 'Статистика кафе',
        'popular_plot': base64.b64encode(popular_plot.getvalue()).decode() if popular_plot else None,
        'ratings_plot': base64.b64encode(ratings_plot.getvalue()).decode() if ratings_plot else None,
        'trend_plot': base64.b64encode(trend_plot.getvalue()).decode() if trend_plot else None,
    }
    return render(request, 'admin/statistics.html', context)
# Добавляем URL в админку (через get_urls)
original_get_urls = admin.site.get_urls


def popular_dishes_view(request):
    dishes = MenuItem.objects.annotate(
        feedback_count=Count('feedback'),
        avg_rating_from_comments=Avg('comments__rating')
    ).filter(feedback_count__gt=0).order_by('-feedback_count')
    context = {
        'dishes': dishes,
        'title': 'Самые популярные блюда'
    }
    return render(request, 'admin/popular_dishes.html', context)

def negative_feedback_view(request):
    bad_feedbacks = Feedback.objects.filter(
        food_rating__lte=2,
        service_rating__lte=2,
        atmosphere_rating__lte=2
    ).order_by('-created_at')
    bad_comments = ItemComment.objects.filter(rating__in=[1, 2]).order_by('-created_at')
    context = {
        'bad_feedbacks': bad_feedbacks,
        'bad_comments': bad_comments,
        'title': 'Негативные отзывы и комментарии'
    }
    return render(request, 'admin/negative_feedback.html', context)

def custom_get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('statistics/', admin.site.admin_view(statistics_view), name='statistics'),
        path('statistics/popular-dishes/', admin.site.admin_view(popular_dishes_view), name='popular_dishes'),
        path('statistics/negative-feedback/', admin.site.admin_view(negative_feedback_view), name='negative_feedback'),
        path('statistics/export-feedback/', admin.site.admin_view(export_feedback_csv), name='export_feedback_csv'),
        path('statistics/export-comments/', admin.site.admin_view(export_comments_csv), name='export_comments_csv'),
        path('statistics/export-popular/', admin.site.admin_view(export_popular_dishes_csv), name='export_popular_csv'),
    ]
    return custom_urls + urls

admin.site.get_urls = custom_get_urls