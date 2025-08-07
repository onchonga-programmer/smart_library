# Library Management System

A comprehensive Django-based library management system that provides digital solutions for managing books, users, borrowing, reservations, and library operations.

## 🚀 Features

### 📚 Book Management
- **Comprehensive Catalog**: Add, edit, delete, and view books with detailed information
- **Categories & Genres**: Organize books by fiction, non-fiction, science, mystery, romance, fantasy, and more
- **Author Management**: Track and manage author information
- **Advanced Search**: Search books by title, author, category, or keywords
- **Book Actions**: Borrow, reserve, add to wishlist, and review books
- **Barcode Generation**: Generate barcodes for physical book tracking

### 👥 User Management
- **User Authentication**: Secure login, logout, and user registration
- **User Profiles**: Personalized user profiles with borrowing history
- **Role-based Access**: Different access levels for users and librarians
- **Dashboard**: Personalized dashboard showing user activity

### 📖 Borrowing System
- **Book Borrowing**: Users can borrow available books
- **Return Management**: Track and process book returns
- **Renewal System**: Extend borrowing periods when possible
- **Overdue Tracking**: Monitor and manage overdue books
- **Borrowing History**: Complete history of user borrowing activities

### 🔖 Advanced Features
- **Reservation System**: Reserve books that are currently borrowed
- **Wishlist**: Save favorite books for future reference
- **Reading Lists**: Create and manage custom reading lists
- **Book Reviews**: Rate and review books
- **Notifications**: Stay updated with library activities
- **Mobile Responsive**: Optimized for all device types

### 📊 Administrative Features
- **Reports & Analytics**: Comprehensive library statistics and reports
- **Bulk Operations**: Perform bulk actions on books and users
- **Library Settings**: Configure system-wide library settings
- **Export Data**: Export library data for external use
- **Overdue Notifications**: Automated notification system

## 🛠️ Technology Stack

- **Backend**: Django 4.x
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Django's built-in authentication system
- **Styling**: Custom CSS with Font Awesome icons
- **Fonts**: Google Fonts (Inter)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd library-management-system
```

### Step 2: Create Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic
```

### Step 7: Run the Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## 🗂️ Project Structure

```
library-management-system/
├── books/                      # Main books application
│   ├── migrations/            # Database migrations
│   ├── templates/             # HTML templates
│   ├── static/               # Static files (CSS, JS, images)
│   ├── models.py             # Database models
│   ├── views.py              # View functions and classes
│   ├── urls.py               # URL patterns
│   ├── forms.py              # Django forms
│   └── admin.py              # Admin configuration
├── library/                   # Main project directory
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
├── templates/                 # Global templates
├── static/                   # Global static files
├── media/                    # User uploaded files
├── requirements.txt          # Python dependencies
└── manage.py                 # Django management script
```

## 📱 Usage

### For Users
1. **Registration**: Create a new account using the signup form
2. **Browse Books**: Explore the book catalog and search for specific titles
3. **Borrow Books**: Click on a book and select "Borrow" if available
4. **Manage Account**: View your dashboard to see borrowed books, reservations, and wishlist
5. **Return Books**: Use the return option when you're done reading

### For Librarians
1. **Admin Access**: Login with librarian credentials
2. **Book Management**: Add, edit, or remove books from the catalog
3. **User Management**: Monitor user activities and borrowing patterns
4. **Reports**: Generate reports on library usage and book popularity
5. **System Settings**: Configure library policies and settings

## 🎯 Key URL Patterns

### Public URLs
- `/` - Home page
- `/books/` - Book catalog
- `/books/registration/login/` - User login
- `/books/registration/signup/` - User registration
- `/books/search/` - Search books

### User Dashboard URLs
- `/books/dashboard/` - User dashboard
- `/books/wishlist/` - User wishlist
- `/books/my-borrows/` - User's borrowed books
- `/books/profile/` - User profile

### Book-specific URLs
- `/books/<id>/` - Book details
- `/books/<id>/borrow/` - Borrow a book
- `/books/<id>/reserve/` - Reserve a book
- `/books/<id>/add-review/` - Add book review

### Administrative URLs
- `/books/librarian/` - Librarian dashboard
- `/books/admin/reports/` - Library reports
- `/books/admin/stats/` - Library statistics

## 🔧 Configuration

### Settings Configuration
Key settings to configure in `settings.py`:

```python
# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Environment Variables
Create a `.env` file for sensitive information:
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=your-database-url
```

## 🎨 Customization

### Styling
- Custom CSS is located in `books/static/books/css/style.css`
- The design uses a modern, responsive layout
- Font Awesome icons are integrated for better UX
- Google Fonts (Inter) provides clean typography

### Templates
- Base template: `books/templates/base.html`
- All templates extend the base template for consistency
- Mobile-responsive design ensures compatibility across devices

## 🚦 API Endpoints (Future Enhancement)

The system includes placeholder API endpoints for future expansion:
- `/books/api/v1/books/` - Book API
- `/books/api/v1/users/` - User API
- `/books/api/v1/categories/` - Category API

## 🔒 Security Features

- CSRF protection on all forms
- User authentication and authorization
- Session management
- XSS protection
- SQL injection prevention through Django ORM

## 📈 Performance Optimizations

- Database query optimization
- Static file compression
- Template caching
- Lazy loading for images
- Efficient pagination

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 🚀 Deployment

### Production Setup
1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email settings for notifications
5. Set up proper logging
6. Use environment variables for sensitive data

### Recommended Deployment Platforms
- **Heroku**: Easy deployment with PostgreSQL addon
- **DigitalOcean**: VPS with more control
- **AWS**: Scalable cloud deployment
- **PythonAnywhere**: Beginner-friendly hosting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request


## 📞 Support

For support and questions:
- Create an issue in the GitHub repository


## 🏆 Acknowledgments

- Django framework for the robust backend
- Font Awesome for icons
- Google Fonts for typography
- Bootstrap inspiration for responsive design
- Open source community for various tools and libraries

---

**Built with ❤️ using Django**

