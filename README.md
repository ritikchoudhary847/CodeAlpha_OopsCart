# OopsCart — Modern Django E-Commerce Platform

OopsCart is a full-stack e-commerce web application built with Django, Python, HTML, CSS and JavaScript. It provides a complete shopping workflow, including product discovery, user authentication, shopping cart management and order placement.

## Features

### User Authentication
- User registration and login
- Secure password validation
- User profile management
- Profile avatar uploads
- Guest cart merging after login

### Product Catalogue
- Product categories
- Product detail pages
- Product search
- Category-based filtering
- Price and name sorting
- Featured products
- Product stock management
- Product image validation

### Shopping Cart
- Add products to cart
- Update item quantities
- Remove cart items
- Guest and authenticated shopping carts
- Stock-aware quantity validation
- Automatic cart summary

### Order Management
- Checkout with customer details
- Cash on Delivery payment option
- Order confirmation
- Order history
- Order and item snapshots
- Stock deduction after successful order placement
- Transaction-based order processing

### Administration
- Django admin integration
- Product and category management
- Inventory management
- Order management

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| SQLite | Database |
| HTML5 | Page structure |
| CSS3 | Styling and responsive layouts |
| JavaScript | Frontend interactions |
| Pillow | Image processing |

## Project Structure

```text
OopsCart/
│
├── accounts/          # Authentication and user profiles
├── cart/              # Shopping cart functionality
├── config/            # Django project configuration
├── media/             # User-uploaded media (not committed)
├── orders/            # Checkout and order management
├── static/            # CSS, JavaScript and static assets
├── store/             # Products, categories and catalogue
├── templates/         # Django HTML templates
│
├── .env.example       # Environment variable reference
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd OopsCart
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Apply database migrations

```powershell
python manage.py migrate
```

### 5. Create an administrator account

```powershell
python manage.py createsuperuser
```

### 6. Populate the product catalogue

```powershell
python manage.py seed_products
```

To populate products without downloading images:

```powershell
python manage.py seed_products --skip-images
```

### 7. Start the development server

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Environment Configuration

Refer to `.env.example` for the production environment variable names.

Configure the actual environment variables through your hosting provider. The example file is a reference and is not automatically loaded by the current Django settings.

Never commit production secret keys, private environment files or user-uploaded media.

## Testing

Run the complete Django test suite:

```powershell
python manage.py test
```

Run Django system checks:

```powershell
python manage.py check
```

Check deployment security configuration:

```powershell
python manage.py check --deploy
```

## Security Considerations

- Django authentication and password validation
- CSRF protection
- Secure session cookie configuration in production
- Product and avatar image validation
- Server-side stock validation
- Ownership checks for customer orders
- Environment-based production secrets
- Production HTTPS security settings

## Project Status

The project has passed **49 automated Django tests** in the development environment.

The test suite covers the accounts, store, cart and orders applications.

## Developer

Developed as part of the CodeAlpha Full Stack Development Internship.

**Project:** OopsCart  
**Domain:** Full Stack Web Development  
**Backend:** Python and Django

---

*OopsCart — A complete shopping experience built with Django.*
