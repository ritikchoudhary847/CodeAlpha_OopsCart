# OopsCart | Full-Stack Django E-Commerce Platform

A modern, responsive e-commerce web application built with **Python, Django, HTML, CSS, JavaScript, and SQLite**.

OopsCart provides an end-to-end shopping experience, from product discovery and cart management to checkout and order tracking. It also includes user authentication, inventory validation, and an administrative interface.

---

## Project Overview

OopsCart is designed to demonstrate practical full-stack web development through a complete e-commerce workflow.

Users can browse products, search and filter the catalogue, manage shopping carts, and place orders using Cash on Delivery. The application also supports guest shopping and automatically merges guest cart items after login.

## Key Features

### User Authentication
- User registration, login, and logout
- Password validation
- User profile management
- Profile avatar uploads
- Guest cart merging after login

### Product Catalogue
- Product categories and featured products
- Product search and category filtering
- Price and name-based sorting
- Detailed product pages
- Product inventory management
- Product image validation

### Shopping Cart
- Add and remove products
- Update product quantities
- Automatic cart calculations
- Guest and authenticated user carts
- Stock-aware quantity validation

### Checkout and Order Management
- Customer and delivery details
- Cash on Delivery (COD)
- Order confirmation and order history
- Order and item snapshots
- Automatic stock deduction after successful order placement
- Transaction-based order processing

### Admin Dashboard
- Django Admin integration
- Product and category management
- Inventory management
- Order management

---

## Screenshots

Add your actual application screenshots to `docs/screenshots/` using the filenames below.

| Homepage | Product Discovery |
|---|---|
| ![OopsCart Homepage](docs/screenshots/homepage.png) | ![Product Discovery](docs/screenshots/product-search.png) |

| Shopping Cart |
|---|
| ![Shopping Cart](docs/screenshots/shopping-cart.png) |

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| SQLite | Relational database |
| HTML5 | Page structure |
| CSS3 | Styling and responsive layouts |
| JavaScript | Frontend interactions |
| Pillow | Image processing |
| Git & GitHub | Version control |

---

## Application Architecture

The application follows Django's modular project structure.

- `accounts/` - Authentication and user profiles
- `store/` - Product catalogue and categories
- `cart/` - Shopping cart functionality
- `orders/` - Checkout and order management
- `config/` - Django project configuration
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and static assets
- `media/` - Uploaded media files
- `manage.py` - Django management utility

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ritikchoudhary847/CodeAlpha_OopsCart.git
cd CodeAlpha_OopsCart
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
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

### 6. Add sample products

```powershell
python manage.py seed_products
```

To skip product image downloads:

```powershell
python manage.py seed_products --skip-images
```

### 7. Run the development server

```powershell
python manage.py runserver
```

Open the application:

**http://127.0.0.1:8000/**

Open the Django administration panel:

**http://127.0.0.1:8000/admin/**

---

## Environment Configuration

The repository includes an `.env.example` file documenting production environment variable names.

The example file is a reference and is not automatically loaded by the current Django settings. Configure the required environment variables through your deployment environment.

Never commit production secret keys, private environment files, database credentials, or user-uploaded media.

---

## Testing

The project has passed **49 automated Django tests** in the development environment.

The test suite covers the following applications:

- Accounts
- Store
- Cart
- Orders

Run the complete test suite:

```powershell
python manage.py test
```

Run Django system checks:

```powershell
python manage.py check
```

Check deployment security settings:

```powershell
python manage.py check --deploy
```

---

## Security and Validation

- Django authentication and password validation
- CSRF protection
- Server-side stock validation
- Product and profile image validation
- Order ownership checks
- Transaction-based order processing
- Environment-based production secrets
- Production HTTPS and secure-cookie configuration

---

## Current Project Scope

- Payment method: Cash on Delivery
- Database: SQLite
- Framework: Django
- Application status: Developed and tested locally

Online payment gateway integration and production deployment are not currently included.

---

## Developer

**Developed as part of the CodeAlpha Full Stack Development Internship.**

**Project:** OopsCart  
**Domain:** Full Stack Web Development  
**Backend:** Python and Django  
**Repository:** [CodeAlpha_OopsCart](https://github.com/ritikchoudhary847/CodeAlpha_OopsCart)

---

*OopsCart - Bringing product discovery, shopping cart management, and order processing together in one Django application.*