from django.urls import path, include
from django.views.generic import RedirectView
from . import views

app_name = 'books'

urlpatterns = [
    # ==================== HOME AND DASHBOARD ====================
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('librarian/', views.LibrarianDashboardView.as_view(), name='librarian_dashboard'),
    
    # ==================== BOOK URLS ====================
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_edit'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    
    # Book Actions
    path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('books/<int:book_id>/reserve/', views.reserve_book, name='reserve_book'),
    path('books/<int:book_id>/add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('books/<int:book_id>/remove-from-wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('books/<int:book_id>/add-review/', views.add_review, name='add_review'),
    path('books/<int:book_id>/barcode/', views.generate_barcode, name='generate_barcode'),
    path('books/bulk-actions/', views.bulk_book_actions, name='bulk_book_actions'),
    
    # ==================== CATEGORY URLS ====================
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),  # Alternative URL
    
    # ==================== AUTHOR URLS ====================
    path('authors/', views.AuthorListView.as_view(), name='author_list'),
    path('authors/create/', views.AuthorCreateView.as_view(), name='author_create'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    
    # ==================== BORROWING URLS ====================
    path('borrows/', views.BorrowListView.as_view(), name='borrow_list'),
    path('borrows/<int:borrow_id>/return/', views.return_book, name='return_book'),
    path('borrows/<int:borrow_id>/renew/', views.renew_book, name='renew_book'),
    
    # ==================== RESERVATION URLS ====================
    path('reservations/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    
    # ==================== REVIEW URLS ====================
    path('reviews/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    
    # ==================== WISHLIST URLS ====================
    path('wishlist/', views.wishlist_view, name='wishlist'),
    #------------------------my borrows urls------------------
    #path('my-borrows/', views.my_borrows_view, name='my_borrows'),

    # ==================== READING LIST URLS ====================
    path('reading-lists/', views.reading_lists_view, name='reading_lists'),
    path('reading-lists/create/', views.ReadingListCreateView.as_view(), name='reading_list_create'),
    path('reading-lists/<int:list_id>/', views.reading_list_detail, name='reading_list_detail'),
    
    # ==================== SEARCH URLS ====================
    path('search/', views.BookListView.as_view(), name='search'),
    path('search/advanced/', views.AdvancedSearchView.as_view(), name='advanced_search'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # ==================== USER PROFILE URLS ====================
    path('profile/', views.user_profile, name='user_profile'),
    
    # ==================== NOTIFICATION URLS ====================
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    
    # ==================== ADMIN/LIBRARIAN URLS ====================
    path('admin/reports/', views.ReportsView.as_view(), name='reports'),
    path('admin/stats/', views.LibraryStatsView.as_view(), name='library_stats'),
    path('admin/settings/', views.library_settings, name='library_settings'),
    path('admin/send-overdue-notifications/', views.send_overdue_notifications, name='send_overdue_notifications'),
    path('admin/export/', views.export_data, name='export_data'),
    
    # ==================== API ENDPOINTS ====================
    #path('api/books/search/', views.api_book_search, name='api_book_search'),
    #path('api/users/search/', views.api_user_search, name='api_user_search'),
    #path('api/books/<int:book_id>/availability/', views.book_availability_check, name='book_availability_check'),
    
    # ==================== GENRE URLS ====================
    path('genres/', views.CategoryListView.as_view(), name='genre_list'),  # Using CategoryListView for genres
    path('genres/<slug:slug>/', views.CategoryDetailView.as_view(), name='genre_detail'),
    
    # ==================== PUBLISHER URLS ====================
    path('publishers/', RedirectView.as_view(pattern_name='books:book_list'), name='publisher_list'),
    
    # ==================== ADDITIONAL UTILITY URLS ====================
    # Redirect common search patterns
    path('find/', RedirectView.as_view(pattern_name='books:search'), name='find'),
    path('browse/', RedirectView.as_view(pattern_name='books:book_list'), name='browse'),
    path('catalog/', RedirectView.as_view(pattern_name='books:book_list'), name='catalog'),
    
    # Quick access URLs
    path('new-arrivals/', views.BookListView.as_view(), {'filter': 'new_arrivals'}, name='new_arrivals'),
    path('featured/', views.BookListView.as_view(), {'filter': 'featured'}, name='featured_books'),
    path('bestsellers/', views.BookListView.as_view(), {'filter': 'bestsellers'}, name='bestsellers'),
    path('available/', views.BookListView.as_view(), {'filter': 'available'}, name='available_books'),
    
    # Language-specific book lists
    path('books/english/', views.BookListView.as_view(), {'language': 'en'}, name='english_books'),
    path('books/spanish/', views.BookListView.as_view(), {'language': 'es'}, name='spanish_books'),
    path('books/french/', views.BookListView.as_view(), {'language': 'fr'}, name='french_books'),
    
    # ==================== MOBILE/AJAX FRIENDLY URLS ====================
    path('mobile/', views.HomeView.as_view(), {'mobile': True}, name='mobile_home'),
    path('mobile/books/', views.BookListView.as_view(), {'mobile': True}, name='mobile_book_list'),
    path('mobile/search/', views.BookListView.as_view(), {'mobile': True}, name='mobile_search'),
    
]

# Additional URL patterns for specific book formats/types
book_type_patterns = [
    path('ebooks/', views.BookListView.as_view(), {'book_type': 'ebook'}, name='ebooks'),
    path('audiobooks/', views.BookListView.as_view(), {'book_type': 'audiobook'}, name='audiobooks'),
    path('magazines/', views.BookListView.as_view(), {'book_type': 'magazine'}, name='magazines'),
    path('journals/', views.BookListView.as_view(), {'book_type': 'journal'}, name='journals'),
]

# Category-specific URL patterns (can be dynamically generated)
category_patterns = [
    path('fiction/', views.CategoryDetailView.as_view(), {'slug': 'fiction'}, name='fiction_books'),
    path('non-fiction/', views.CategoryDetailView.as_view(), {'slug': 'non-fiction'}, name='non_fiction_books'),
    path('science/', views.CategoryDetailView.as_view(), {'slug': 'science'}, name='science_books'),
    path('history/', views.CategoryDetailView.as_view(), {'slug': 'history'}, name='history_books'),
    path('biography/', views.CategoryDetailView.as_view(), {'slug': 'biography'}, name='biography_books'),
    path('technology/', views.CategoryDetailView.as_view(), {'slug': 'technology'}, name='technology_books'),
    path('literature/', views.CategoryDetailView.as_view(), {'slug': 'literature'}, name='literature_books'),
    path('children/', views.CategoryDetailView.as_view(), {'slug': 'children'}, name='children_books'),
    path('young-adult/', views.CategoryDetailView.as_view(), {'slug': 'young-adult'}, name='young_adult_books'),
    path('mystery/', views.CategoryDetailView.as_view(), {'slug': 'mystery'}, name='mystery_books'),
    path('romance/', views.CategoryDetailView.as_view(), {'slug': 'romance'}, name='romance_books'),
    path('fantasy/', views.CategoryDetailView.as_view(), {'slug': 'fantasy'}, name='fantasy_books'),
    path('science-fiction/', views.CategoryDetailView.as_view(), {'slug': 'science-fiction'}, name='sci_fi_books'),
]

# User action patterns
user_action_patterns = [
    path('my-books/', views.DashboardView.as_view(), name='my_books'),
    path('my-borrows/', views.DashboardView.as_view(), {'section': 'borrows'}, name='my_borrows'),
    path('my-reservations/', views.DashboardView.as_view(), {'section': 'reservations'}, name='my_reservations'),
    path('my-reviews/', views.DashboardView.as_view(), {'section': 'reviews'}, name='my_reviews'),
    path('my-history/', views.user_profile, name='my_history'),
]

# Quick action patterns for librarians
librarian_patterns = [
    path('quick-borrow/', views.borrow_book, name='quick_borrow'),
    path('quick-return/', views.return_book, name='quick_return'),
    path('overdue-books/', views.BorrowListView.as_view(), {'status': 'overdue'}, name='overdue_books'),
    path('active-borrows/', views.BorrowListView.as_view(), {'status': 'active'}, name='active_borrows'),
    path('returned-books/', views.BorrowListView.as_view(), {'status': 'returned'}, name='returned_books'),
]

# Extend main urlpatterns with additional patterns
urlpatterns.extend(book_type_patterns)
urlpatterns.extend(category_patterns)
urlpatterns.extend(user_action_patterns)
urlpatterns.extend(librarian_patterns)

# REST API style URLs (optional, for future API expansion)
api_v1_patterns = [
    path('api/v1/books/', views.api_book_search, name='api_v1_books'),
    path('api/v1/books/<int:book_id>/', views.book_availability_check, name='api_v1_book_detail'),
    path('api/v1/users/', views.api_user_search, name='api_v1_users'),
    path('api/v1/categories/', views.CategoryListView.as_view(), name='api_v1_categories'),
]

urlpatterns.extend(api_v1_patterns)

# Error handling URLs (these would typically be in main project urls.py)
error_patterns = [
    path('404/', views.handler404, name='404'),
    path('500/', views.handler500, name='500'),
]

# Development/debugging URLs (only include in DEBUG mode)
debug_patterns = [
    path('debug/stats/', views.LibraryStatsView.as_view(), name='debug_stats'),
    path('debug/test-notifications/', views.send_overdue_notifications, name='debug_notifications'),
]

# Include debug patterns conditionally
import django.conf
if getattr(django.conf.settings, 'DEBUG', False):
    urlpatterns.extend(debug_patterns)

# URL patterns for different views of the same data
alternative_patterns = [
    # Alternative book list views
    path('library/', views.BookListView.as_view(), name='library'),
    path('collection/', views.BookListView.as_view(), name='collection'),
    path('inventory/', views.BookListView.as_view(), name='inventory'),
    
    # Alternative search URLs
    path('find-books/', views.BookListView.as_view(), name='find_books'),
    path('book-search/', views.BookListView.as_view(), name='book_search'),
    
    # Alternative category URLs
    path('subjects/', views.CategoryListView.as_view(), name='subjects'),
    path('topics/', views.CategoryListView.as_view(), name='topics'),
    
    # Alternative author URLs  
    path('writers/', views.AuthorListView.as_view(), name='writers'),
    
    # Alternative dashboard URLs
    path('account/', views.DashboardView.as_view(), name='account'),
    path('my-account/', views.DashboardView.as_view(), name='my_account'),
]

urlpatterns.extend(alternative_patterns)

# Sorting and filtering URL patterns
filter_patterns = [
    # Sort by different criteria
    path('books/popular/', views.BookListView.as_view(), {'sort': 'popular'}, name='popular_books'),
    path('books/recent/', views.BookListView.as_view(), {'sort': 'recent'}, name='recent_books'),
    path('books/alphabetical/', views.BookListView.as_view(), {'sort': 'title'}, name='books_alphabetical'),
    path('books/by-author/', views.BookListView.as_view(), {'sort': 'author'}, name='books_by_author'),
    
    # Filter by availability
    path('books/borrowed/', views.BookListView.as_view(), {'availability': 'borrowed'}, name='borrowed_books'),
    path('books/reserved/', views.BookListView.as_view(), {'availability': 'reserved'}, name='reserved_books'),
    
    # Filter by condition
    path('books/excellent/', views.BookListView.as_view(), {'condition': 'excellent'}, name='excellent_books'),
    path('books/good/', views.BookListView.as_view(), {'condition': 'good'}, name='good_books'),
    path('books/damaged/', views.BookListView.as_view(), {'condition': 'damaged'}, name='damaged_books'),
]

urlpatterns.extend(filter_patterns)

# SEO-friendly URLs for common searches
seo_patterns = [
    path('best-books/', views.BookListView.as_view(), {'featured': True}, name='best_books'),
    path('new-books/', views.BookListView.as_view(), {'new_arrivals': True}, name='new_books'),
    path('top-rated/', views.BookListView.as_view(), {'sort': 'rating'}, name='top_rated_books'),
    path('most-borrowed/', views.BookListView.as_view(), {'sort': 'borrow_count'}, name='most_borrowed_books'),
]

urlpatterns.extend(seo_patterns)


#wishlist urls and borrow list urls
urlpatterns += [
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('my-borrows/', views.MyBorrowsView.as_view(), name='my_borrows'),
]



# Authentication URLs
urlpatterns += [
    path('registration/', include('django.contrib.auth.urls')),  # Django's built-in auth URLs
    path('registration/signup/', views.signup_view, name='signup'),  # Signup URL should be at root level
]