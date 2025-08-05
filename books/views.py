from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import login
from django.db.models import Q, Count, Avg, F
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.conf import settings
import json
import csv
import os
from datetime import datetime, timedelta
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    TemplateView, FormView
)
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.contrib.auth.models import User
from django.db import models

from .models import (
    Category, Author, Publisher, Book, BorrowRecord, 
    Reservation, Review, Wishlist, ReadingList, ReadingListItem,
    BookHistory, Genre, BookCondition, Notification, UserProfile,
    UserActivity
)
from .forms import (
    CategoryForm, AuthorForm, PublisherForm, BookForm, BorrowRecordForm,
    ReturnBookForm, RenewBookForm, ReservationForm, ReviewForm, WishlistForm,
    ReadingListForm, ReadingListItemForm, GenreForm, BookConditionForm,
    BookSearchForm, NotificationForm, BulkBookActionForm, LibrarySettingsForm,
    CustomUserCreationForm, ProfileForm
)


def is_librarian(user):
    """Check if user is a librarian (staff member)"""
    return user.is_staff


# ==================== HOME AND DASHBOARD VIEWS ====================

class HomeView(TemplateView):
    """Library homepage with featured books and statistics"""
    template_name = 'books/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'featured_books': Book.objects.filter(
                is_active=True, is_featured=True
            ).select_related('category', 'publisher').prefetch_related('authors')[:6],
            'new_arrivals': Book.objects.filter(
                is_active=True, is_new_arrival=True
            ).select_related('category', 'publisher').prefetch_related('authors')[:6],
            'bestsellers': Book.objects.filter(
                is_active=True, is_bestseller=True
            ).select_related('category', 'publisher').prefetch_related('authors')[:6],
            'categories': Category.objects.filter(
                is_active=True, parent__isnull=True
            ).annotate(book_count=Count('books'))[:8],
            'total_books': Book.objects.filter(is_active=True).count(),
            'total_authors': Author.objects.filter(is_active=True).count(),
            'books_borrowed': BorrowRecord.objects.filter(status='active').count(),
        })
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard with personal library information"""
    template_name = 'books/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'active_borrows': BorrowRecord.objects.filter(
                user=user, status='active'
            ).select_related('book').order_by('due_date')[:5],
            'overdue_books': BorrowRecord.objects.filter(
                user=user, status='active', due_date__lt=timezone.now().date()
            ).select_related('book'),
            'reservations': Reservation.objects.filter(
                user=user, is_active=True
            ).select_related('book')[:5],
            'recent_reviews': Review.objects.filter(
                user=user
            ).select_related('book').order_by('-created_at')[:5],
            'wishlist_count': Wishlist.objects.filter(user=user).count(),
            'reading_lists': ReadingList.objects.filter(user=user)[:5],
            'notifications': Notification.objects.filter(
                user=user, is_read=False
            ).order_by('-created_at')[:5],
        })
        return context


# ==================== BOOK VIEWS ====================

class BookListView(ListView):
    """List all books with search and filtering"""
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Book.objects.filter(is_active=True).select_related(
            'category', 'publisher'
        ).prefetch_related('authors')
        
        form = BookSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            author = form.cleaned_data.get('author')
            language = form.cleaned_data.get('language')
            availability = form.cleaned_data.get('availability')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(subtitle__icontains=query) |
                    Q(authors__first_name__icontains=query) |
                    Q(authors__last_name__icontains=query) |
                    Q(isbn_10__icontains=query) |
                    Q(isbn_13__icontains=query) |
                    Q(description__icontains=query)
                ).distinct()
            
            if category:
                queryset = queryset.filter(category=category)
            
            if author:
                queryset = queryset.filter(authors=author)
            
            if language:
                queryset = queryset.filter(language=language)
            
            if availability == 'available':
                queryset = queryset.filter(available_copies__gt=0)
            elif availability == 'borrowed':
                queryset = queryset.filter(available_copies=0)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = BookSearchForm(self.request.GET)
        return context


class BookDetailView(DetailView):
    """Detailed view of a single book"""
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    
    def get_queryset(self):
        return Book.objects.filter(is_active=True).select_related(
            'category', 'publisher'
        ).prefetch_related('authors')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        user = self.request.user
        
        context.update({
            'reviews': Review.objects.filter(
                book=book, is_approved=True
            ).select_related('user').order_by('-created_at'),
            'user_review': None,
            'is_in_wishlist': False,
            'user_reservation': None,
            'can_borrow': book.is_available,
            'related_books': Book.objects.filter(
                category=book.category, is_active=True
            ).exclude(pk=book.pk)[:4]
        })
        
        if user.is_authenticated:
            try:
                context['user_review'] = Review.objects.get(book=book, user=user)
            except Review.DoesNotExist:
                pass
            
            context['is_in_wishlist'] = Wishlist.objects.filter(
                user=user, book=book
            ).exists()
            
            try:
                context['user_reservation'] = Reservation.objects.get(
                    user=user, book=book, is_active=True
                )
            except Reservation.DoesNotExist:
                pass
        
        return context


class BookCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new book (librarians only)"""
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        response = super().form_valid(form)
        
        # Create history record
        BookHistory.objects.create(
            book=self.object,
            action='created',
            librarian=self.request.user,
            details=f"Book created: {self.object.title}"
        )
        
        messages.success(self.request, f'Book "{self.object.title}" created successfully.')
        return response


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing book (librarians only)"""
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create history record
        BookHistory.objects.create(
            book=self.object,
            action='updated',
            librarian=self.request.user,
            details=f"Book updated: {self.object.title}"
        )
        
        messages.success(self.request, f'Book "{self.object.title}" updated successfully.')
        return response


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a book (librarians only)"""
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        book = self.get_object()
        book_title = book.title
        
        # Check if book has active borrows
        if BorrowRecord.objects.filter(book=book, status='active').exists():
            messages.error(request, 'Cannot delete book with active borrows.')
            return redirect('books:book_detail', pk=book.pk)
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Book "{book_title}" deleted successfully.')
        return response


# ==================== CATEGORY VIEWS ====================

class CategoryListView(ListView):
    """List all categories"""
    model = Category
    template_name = 'books/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).annotate(
            book_count=Count('books', filter=Q(books__is_active=True))
        ).order_by('name')


class CategoryDetailView(DetailView):
    """Show books in a specific category"""
    model = Category
    template_name = 'books/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        
        books = Book.objects.filter(
            category=category, is_active=True
        ).select_related('publisher').prefetch_related('authors')
        
        paginator = Paginator(books, 20)
        page_number = self.request.GET.get('page')
        context['books'] = paginator.get_page(page_number)
        
        return context


class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new category (librarians only)"""
    model = Category
    form_class = CategoryForm
    template_name = 'books/category_form.html'
    success_url = reverse_lazy('books:category_list')
    
    def test_func(self):
        return is_librarian(self.request.user)


# ==================== AUTHOR VIEWS ====================

class AuthorListView(ListView):
    """List all authors"""
    model = Author
    template_name = 'books/author_list.html'
    context_object_name = 'authors'
    paginate_by = 20
    
    def get_queryset(self):
        return Author.objects.filter(is_active=True).annotate(
            book_count=Count('books', filter=Q(books__is_active=True))
        ).order_by('last_name', 'first_name')


class AuthorDetailView(DetailView):
    """Show author details and their books"""
    model = Author
    template_name = 'books/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object
        
        books = Book.objects.filter(
            authors=author, is_active=True
        ).select_related('category', 'publisher')
        
        paginator = Paginator(books, 12)
        page_number = self.request.GET.get('page')
        context['books'] = paginator.get_page(page_number)
        
        return context


class AuthorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new author (librarians only)"""
    model = Author
    form_class = AuthorForm
    template_name = 'books/author_form.html'
    success_url = reverse_lazy('books:author_list')
    
    def test_func(self):
        return is_librarian(self.request.user)


# ==================== BORROWING VIEWS ====================

@login_required
@user_passes_test(is_librarian)
def borrow_book(request, book_id):
    """Process book borrowing (librarians only)"""
    book = get_object_or_404(Book, id=book_id, is_active=True)
    
    if request.method == 'POST':
        form = BorrowRecordForm(request.POST)
        if form.is_valid():
            if not book.is_available:
                messages.error(request, 'This book is not available for borrowing.')
                return redirect('books:book_detail', pk=book.pk)
            
            # Check if user already has maximum books
            user = form.cleaned_data['user']
            active_borrows = BorrowRecord.objects.filter(
                user=user, status='active'
            ).count()
            
            if active_borrows >= 5:  # Default maximum
                messages.error(request, 'User has reached maximum borrowing limit.')
                return redirect('books:book_detail', pk=book.pk)
            
            with transaction.atomic():
                borrow_record = form.save(commit=False)
                borrow_record.book = book
                borrow_record.librarian = request.user
                borrow_record.save()
                
                # Update book availability
                book.available_copies -= 1
                book.save()
                
                # Create history record
                BookHistory.objects.create(
                    book=book,
                    action='borrowed',
                    user=user,
                    librarian=request.user,
                    details=f"Borrowed by {user.username}"
                )
                
                messages.success(request, f'Book borrowed successfully to {user.username}.')
                return redirect('books:book_detail', pk=book.pk)
    else:
        form = BorrowRecordForm(initial={
            'book': book,
            'due_date': timezone.now().date() + timezone.timedelta(days=14)
        })
    
    return render(request, 'books/borrow_form.html', {
        'form': form,
        'book': book
    })


@login_required
@user_passes_test(is_librarian)
def return_book(request, borrow_id):
    """Process book return (librarians only)"""
    borrow_record = get_object_or_404(BorrowRecord, id=borrow_id, status='active')
    
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Update borrow record
                borrow_record.return_book()
                
                # Update book condition if needed
                new_condition = form.cleaned_data['condition']
                if new_condition != borrow_record.book.condition:
                    BookCondition.objects.create(
                        book=borrow_record.book,
                        condition=new_condition,
                        notes=form.cleaned_data.get('notes', ''),
                        updated_by=request.user
                    )
                    borrow_record.book.condition = new_condition
                    borrow_record.book.save()
                
                # Create history record
                BookHistory.objects.create(
                    book=borrow_record.book,
                    action='returned',
                    user=borrow_record.user,
                    librarian=request.user,
                    details=f"Returned by {borrow_record.user.username}"
                )
                
                # Check for reservations
                next_reservation = Reservation.objects.filter(
                    book=borrow_record.book, is_active=True
                ).order_by('reservation_date').first()
                
                if next_reservation:
                    # Notify user about availability
                    Notification.objects.create(
                        user=next_reservation.user,
                        type='available',
                        title='Reserved Book Available',
                        message=f'Your reserved book "{borrow_record.book.title}" is now available for pickup.',
                        book=borrow_record.book
                    )
                
                messages.success(request, 'Book returned successfully.')
                return redirect('books:borrow_list')
    else:
        form = ReturnBookForm(initial={'condition': borrow_record.book.condition})
    
    return render(request, 'books/return_form.html', {
        'form': form,
        'borrow_record': borrow_record
    })


@login_required
def renew_book(request, borrow_id):
    """Renew a borrowed book"""
    borrow_record = get_object_or_404(
        BorrowRecord, 
        id=borrow_id, 
        user=request.user, 
        status='active'
    )
    
    if request.method == 'POST':
        form = RenewBookForm(borrow_record, request.POST)
        if form.is_valid():
            days = form.cleaned_data['renewal_days']
            if borrow_record.renew(days):
                messages.success(request, f'Book renewed for {days} days.')
            else:
                messages.error(request, 'Maximum renewal limit reached.')
            return redirect('books:dashboard')
    else:
        form = RenewBookForm(borrow_record)
    
    return render(request, 'books/renew_form.html', {
        'form': form,
        'borrow_record': borrow_record
    })


class BorrowListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """List all borrow records (librarians only)"""
    model = BorrowRecord
    template_name = 'books/borrow_list.html'
    context_object_name = 'borrows'
    paginate_by = 50
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_queryset(self):
        status = self.request.GET.get('status', 'active')
        queryset = BorrowRecord.objects.select_related(
            'user', 'book', 'librarian'
        ).order_by('-borrow_date')
        
        if status == 'overdue':
            queryset = queryset.filter(
                status='active',
                due_date__lt=timezone.now().date()
            )
        elif status in ['active', 'returned', 'lost', 'damaged']:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', 'active')
        return context


# ==================== RESERVATION VIEWS ====================

@login_required
def reserve_book(request, book_id):
    """Reserve a book"""
    book = get_object_or_404(Book, id=book_id, is_active=True)
    
    if book.is_available:
        messages.info(request, 'This book is currently available for borrowing.')
        return redirect('books:book_detail', pk=book.pk)
    
    if request.method == 'POST':
        form = ReservationForm(request.user, request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            
            # Calculate position in queue
            reservation.position = Reservation.objects.filter(
                book=book, is_active=True
            ).count() + 1
            
            reservation.save()
            
            messages.success(
                request, 
                f'Book reserved successfully. You are #{reservation.position} in the queue.'
            )
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = ReservationForm(request.user, initial={'book': book})
    
    return render(request, 'books/reserve_form.html', {
        'form': form,
        'book': book
    })


@login_required
def cancel_reservation(request, reservation_id):
    """Cancel a book reservation"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user, 
        is_active=True
    )
    
    if request.method == 'POST':
        book_title = reservation.book.title
        reservation.is_active = False
        reservation.save()
        
        # Update positions for other reservations
        Reservation.objects.filter(
            book=reservation.book,
            is_active=True,
            position__gt=reservation.position
        ).update(position=F('position') - 1)
        
        messages.success(request, f'Reservation for "{book_title}" cancelled.')
        return redirect('books:dashboard')
    
    return render(request, 'books/cancel_reservation.html', {
        'reservation': reservation
    })


# ==================== REVIEW VIEWS ====================

@login_required
def add_review(request, book_id):
    """Add a review for a book"""
    book = get_object_or_404(Book, id=book_id, is_active=True)
    
    # Check if user already reviewed this book
    if Review.objects.filter(user=request.user, book=book).exists():
        messages.error(request, 'You have already reviewed this book.')
        return redirect('books:book_detail', pk=book.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            
            messages.success(request, 'Review added successfully.')
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = ReviewForm()
    
    return render(request, 'books/review_form.html', {
        'form': form,
        'book': book
    })


@login_required
def edit_review(request, review_id):
    """Edit user's own review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully.')
            return redirect('books:book_detail', pk=review.book.pk)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'books/review_form.html', {
        'form': form,
        'book': review.book,
        'editing': True
    })


@login_required
def delete_review(request, review_id):
    """Delete user's own review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    book = review.book
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully.')
        return redirect('books:book_detail', pk=book.pk)
    
    return render(request, 'books/delete_review.html', {'review': review})


# ==================== WISHLIST VIEWS ====================

@login_required
def wishlist_view(request):
    """User's wishlist"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('book').order_by('priority', '-added_date')
    
    paginator = Paginator(wishlist_items, 20)
    page_number = request.GET.get('page')
    wishlist_items = paginator.get_page(page_number)
    
    return render(request, 'books/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def add_to_wishlist(request, book_id):
    """Add book to wishlist"""
    book = get_object_or_404(Book, id=book_id, is_active=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={'priority': 3}
    )
    
    if created:
        messages.success(request, f'"{book.title}" added to your wishlist.')
    else:
        messages.info(request, f'"{book.title}" is already in your wishlist.')
    
    return redirect('books:book_detail', pk=book.pk)


@login_required
def remove_from_wishlist(request, book_id):
    """Remove book from wishlist"""
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, book_id=book_id)
        book_title = wishlist_item.book.title
        wishlist_item.delete()
        messages.success(request, f'"{book_title}" removed from your wishlist.')
    except Wishlist.DoesNotExist:
        messages.error(request, 'Book not found in your wishlist.')
    
    return redirect('books:wishlist')


# ==================== READING LIST VIEWS ====================

@login_required
def reading_lists_view(request):
    """User's reading lists"""
    reading_lists = ReadingList.objects.filter(
        user=request.user
    ).annotate(book_count=Count('books')).order_by('-updated_at')
    
    return render(request, 'books/reading_lists.html', {
        'reading_lists': reading_lists
    })


@login_required
def reading_list_detail(request, list_id):
    """Details of a specific reading list"""
    reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
    items = ReadingListItem.objects.filter(
        reading_list=reading_list
    ).select_related('book').order_by('order', 'added_date')
    
    return render(request, 'books/reading_list_detail.html', {
        'reading_list': reading_list,
        'items': items
    })


class ReadingListCreateView(LoginRequiredMixin, CreateView):
    """Create a new reading list"""
    model = ReadingList
    form_class = ReadingListForm
    template_name = 'books/reading_list_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('books:reading_lists')


# ==================== NOTIFICATION VIEWS ====================

@login_required
def notifications_view(request):
    """User notifications"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Mark as read
    notifications.filter(is_read=False).update(is_read=True)
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    return render(request, 'books/notifications.html', {
        'notifications': notifications
    })


# ==================== AJAX VIEWS ====================

@login_required
def mark_notification_read(request):
    """Mark notification as read (AJAX)"""
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(
                id=notification_id, user=request.user
            )
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def book_availability_check(request, book_id):
    """Check book availability (AJAX)"""
    try:
        book = Book.objects.get(id=book_id, is_active=True)
        return JsonResponse({
            'available': book.is_available,
            'available_copies': book.available_copies,
            'total_copies': book.total_copies
        })
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)


# ==================== ADMIN/LIBRARIAN VIEWS ====================

class LibrarianDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Librarian dashboard with library statistics"""
    template_name = 'books/librarian_dashboard.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        context.update({
            'total_books': Book.objects.filter(is_active=True).count(),
            'books_borrowed': BorrowRecord.objects.filter(status='active').count(),
            'overdue_books': BorrowRecord.objects.filter(
                status='active', due_date__lt=today
            ).count(),
            'active_reservations': Reservation.objects.filter(is_active=True).count(),
            'recent_borrows': BorrowRecord.objects.filter(
                borrow_date__date=today
            ).select_related('user', 'book').order_by('-borrow_date')[:10],
            'recent_returns': BorrowRecord.objects.filter(
                return_date__date=today
            ).select_related('user', 'book').order_by('-return_date')[:10],
            'popular_books': Book.objects.annotate(
                borrow_count=Count('borrow_records')
            ).order_by('-borrow_count')[:10],
            'new_reviews': Review.objects.filter(
                created_at__date=today
            ).select_related('user', 'book').order_by('-created_at')[:5],
        })
        return context


@login_required
@user_passes_test(is_librarian)
def bulk_book_actions(request):
    """Handle bulk actions on books"""
    if request.method == 'POST':
        form = BulkBookActionForm(request.POST)
        book_ids = request.POST.getlist('book_ids')
        
        if form.is_valid() and book_ids:
            action = form.cleaned_data['action']
            books = Book.objects.filter(id__in=book_ids)
            count = books.count()
            
            if action == 'activate':
                books.update(is_active=True)
                messages.success(request, f'{count} books activated.')
            
            elif action == 'deactivate':
                # Check for active borrows
                active_borrows = BorrowRecord.objects.filter(
                    book__in=books, status='active'
                ).exists()
                if active_borrows:
                    messages.error(request, 'Cannot deactivate books with active borrows.')
                else:
                    books.update(is_active=False)
                    messages.success(request, f'{count} books deactivated.')
            
            elif action == 'mark_featured':
                books.update(is_featured=True)
                messages.success(request, f'{count} books marked as featured.')
            
            elif action == 'unmark_featured':
                books.update(is_featured=False)
                messages.success(request, f'{count} books removed from featured.')
            
            elif action == 'update_condition':
                new_condition = form.cleaned_data.get('new_condition')
                if new_condition:
                    books.update(condition=new_condition)
                    # Create condition records
                    for book in books:
                        BookCondition.objects.create(
                            book=book,
                            condition=new_condition,
                            notes=f'Bulk update by {request.user.username}',
                            updated_by=request.user
                        )
                    messages.success(request, f'{count} books condition updated.')
            
            elif action == 'delete':
                # Check for active borrows
                active_borrows = BorrowRecord.objects.filter(
                    book__in=books, status='active'
                ).exists()
                if active_borrows:
                    messages.error(request, 'Cannot delete books with active borrows.')
                else:
                    books.delete()
                    messages.success(request, f'{count} books deleted.')
        
        return redirect('books:book_list')
    
    return redirect('books:book_list')


class ReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Library reports and statistics"""
    template_name = 'books/reports.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date range for reports
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=30)
        
        context.update({
            'period_borrows': BorrowRecord.objects.filter(
                borrow_date__date__range=[start_date, end_date]
            ).count(),
            'period_returns': BorrowRecord.objects.filter(
                return_date__date__range=[start_date, end_date]
            ).count(),
            'most_popular_books': Book.objects.annotate(
                borrow_count=Count('borrow_records')
            ).order_by('-borrow_count')[:10],
            'most_active_users': User.objects.annotate(
                borrow_count=Count('borrow_records')
            ).order_by('-borrow_count')[:10],
            'category_stats': Category.objects.annotate(
                book_count=Count('books', filter=Q(books__is_active=True)),
                borrow_count=Count('books__borrow_records')
            ).order_by('-borrow_count')[:10],
            'overdue_summary': BorrowRecord.objects.filter(
                status='active', 
                due_date__lt=end_date
            ).select_related('user', 'book'),
            'late_fees_collected': BorrowRecord.objects.filter(
                return_date__date__range=[start_date, end_date]
            ).aggregate(total_fees=models.Sum('late_fee'))['total_fees'] or 0,
        })
        return context


# ==================== SEARCH VIEWS ====================

class AdvancedSearchView(TemplateView):
    """Advanced search page"""
    template_name = 'books/advanced_search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = BookSearchForm()
        return context


def search_suggestions(request):
    """AJAX search suggestions"""
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    if len(query) >= 2:
        # Search in book titles
        books = Book.objects.filter(
            title__icontains=query, is_active=True
        ).values('title', 'id')[:5]
        
        # Search in author names
        authors = Author.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query),
            is_active=True
        ).values('first_name', 'last_name', 'id')[:5]
        
        for book in books:
            suggestions.append({
                'type': 'book',
                'title': book['title'],
                'url': reverse('books:book_detail', kwargs={'pk': book['id']})
            })
        
        for author in authors:
            suggestions.append({
                'type': 'author',
                'title': f"{author['first_name']} {author['last_name']}",
                'url': reverse('books:author_detail', kwargs={'pk': author['id']})
            })
    
    return JsonResponse({'suggestions': suggestions})


# ==================== USER PROFILE VIEWS ====================

@login_required
def user_profile(request):
    """User profile with borrowing history"""
    user = request.user
    
    # Get user's borrowing statistics
    borrow_history = BorrowRecord.objects.filter(user=user).select_related('book')
    
    context = {
        'user': user,
        'total_borrowed': borrow_history.count(),
        'books_returned': borrow_history.filter(status='returned').count(),
        'current_borrows': borrow_history.filter(status='active').count(),
        'overdue_count': borrow_history.filter(
            status='active', due_date__lt=timezone.now().date()
        ).count(),
        'total_late_fees': borrow_history.aggregate(
            total=models.Sum('late_fee')
        )['total'] or 0,
        'recent_borrows': borrow_history.order_by('-borrow_date')[:10],
        'favorite_categories': Category.objects.filter(
            books__borrow_records__user=user
        ).annotate(
            borrow_count=Count('books__borrow_records')
        ).order_by('-borrow_count')[:5],
        'reading_stats': {
            'total_reviews': Review.objects.filter(user=user).count(),
            'average_rating': Review.objects.filter(user=user).aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
            'wishlist_count': Wishlist.objects.filter(user=user).count(),
            'reading_lists_count': ReadingList.objects.filter(user=user).count(),
        }
    }
    
    return render(request, 'books/user/profile.html', context)


# ==================== EXPORT VIEWS ====================

@login_required
@user_passes_test(is_librarian)
def export_data(request):
    """Export library data (CSV format)"""
    import csv
    from django.http import HttpResponse
    
    export_type = request.GET.get('type', 'books')
    
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'books':
        response['Content-Disposition'] = 'attachment; filename="books_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Title', 'Authors', 'ISBN-13', 'Category', 'Publisher',
            'Publication Date', 'Total Copies', 'Available Copies',
            'Condition', 'Location'
        ])
        
        books = Book.objects.filter(is_active=True).select_related(
            'category', 'publisher'
        ).prefetch_related('authors')
        
        for book in books:
            writer.writerow([
                book.title,
                book.authors_list,
                book.isbn_13 or '',
                book.category.name if book.category else '',
                book.publisher.name if book.publisher else '',
                book.publication_date or '',
                book.total_copies,
                book.available_copies,
                book.get_condition_display(),
                book.location or ''
            ])
    
    elif export_type == 'borrows':
        response['Content-Disposition'] = 'attachment; filename="borrows_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'User', 'Book Title', 'Borrow Date', 'Due Date', 'Return Date',
            'Status', 'Late Fee', 'Librarian'
        ])
        
        borrows = BorrowRecord.objects.all().select_related(
            'user', 'book', 'librarian'
        )
        
        for borrow in borrows:
            writer.writerow([
                borrow.user.username,
                borrow.book.title,
                borrow.borrow_date.date(),
                borrow.due_date,
                borrow.return_date.date() if borrow.return_date else '',
                borrow.get_status_display(),
                borrow.late_fee,
                borrow.librarian.username if borrow.librarian else ''
            ])
    
    return response


# ==================== API ENDPOINTS ====================

@login_required
def api_book_search(request):
    """API endpoint for book search"""
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    if len(query) < 2:
        return JsonResponse({'books': []})
    
    books = Book.objects.filter(
        Q(title__icontains=query) | 
        Q(authors__first_name__icontains=query) |
        Q(authors__last_name__icontains=query),
        is_active=True
    ).select_related('category').prefetch_related('authors').distinct()[:limit]
    
    book_data = []
    for book in books:
        book_data.append({
            'id': book.id,
            'title': book.title,
            'authors': book.authors_list,
            'category': book.category.name if book.category else '',
            'available': book.is_available,
            'cover_url': book.cover_image.url if book.cover_image else None,
        })
    
    return JsonResponse({'books': book_data})


@login_required
@user_passes_test(is_librarian)
def api_user_search(request):
    """API endpoint for user search (librarians only)"""
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )[:limit]
    
    user_data = []
    for user in users:
        active_borrows = BorrowRecord.objects.filter(
            user=user, status='active'
        ).count()
        
        user_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip(),
            'email': user.email,
            'active_borrows': active_borrows,
        })
    
    return JsonResponse({'users': user_data})


# ==================== ERROR HANDLERS ====================

def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'books/404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'books/500.html', status=500)


# ==================== UTILITY VIEWS ====================

@login_required
@user_passes_test(is_librarian)
def library_settings(request):
    """Library settings management"""
    if request.method == 'POST':
        form = LibrarySettingsForm(request.POST)
        if form.is_valid():
            # Save settings to session or database
            # This would typically be stored in a Settings model
            messages.success(request, 'Library settings updated successfully.')
            return redirect('books:librarian_dashboard')
    else:
        # Load current settings
        form = LibrarySettingsForm()
    
    return render(request, 'books/library_settings.html', {'form': form})


@login_required
@user_passes_test(is_librarian)
def send_overdue_notifications(request):
    """Send notifications to users with overdue books"""
    overdue_borrows = BorrowRecord.objects.filter(
        status='active',
        due_date__lt=timezone.now().date()
    ).select_related('user', 'book')
    
    notifications_sent = 0
    
    for borrow in overdue_borrows:
        # Check if notification already sent today
        today = timezone.now().date()
        existing_notification = Notification.objects.filter(
            user=borrow.user,
            type='overdue',
            book=borrow.book,
            created_at__date=today
        ).exists()
        
        if not existing_notification:
            Notification.objects.create(
                user=borrow.user,
                type='overdue',
                title='Overdue Book',
                message=f'Your book "{borrow.book.title}" is overdue. '
                       f'Please return it as soon as possible to avoid additional fees.',
                book=borrow.book
            )
            notifications_sent += 1
    
    messages.success(
        request, 
        f'{notifications_sent} overdue notifications sent successfully.'
    )
    return redirect('books:librarian_dashboard')


@login_required
@user_passes_test(is_librarian)
def generate_barcode(request, book_id):
    """Generate and display barcode for a book"""
    book = get_object_or_404(Book, id=book_id)
    
    try:
        from barcode import Code128
        from barcode.writer import ImageWriter
        from io import BytesIO
        import base64
        
        # Generate barcode
        code128 = Code128(book.barcode, writer=ImageWriter())
        buffer = BytesIO()
        code128.write(buffer)
        
        # Convert to base64 for display
        buffer.seek(0)
        barcode_image = base64.b64encode(buffer.getvalue()).decode()
        
        return render(request, 'books/barcode.html', {
            'book': book,
            'barcode_image': barcode_image
        })
    
    except ImportError:
        messages.error(request, 'Barcode generation library not installed.')
        return redirect('books:book_detail', pk=book.pk)


# ==================== STATISTICS VIEWS ====================

class LibraryStatsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Detailed library statistics"""
    template_name = 'books/library_stats.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Monthly statistics for the past 12 months
        from django.db.models import Count, Q
        from datetime import date, timedelta
        import calendar
        
        monthly_stats = []
        for i in range(12):
            month_start = date.today().replace(day=1) - timedelta(days=i*30)
            month_end = month_start.replace(
                day=calendar.monthrange(month_start.year, month_start.month)[1]
            )
            
            borrows = BorrowRecord.objects.filter(
                borrow_date__date__range=[month_start, month_end]
            ).count()
            
            returns = BorrowRecord.objects.filter(
                return_date__date__range=[month_start, month_end]
            ).count()
            
            monthly_stats.append({
                'month': month_start.strftime('%B %Y'),
                'borrows': borrows,
                'returns': returns
            })
        
        context.update({
            'monthly_stats': reversed(monthly_stats),
            'top_categories': Category.objects.annotate(
                borrow_count=Count('books__borrow_records')
            ).order_by('-borrow_count')[:10],
            'user_activity': User.objects.annotate(
                total_borrows=Count('borrow_records'),
                active_borrows=Count('borrow_records', filter=Q(borrow_records__status='active'))
            ).order_by('-total_borrows')[:20],
            'book_condition_stats': Book.objects.values('condition').annotate(
                count=Count('id')
            ).order_by('condition'),
        })
        
        return context

# books/views.py
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView

@method_decorator(login_required, name='dispatch')
class WishlistView(ListView):
    template_name = 'books/wishlist.html'
    context_object_name = 'wishlist_items'
    
    def get_queryset(self):
        # Return user's wishlist items with related books
        return Wishlist.objects.filter(
            user=self.request.user
        ).select_related('book').order_by('priority', '-added_date')

@method_decorator(login_required, name='dispatch')
class MyBorrowsView(ListView):
    template_name = 'books/my_borrows.html'
    context_object_name = 'borrowed_books'
    
    def get_queryset(self):
        # Return user's active borrowed books
        return BorrowRecord.objects.filter(
            user=self.request.user,
            status='active'
        ).select_related('book')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for the user
            profile = UserProfile.objects.create(user=user)
            login(request, user)  # Automatically log in the user after signup
            messages.success(request, 'Account created successfully! Please complete your profile.')
            return redirect('books:user_profile')  # Redirect to profile page to complete setup
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'books/registration/signup.html', {'form': form})

@login_required
def profile_view(request):
    """Display user profile page"""
    user = request.user
    profile = user.profile
    
    # Get user statistics
    current_borrowed = user.borrowrecord_set.filter(return_date__isnull=True).count()
    total_borrowed = user.borrowrecord_set.count()
    total_returned = user.borrowrecord_set.filter(return_date__isnull=False).count()
    wishlist_count = user.wishlist.count()
    
    # Get recent activities (last 10)
    recent_activities = user.activities.select_related('book')[:10]
    
    # Get wishlist items (top 5 by priority)
    wishlist_items = user.wishlist.select_related('book')[:5]
    
    # Get overdue books if any
    overdue_books = user.borrowrecord_set.filter(
        return_date__isnull=True,
        due_date__lt=timezone.now().date()
    ).select_related('book')
    
    context = {
        'profile': profile,
        'current_borrowed': current_borrowed,
        'total_borrowed': total_borrowed,
        'total_returned': total_returned,
        'wishlist_count': wishlist_count,
        'recent_activities': recent_activities,
        'wishlist_items': wishlist_items,
        'overdue_books': overdue_books,
        'total_fines': profile.current_fines,
    }
    
    return render(request, 'profile.html', context)


@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """Update user profile information"""
    user = request.user
    profile = user.profile
    
    try:
        # Update User model fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Update UserProfile fields
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        
        if profile.user_type == 'student':
            profile.student_id = request.POST.get('student_id', profile.student_id)
        else:
            profile.employee_id = request.POST.get('employee_id', profile.employee_id)
        
        profile.department = request.POST.get('department', profile.department)
        profile.save()
        
        # Log activity
        UserActivity.log_activity(
            user=user,
            activity_type='profile_update',
            description='Profile information updated'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating profile: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["POST"])
def update_avatar(request):
    """Update user profile avatar"""
    if 'avatar' not in request.FILES:
        return JsonResponse({
            'success': False,
            'message': 'No image file provided'
        }, status=400)
    
    try:
        profile = request.user.profile
        
        # Delete old avatar if it's not the default
        if profile.avatar and profile.avatar.name != 'avatars/default.png':
            if os.path.isfile(profile.avatar.path):
                os.remove(profile.avatar.path)
        
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        # Log activity
        UserActivity.log_activity(
            user=request.user,
            activity_type='profile_update',
            description='Profile picture updated'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Profile picture updated successfully!',
            'avatar_url': profile.avatar.url
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating avatar: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["POST"])
def change_password(request):
    """Change user password"""
    form = PasswordChangeForm(request.user, request.POST)
    
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # Keep user logged in
        
        # Log activity
        UserActivity.log_activity(
            user=user,
            activity_type='password_change',
            description='Password changed successfully'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully!'
        })
    else:
        errors = []
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"{field}: {error}")
        
        return JsonResponse({
            'success': False,
            'message': '; '.join(errors)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def update_notification_settings(request):
    """Update user notification preferences"""
    try:
        profile = request.user.profile
        data = json.loads(request.body)
        
        profile.email_notifications = data.get('email_notifications', profile.email_notifications)
        profile.sms_notifications = data.get('sms_notifications', profile.sms_notifications)
        profile.public_profile = data.get('public_profile', profile.public_profile)
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification settings updated!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating settings: {str(e)}'
        }, status=400)


@login_required
def delete_account(request):
    """Delete user account (soft delete - deactivate)"""
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        
        if confirmation != 'DELETE':
            return JsonResponse({
                'success': False,
                'message': 'Please type "DELETE" to confirm account deletion'
            }, status=400)
        
        try:
            user = request.user
            
            # Check for active borrowed books
            active_borrows = user.borrowrecord_set.filter(return_date__isnull=True).count()
            if active_borrows > 0:
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot delete account. You have {active_borrows} books currently borrowed.'
                }, status=400)
            
            # Check for unpaid fines
            if user.profile.current_fines > 0:
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot delete account. You have ${user.profile.current_fines} in unpaid fines.'
                }, status=400)
            
            # Soft delete - deactivate account
            user.is_active = False
            user.profile.is_active_member = False
            user.save()
            user.profile.save()
            
            # Log activity before deactivation
            UserActivity.log_activity(
                user=user,
                activity_type='profile_update',
                description='Account deactivated by user'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Account has been deactivated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deactivating account: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@login_required
def export_user_data(request):
    """Export user data as CSV"""
    user = request.user
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="user_data_{user.username}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # User Information
    writer.writerow(['USER INFORMATION'])
    writer.writerow(['Field', 'Value'])
    writer.writerow(['Username', user.username])
    writer.writerow(['Full Name', user.get_full_name()])
    writer.writerow(['Email', user.email])
    writer.writerow(['Phone', user.profile.phone])
    writer.writerow(['Address', user.profile.address])
    writer.writerow(['User Type', user.profile.get_user_type_display()])
    writer.writerow(['Library Card', user.profile.library_card_number])
    writer.writerow(['Member Since', user.profile.membership_date.strftime('%Y-%m-%d')])
    writer.writerow([])
    
    # Borrowing History
    writer.writerow(['BORROWING HISTORY'])
    writer.writerow(['Book Title', 'Borrow Date', 'Due Date', 'Return Date', 'Status'])
    
    borrow_records = user.borrowrecord_set.select_related('book').order_by('-borrow_date')
    for record in borrow_records:
        status = 'Returned' if record.return_date else ('Overdue' if record.due_date < timezone.now().date() else 'Active')
        writer.writerow([
            record.book.title,
            record.borrow_date.strftime('%Y-%m-%d'),
            record.due_date.strftime('%Y-%m-%d'),
            record.return_date.strftime('%Y-%m-%d') if record.return_date else '',
            status
        ])
    
    writer.writerow([])
    
    # Wishlist
    writer.writerow(['WISHLIST'])
    writer.writerow(['Book Title', 'Author', 'Added Date', 'Priority'])
    
    wishlist_items = user.wishlist.select_related('book').order_by('-added_date')
    for item in wishlist_items:
        priority_map = {1: 'High', 2: 'Medium', 3: 'Low'}
        writer.writerow([
            item.book.title,
            item.book.author,
            item.added_date.strftime('%Y-%m-%d'),
            priority_map.get(item.priority, 'Unknown')
        ])
    
    writer.writerow([])
    
    # Recent Activities
    writer.writerow(['RECENT ACTIVITIES'])
    writer.writerow(['Activity', 'Description', 'Date'])
    
    activities = user.activities.order_by('-timestamp')[:50]  # Last 50 activities
    for activity in activities:
        writer.writerow([
            activity.get_activity_type_display(),
            activity.description,
            activity.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@login_required
def get_user_activities(request):
    """Get paginated user activities for AJAX requests"""
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10)
    
    activities = request.user.activities.select_related('book').order_by('-timestamp')
    paginator = Paginator(activities, per_page)
    page_obj = paginator.get_page(page)
    
    activities_data = []
    for activity in page_obj:
        activities_data.append({
            'type': activity.get_activity_type_display(),
            'description': activity.description,
            'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'book_title': activity.book.title if activity.book else None,
        })
    
    return JsonResponse({
        'activities': activities_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })
