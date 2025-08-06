from django.db import models

# Create your models here.
"""
Books app models for the GreenLeaf Library System
"""
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image
import os
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator


class Category(models.Model):
    """Book categories/genres"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📚', help_text='Emoji or icon class')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('books:category', kwargs={'slug': self.slug})
    
    @property
    def book_count(self):
        return self.books.filter(is_active=True).count()


class Author(models.Model):
    """Book authors"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True, null=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = ['first_name', 'last_name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.first_name}-{self.last_name}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def book_count(self):
        return self.books.filter(is_active=True).count()
    
    def get_absolute_url(self):
        return reverse('books:author_detail', kwargs={'pk': self.pk})


class Publisher(models.Model):
    """Book publishers"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """Main book model"""
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ar', 'Arabic'),
        ('hi', 'Hindi'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    authors = models.ManyToManyField(Author, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Publication Details
    isbn_10 = models.CharField(max_length=10, blank=True, unique=True, null=True)
    isbn_13 = models.CharField(max_length=13, blank=True, unique=True, null=True)
    publication_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=100, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    
    # Content
    description = models.TextField(blank=True)
    table_of_contents = models.TextField(blank=True)
    
    # Physical Details
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    location = models.CharField(max_length=100, blank=True, help_text='Physical location in library')
    barcode = models.CharField(max_length=50, unique=True, blank=True)
    
    # Inventory
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    
    # Status and Settings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    allow_reservation = models.BooleanField(default=True)
    
    # Pricing (if library charges fees)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    late_fee_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=0.50)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='books_added')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn_13']),
            models.Index(fields=['isbn_10']),
            models.Index(fields=['is_active', 'available_copies']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.barcode:
            self.barcode = str(uuid.uuid4())[:12].upper()
        
        # Ensure available copies doesn't exceed total copies
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
            
        super().save(*args, **kwargs)
        
        # Resize cover image
        if self.cover_image:
            self.resize_image()
    
    def resize_image(self):
        """Resize cover image to standard size"""
        try:
            with Image.open(self.cover_image.path) as img:
                if img.height > 400 or img.width > 300:
                    output_size = (300, 400)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.cover_image.path, quality=85, optimize=True)
        except Exception:
            pass  # Handle errors silently
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('books:detail', kwargs={'pk': self.pk})
    
    @property
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.is_active and self.available_copies > 0
    
    @property
    def authors_list(self):
        """Get comma-separated list of authors"""
        return ", ".join([str(author) for author in self.authors.all()])
    
    @property
    def borrowed_copies(self):
        """Number of currently borrowed copies"""
        return self.total_copies - self.available_copies
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    @property
    def rating_count(self):
        """Number of ratings/reviews"""
        return self.reviews.filter(is_approved=True).count()
    
    @property
    def borrow_count(self):
        """Total number of times this book has been borrowed"""
        return self.borrow_records.count()
    
    def get_due_date(self, borrow_period_days=14):
        """Calculate due date for borrowing"""
        return timezone.now().date() + timezone.timedelta(days=borrow_period_days)


class BorrowRecord(models.Model):
    """Track book borrowing and returns"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateTimeField(null=True, blank=True)
    renewed_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    librarian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_borrows')
    
    class Meta:
        ordering = ['-borrow_date']
        unique_together = ['user', 'book', 'borrow_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
    
    @property
    def is_overdue(self):
        """Check if book is overdue"""
        if self.status == 'returned':
            return False
        return timezone.now().date() > self.due_date
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days
    
    @property
    def calculated_late_fee(self):
        """Calculate late fee based on days overdue"""
        if not self.is_overdue:
            return 0
        return self.days_overdue * self.book.late_fee_per_day
    
    def return_book(self):
        """Mark book as returned and update availability"""
        self.return_date = timezone.now()
        self.status = 'returned'
        self.late_fee = self.calculated_late_fee
        self.save()
        
        # Update book availability
        self.book.available_copies += 1
        self.book.save()
    
    def renew(self, days=14):
        """Renew the book for additional days"""
        if self.renewed_count < 3:  # Maximum 3 renewals
            self.due_date += timezone.timedelta(days=days)
            self.renewed_count += 1
            self.save()
            return True
        return False


class Reservation(models.Model):
    """Book reservations when all copies are borrowed"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    notified = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['reservation_date']
        unique_together = ['user', 'book']
    
    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} reserved {self.book.title}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expiry_date


class Review(models.Model):
    """Book reviews and ratings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)
    helpful_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'book']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}/5)"


class Wishlist(models.Model):
    """User wishlist for books they want to read"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(default=1, help_text="1=High, 2=Medium, 3=Low")
    notes = models.TextField(blank=True, max_length=500)

    class Meta:
        db_table = 'wishlists'
        unique_together = ('user', 'book')
        ordering = ['priority', '-added_date']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class ReadingList(models.Model):
    """User-created reading lists"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_lists')
    books = models.ManyToManyField(Book, through='ReadingListItem', related_name='reading_lists')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @property
    def book_count(self):
        return self.books.count()


class ReadingListItem(models.Model):
    """Items in reading lists with order and notes"""
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'added_date']
        unique_together = ['reading_list', 'book']
    
    def __str__(self):
        return f"{self.reading_list.name} - {self.book.title}"


class BookHistory(models.Model):
    """Track changes to book records"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('reserved', 'Reserved'),
        ('damaged', 'Marked as Damaged'),
        ('lost', 'Marked as Lost'),
        ('condition_changed', 'Condition Changed'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    librarian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='book_actions')
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Book histories'
    
    def __str__(self):
        return f"{self.book.title} - {self.get_action_display()}"
    # Add these models to the end of your models.py file

class BookCondition(models.Model):
    """Track condition changes and maintenance of books"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='condition_records')
    condition = models.CharField(max_length=20, choices=Book.CONDITION_CHOICES)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.book.title} - {self.get_condition_display()}"


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('due_soon', 'Book Due Soon'),
        ('overdue', 'Book Overdue'),
        ('available', 'Reserved Book Available'),
        ('reservation_expired', 'Reservation Expired'),
        ('new_book', 'New Book Added'),
        ('review_reply', 'Review Reply'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    #creating my borrows model to track user's borrowed books


class UserProfile(models.Model):
    """Extended user profile with library-specific information"""
    
    USER_TYPES = (
        ('student', 'Student'),
        ('librarian', 'Librarian'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    address = models.TextField(blank=True, max_length=500)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # User type specific fields
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    student_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    employee_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    public_profile = models.BooleanField(default=True)
    
    # Library specific fields
    membership_date = models.DateTimeField(auto_now_add=True)
    library_card_number = models.CharField(max_length=20, unique=True, blank=True)
    max_books_allowed = models.IntegerField(default=5)
    current_fines = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active_member = models.BooleanField(default=True)
    
    # Reading preferences
    favorite_genres = models.ManyToManyField('Genre', blank=True)
    reading_goal = models.IntegerField(default=12, help_text="Books per year")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_user_type_display()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize avatar image
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

    @property
    def total_books_borrowed(self):
        """Get total number of books ever borrowed"""
        return self.user.borrowrecord_set.count()

    @property
    def books_currently_borrowed(self):
        """Get currently borrowed books count"""
        return self.user.borrowrecord_set.filter(return_date__isnull=True).count()

    @property
    def total_fines_paid(self):
        """Get total fines paid historically"""
        return self.user.fine_set.aggregate(
            total=models.Sum('amount_paid')
        )['total'] or 0

    @property
    def overdue_books_count(self):
        """Get count of overdue books"""
        from django.utils import timezone
        return self.user.borrowrecord_set.filter(
            return_date__isnull=True,
            due_date__lt=timezone.now().date()
        ).count()

    def generate_library_card_number(self):
        """Generate unique library card number"""
        if not self.library_card_number:
            prefix = 'LIB'
            year = timezone.now().year
            max_attempts = 100  # Prevent infinite loop
            attempt = 0
            
            while attempt < max_attempts:
                # Get the last card number for this year
                last_profile = UserProfile.objects.filter(
                    library_card_number__startswith=f'{prefix}{year}'
                ).order_by('library_card_number').last()
                
                if last_profile:
                    try:
                        last_number = int(last_profile.library_card_number[-4:])
                        new_number = last_number + 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                
                new_card_number = f'{prefix}{year}{new_number:04d}'
                
                # Check if this number is already taken
                if not UserProfile.objects.filter(library_card_number=new_card_number).exists():
                    self.library_card_number = new_card_number
                    break
                
                attempt += 1
            
            if attempt >= max_attempts:
                # If we couldn't generate a unique number, create a fallback
                timestamp = int(timezone.now().timestamp())
                self.library_card_number = f'{prefix}{year}{timestamp % 10000:04d}'


class Genre(models.Model):
    """Book genres (can be multiple per book)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'genres'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('books:genre', kwargs={'slug': self.slug})


class UserActivity(models.Model):
    """Track user activities for the profile dashboard"""
    
    ACTIVITY_TYPES = (
        ('borrow', 'Book Borrowed'),
        ('return', 'Book Returned'),
        ('wishlist_add', 'Added to Wishlist'),
        ('wishlist_remove', 'Removed from Wishlist'),
        ('review', 'Book Reviewed'),
        ('fine_paid', 'Fine Paid'),
        ('profile_update', 'Profile Updated'),
        ('password_change', 'Password Changed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    book = models.ForeignKey(
        'Book', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Related book if applicable"
    )
    metadata = models.JSONField(default=dict, blank=True)  # Store additional activity data
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_activities'
        ordering = ['-timestamp']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

    @classmethod
    def log_activity(cls, user, activity_type, description, book=None, **metadata):
        """Helper method to log user activities"""
        return cls.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            book=book,
            metadata=metadata
        )


class BookReview(models.Model):
    """User reviews and ratings for books"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_reviews')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='book_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review_text = models.TextField(blank=True, max_length=1000)
    is_public = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'book_reviews'
        unique_together = ('user', 'book')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}★)"


# Signal handlers to automatically create/update profiles
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                profile = UserProfile.objects.create(
                    user=instance,
                    user_type='librarian' if instance.is_staff else 'student'
                )
                profile.generate_library_card_number()
                profile.save()
                break
            except IntegrityError:
                if attempt == max_attempts - 1:
                    raise  # Re-raise the exception if all attempts failed
                continue


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        try:
            instance.profile.save()
        except IntegrityError:
            if not instance.profile.library_card_number:
                instance.profile.generate_library_card_number()
                instance.profile.save()