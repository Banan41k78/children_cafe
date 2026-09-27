# kids_cafe/views.py
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from .forms import HallRentalForm, JobApplicationForm, RegistrationForm, UserProfileForm, CommentForm
from .models import MenuItem, HallRental, JobApplication, UserProfile, ItemComment
from .models import Feedback
from .forms import FeedbackForm

# views.py
def feedback_form(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            form.save_m2m()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('kids_cafe:feedback_list')
    else:
        form = FeedbackForm()
    context = {
        'form': form,
        'dishes_list': MenuItem.objects.all(),
    }
    return render(request, 'kids_cafe/feedback_form.html', context)

def feedback_list(request):
    feedbacks = Feedback.objects.all().select_related('user').prefetch_related('dishes')
    return render(request, 'kids_cafe/feedback_list.html', {'feedbacks': feedbacks})

    
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('kids_cafe:profile')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    rentals = HallRental.objects.filter(user=request.user).order_by('-start_datetime')
    job_apps = JobApplication.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('kids_cafe:profile')
    else:
        profile_form = UserProfileForm(instance=request.user.profile)

    return render(request, 'registration/profile.html', {
        'rentals': rentals,
        'job_apps': job_apps,
        'profile_form': profile_form,
    })


def index(request):
    context = {
        'title': 'Детское кафе "Сладкая страна"',
        'slogan': 'Где каждый день — праздник! 🎈',
        'special_offer': 'Детское мороженое в подарок при заказе от 500 ₽',
    }
    return render(request, 'kids_cafe/index.html', context)


def catalog(request):
    items = MenuItem.objects.all()
    context = {
        'title': 'Наше меню',
        'items': items,
    }
    return render(request, 'kids_cafe/catalog.html', context)


def product_detail(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    context = {
        'title': item.title,
        'item': item,
    }
    return render(request, 'kids_cafe/product_detail.html', context)


def about(request):
    context = {
        'title': 'О нас',
        'description': 'Мы — уютное кафе для детей и родителей. Аниматоры, безопасные игровые зоны, вкусная и полезная еда. Работаем с 2015 года.',
    }
    return render(request, 'kids_cafe/about.html', context)


def contacts(request):
    context = {
        'title': 'Контакты',
        'address': 'г. Тула, ул. Советская, д. 1',
        'phone': '+7 (950) 908-71-17',
        'email': 'hello@kidscafe.ru',
    }
    return render(request, 'kids_cafe/contacts.html', context)


def rental_form(request):
    active_rentals = HallRental.objects.filter(status__in=['pending', 'confirmed'])
    busy_slots = []
    for rental in active_rentals:
        busy_slots.append({
            'start': rental.start_datetime.isoformat(),
            'end': rental.end_datetime.isoformat(),
        })

    if request.method == 'POST':
        form = HallRentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            if request.user.is_authenticated:
                rental.user = request.user
            rental.save()
            messages.success(request, 'Ваша заявка на аренду принята! Мы свяжемся с вами.')
            return redirect('kids_cafe:rental_form')
    else:
        form = HallRentalForm()

    context = {
        'form': form,
        'busy_slots': json.dumps(busy_slots, cls=DjangoJSONEncoder),
    }
    return render(request, 'kids_cafe/rental.html', context)


def job_form(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            if request.user.is_authenticated:
                job.user = request.user
            job.save()
            messages.success(request, 'Ваша анкета отправлена! Мы рассмотрим её и свяжемся.')
            return redirect('kids_cafe:job_form')
    else:
        form = JobApplicationForm()
    return render(request, 'kids_cafe/job.html', {'form': form})



@login_required
def add_comment(request, item_id):
    menu_item = get_object_or_404(MenuItem, pk=item_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.menu_item = menu_item
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(ItemComment, pk=parent_id)
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
        else:
            messages.error(request, 'Ошибка в форме комментария.')
    return redirect('kids_cafe:product_detail', pk=item_id)


@login_required
def like_comment_ajax(request, comment_id):
    comment = get_object_or_404(ItemComment, pk=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({'likes': comment.total_likes(), 'liked': liked})


# Изменить существующую функцию product_detail (добавить комментарии и форму)
def product_detail(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    comments = ItemComment.objects.filter(menu_item=item, parent__isnull=True).select_related('author').prefetch_related('replies', 'likes')
    comment_form = CommentForm()
    context = {
        'title': item.title,
        'item': item,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'kids_cafe/product_detail.html', context)