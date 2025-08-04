"""
Main views.py structure for the GreenLeaf Library System
This file should be in your main project directory
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.views.generic import TemplateView

from books.models import Book, BorrowRecord, Category, Reservation, Review
from books.forms import CustomUserCreationForm, ContactForm


class HomeView(TemplateView):
    """Homepage view with featured books and user stats"""
    template_name = 'books/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'featured_books': Book.objects.filter(
                is_active=True, is_featured=True
            ).select_related('category').prefetch_related('authors')[:6],
            'new_arrivals': Book.objects.filter(
                is_active=True
            ).order_by('-created_at')[:6],
            'popular_categories': Category.objects.annotate(
                book_count=Count('books', filter=Q(books__is_active=True))
            ).order_by('-book_count')[:4],
        })
        
        # Add user-specific data if authenticated
        if self.request.user.is_authenticated:
            user = self.request.user
            user_stats = {
                'books_borrowed': BorrowRecord.objects.filter(
                    user=user
            ).count(),
                'books_returned': BorrowRecord.objects.filter(
                    user=user, 
                    status='returned'
                ).count(),
                'current_borrowed': BorrowRecord.objects.filter(
                    user=user, 
                    status='active'
                ).count(),
                'overdue_books': BorrowRecord.objects.filter(
                    user=user,
                    status='active',
                    due_date__lt=timezone.now().date()
                ).count(),
            }
            
            recent_activity = BorrowRecord.objects.filter(
                user=user
            ).select_related('book').order_by('-borrow_date')[:5]
            
            context.update({
                'user_stats': user_stats,
                'recent_activity': recent_activity,
            })
        
        return context


def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('books:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to GreenLeaf Library! Your account has been created.')
            return redirect('books:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'books/registration/signup.html', {'form': form})


@login_required
def profile(request):
    """User profile and dashboard"""
    user = request.user
    borrowed_books = BorrowRecord.objects.filter(
        user=user, 
        status='active'
    ).select_related('book').order_by('due_date')
    
    overdue_books = borrowed_books.filter(
        due_date__lt=timezone.now().date()
    )
    
    reading_history = BorrowRecord.objects.filter(
        user=user,
        status='returned'
    ).select_related('book').order_by('-return_date')[:10]
    
    reservations = Reservation.objects.filter(
        user=user,
        is_active=True
    ).select_related('book')
    
    reviews = Review.objects.filter(
        user=user
    ).select_related('book').order_by('-created_at')[:5]
    
    context = {
        'borrowed_books': borrowed_books,
        'overdue_books': overdue_books,
        'reading_history': reading_history,
        'total_books_read': BorrowRecord.objects.filter(user=user, status='returned').count(),
        'reservations': reservations,
        'recent_reviews': reviews,
    }
    
    return render(request, 'books/registration/profile.html', context)


@login_required
def dashboard(request):
    """User dashboard with detailed statistics"""
    return render(request, 'books/dashboard.html')


def about(request):
    """About page"""
    return render(request, 'books/pages/about.html')


def contact(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process contact form
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'books/pages/contact.html', {'form': form})


def global_search(request):
    """Global search across all content"""
    query = request.GET.get('q', '')
    results = {}
    
    if query:
        # Search books
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(authors__first_name__icontains=query) |
            Q(authors__last_name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).select_related('category').prefetch_related('authors').distinct()[:10]
        
        # Search categories
        categories = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )[:5]
        
        results = {
            'books': books,
            'categories': categories,
            'query': query,
        }
    
    return render(request, 'books/search/results.html', results)


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with system statistics"""
    stats = {
        'total_books': Book.objects.filter(is_active=True).count(),
        'available_books': Book.objects.filter(available_copies__gt=0, is_active=True).count(),
        'borrowed_books': BorrowRecord.objects.filter(status='active').count(),
        'overdue_books': BorrowRecord.objects.filter(
            status='active',
            due_date__lt=timezone.now().date()
        ).count(),
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
    }
    
    # Get recent activity
    stats.update({
        'recent_borrows': BorrowRecord.objects.select_related('user', 'book').order_by('-borrow_date')[:10],
        'recent_returns': BorrowRecord.objects.filter(status='returned').select_related('user', 'book').order_by('-return_date')[:10],
        'recent_reviews': Review.objects.select_related('user', 'book').order_by('-created_at')[:5],
    })
    
    return render(request, 'books/admin/dashboard.html', {'stats': stats})


@staff_member_required
def admin_reports(request):
    """Admin reports and analytics"""
    return render(request, 'books/admin/reports.html')


def help_center(request):
    """Help center and FAQ"""
    return render(request, 'books/pages/help.html')


def faq(request):
    """Frequently Asked Questions"""
    return render(request, 'books/pages/faq.html')


def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'books/pages/terms.html')


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'books/pages/privacy.html')


@login_required
def profile(request):
    """User profile view"""
    user = request.user
    context = {
        'user': user,
        'borrowed_books': BorrowRecord.objects.filter(
            user=user, 
            status='borrowed'
        ).select_related('book'),
        'reservation_history': Reservation.objects.filter(
            user=user
        ).select_related('book'),
        'review_history': Review.objects.filter(
            user=user
        ).select_related('book'),
    }
    return render(request, 'books/user/profile.html', context)


@login_required
def dashboard(request):
    """User dashboard view"""
    user = request.user
    context = {
        'user': user,
        'current_borrows': BorrowRecord.objects.filter(
            user=user, 
            status='borrowed'
        ).select_related('book'),
        'pending_reservations': Reservation.objects.filter(
            user=user, 
            status='pending'
        ).select_related('book'),
        'recent_activity': BorrowRecord.objects.filter(
            user=user
        ).select_related('book').order_by('-borrow_date')[:5],
        'reading_stats': {
            'total_books_read': BorrowRecord.objects.filter(
                user=user, 
                status='returned'
            ).count(),
            'currently_reading': BorrowRecord.objects.filter(
                user=user, 
                status='borrowed'
            ).count(),
            'total_reviews': Review.objects.filter(user=user).count(),
        }
    }
    return render(request, 'books/user/dashboard.html', context)


# Custom Error Views
def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, 'books/errors/404.html', status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, 'books/errors/500.html', status=500)


def custom_403(request, exception):
    """Custom 403 error page"""
    return render(request, 'books/errors/403.html', status=403)


def custom_400(request, exception):
    """Custom 400 error page"""
    return render(request, 'books/errors/400.html', status=400)