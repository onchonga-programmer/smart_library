from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from .models import (
    Category, Author, Publisher, Book, BorrowRecord, 
    Reservation, Review, Wishlist, ReadingList, ReadingListItem,
    BookHistory, Genre, BookCondition, Notification
)


class CategoryForm(forms.ModelForm):
    """Form for creating and editing book categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'parent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional category description'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '📚 or icon class'
            }),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude self from parent choices to prevent circular references
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk)


class AuthorForm(forms.ModelForm):
    """Form for creating and editing authors"""
    
    class Meta:
        model = Author
        fields = [
            'first_name', 'last_name', 'bio', 'birth_date', 'death_date',
            'nationality', 'photo', 'website', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Author biography'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'death_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nationality'
            }),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        death_date = cleaned_data.get('death_date')
        
        if birth_date and death_date and birth_date >= death_date:
            raise ValidationError("Death date must be after birth date.")
        
        return cleaned_data


class PublisherForm(forms.ModelForm):
    """Form for creating and editing publishers"""
    
    class Meta:
        model = Publisher
        fields = ['name', 'address', 'website', 'email', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publisher name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Publisher address'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@publisher.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class BookForm(forms.ModelForm):
    """Form for creating and editing books"""
    
    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'authors', 'category', 'publisher',
            'isbn_10', 'isbn_13', 'publication_date', 'edition', 'pages',
            'language', 'description', 'table_of_contents', 'cover_image',
            'condition', 'location', 'total_copies', 'available_copies',
            'is_active', 'is_featured', 'is_bestseller', 'is_new_arrival',
            'allow_reservation', 'price', 'late_fee_per_day'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book title'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subtitle (optional)'
            }),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'publisher': forms.Select(attrs={'class': 'form-control'}),
            'isbn_10': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit ISBN'
            }),
            'isbn_13': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '13-digit ISBN'
            }),
            'publication_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'edition': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1st Edition'
            }),
            'pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Book description'
            }),
            'table_of_contents': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Table of contents (optional)'
            }),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A-1-001'
            }),
            'total_copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'available_copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'late_fee_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_bestseller': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new_arrival': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_reservation': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        total_copies = cleaned_data.get('total_copies')
        available_copies = cleaned_data.get('available_copies')
        
        if total_copies and available_copies and available_copies > total_copies:
            raise ValidationError("Available copies cannot exceed total copies.")
        
        return cleaned_data


class BorrowRecordForm(forms.ModelForm):
    """Form for creating and editing borrow records"""
    
    class Meta:
        model = BorrowRecord
        fields = ['user', 'book', 'due_date', 'status', 'notes']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'book': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available books for new borrows
        if not self.instance.pk:
            self.fields['book'].queryset = Book.objects.filter(
                is_active=True, available_copies__gt=0
            )


class ReturnBookForm(forms.Form):
    """Form for processing book returns"""
    condition = forms.ChoiceField(
        choices=Book.CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Current condition of the returned book"
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any damage or notes about the return'
        })
    )


class RenewBookForm(forms.Form):
    """Form for renewing borrowed books"""
    renewal_days = forms.IntegerField(
        initial=14,
        min_value=1,
        max_value=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of days to extend'
        })
    )
    
    def __init__(self, borrow_record, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.borrow_record = borrow_record
    
    def clean(self):
        cleaned_data = super().clean()
        if self.borrow_record.renewed_count >= 3:
            raise ValidationError("Maximum renewal limit (3) has been reached.")
        return cleaned_data


class ReservationForm(forms.ModelForm):
    """Form for creating book reservations"""
    
    class Meta:
        model = Reservation
        fields = ['book']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'})
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Only show books that are not available
        self.fields['book'].queryset = Book.objects.filter(
            is_active=True, available_copies=0, allow_reservation=True
        )
    
    def clean_book(self):
        book = self.cleaned_data['book']
        # Check if user already has this book reserved
        if Reservation.objects.filter(user=self.user, book=book, is_active=True).exists():
            raise ValidationError("You already have an active reservation for this book.")
        return book


class ReviewForm(forms.ModelForm):
    """Form for creating and editing book reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title (optional)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts about this book...'
            })
        }


class WishlistForm(forms.ModelForm):
    """Form for adding books to wishlist"""
    
    class Meta:
        model = Wishlist
        fields = ['book', 'priority', 'notes']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(
                choices=[(i, f'Priority {i}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes'
            })
        }


class ReadingListForm(forms.ModelForm):
    """Form for creating and editing reading lists"""
    
    class Meta:
        model = ReadingList
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reading list name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of your reading list'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class ReadingListItemForm(forms.ModelForm):
    """Form for adding items to reading lists"""
    
    class Meta:
        model = ReadingListItem
        fields = ['book', 'order', 'notes']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes'
            })
        }


class GenreForm(forms.ModelForm):
    """Form for creating and editing genres"""
    
    class Meta:
        model = Genre
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Genre name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Genre description'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class BookConditionForm(forms.ModelForm):
    """Form for updating book condition"""
    
    class Meta:
        model = BookCondition
        fields = ['condition', 'notes']
        widgets = {
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Details about condition change'
            })
        }


class BookSearchForm(forms.Form):
    """Form for searching books"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, author, ISBN...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    author = forms.ModelChoiceField(
        queryset=Author.objects.filter(is_active=True),
        required=False,
        empty_label="All Authors",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    language = forms.ChoiceField(
        choices=[('', 'All Languages')] + Book.LANGUAGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    availability = forms.ChoiceField(
        choices=[
            ('', 'All Books'),
            ('available', 'Available Only'),
            ('borrowed', 'Currently Borrowed')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class NotificationForm(forms.ModelForm):
    """Form for creating notifications (admin use)"""
    
    class Meta:
        model = Notification
        fields = ['user', 'type', 'title', 'message', 'book']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Notification title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notification message'
            }),
            'book': forms.Select(attrs={'class': 'form-control'})
        }


class BulkBookActionForm(forms.Form):
    """Form for bulk actions on books"""
    ACTION_CHOICES = [
        ('', 'Select Action'),
        ('activate', 'Activate Selected Books'),
        ('deactivate', 'Deactivate Selected Books'),
        ('mark_featured', 'Mark as Featured'),
        ('unmark_featured', 'Remove Featured Status'),
        ('update_condition', 'Update Condition'),
        ('delete', 'Delete Selected Books'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Optional fields for specific actions
    new_condition = forms.ChoiceField(
        choices=Book.CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class LibrarySettingsForm(forms.Form):
    """Form for library-wide settings"""
    default_borrow_period = forms.IntegerField(
        initial=14,
        min_value=1,
        max_value=90,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Default borrowing period in days"
    )
    max_renewals = forms.IntegerField(
        initial=3,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Maximum number of renewals allowed"
    )
    max_books_per_user = forms.IntegerField(
        initial=5,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Maximum books a user can borrow at once"
    )
    default_late_fee = forms.DecimalField(
        initial=0.50,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        }),
        help_text="Default late fee per day"
    )
    send_due_date_reminders = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Send email reminders before due dates"
    )
    reminder_days_before = forms.IntegerField(
        initial=3,
        min_value=1,
        max_value=14,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Days before due date to send reminder"
    )
    #0hhfhvdnjvs
class CustomUserCreationForm(forms.ModelForm):
    """Form for user registration"""
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter a strong password"
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Re-enter your password"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'})
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        
        return user   
class ContactForm(forms.Form):
    """Form for user contact messages"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Your Name'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Your Email'
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Subject'
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        label='Message'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('message'):
            raise ValidationError("Message cannot be empty.")
        
        return cleaned_data     