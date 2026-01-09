🛒 ShopCore API

ShopCore is a scalable e-commerce backend API built with Django REST Framework. The project is designed to evolve step‑by‑step from Junior+ to Mid‑level backend architecture, following real‑world e‑commerce requirements.

⚠️ This project is under active development.

📌 Current Features

🔐 Authentication & Users

User registration system

JWT Authentication (login / refresh)

Authenticated user permissions

📦 Products

Product CRUD operations

Admin‑only product management

Filtering & search support

🛒 Cart System (NEW)

One cart per authenticated user

Users can only access their own cart

CartItem management (add / update / remove products)

Quantity & stock validation

Cascade delete support

📚 API Docs

Swagger UI

Redoc

🧱 Project Structure

ShopCore/
├── config/
│   ├── manage.py
│   ├── login/
│   ├── product/
│   ├── cart/
│   └── config/
├── requirements.txt
├── README.md
└── venv/

🛠 Installation

git clone https://github.com/Jemsit0300/ShopCore.git
cd ShopCore
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

📚 API Documentation

Swagger UI:
👉 http://localhost:8000/api/docs/

Redoc:
👉 http://localhost:8000/api/schema/redoc/

🛒 Cart & CartItem System

🗓️ Day 6 – Cart Model

Purpose: Create a cart bound to the authenticated user

Implemented

Cart model

user (FK → Custom User)

created_at

CartSerializer

Cart create endpoint (authenticated users)

Cart list endpoint (user sees only own cart)

Security Checks

JWT authentication required

Users cannot access other users' carts

🎯 Level impact: Junior+ → Mid threshold

🗓️ Day 7 – CartItem Model & Serializer

Purpose: Add / remove products from cart

Implemented

CartItem model

cart (FK → Cart)

product (FK → Product)

quantity (default = 1)

CartItemSerializer

CartItem create endpoint

CartItem list endpoint (cart detail)

Security Checks

Only cart owner can add products

Quantity default works correctly

🎯 Level impact: Mid

🗓️ Day 8 – Quantity Update & Validation

Purpose: Enforce correct quantity logic

Implemented

CartItem update endpoint (PUT / PATCH)

Quantity validation rules:

Quantity ≥ 1

Quantity ≤ product stock

Validation Checks

Stock limit cannot be exceeded

JWT authorization enforced

🎯 Level impact: Mid

🗓️ Day 9 – CartItem & Cart Delete

Purpose: Complete cart lifecycle

Implemented

CartItem delete endpoint

Cart delete endpoint (user‑owned only)

Cascade delete: deleting cart removes cart items

Security Checks

Users cannot delete others' cart items

JWT authentication enforced

🎯 Level impact: Mid

🗓️ Day 10 – Tests & Documentation

Purpose: Stabilize & document the system

Implemented

Cart create / update / delete tests

CartItem create / update / delete tests

Swagger & Redoc verification

README updated (this document)

🎯 Level impact: Mid

🧱 Technologies Used

Python

Django

Django REST Framework

Simple JWT

drf-spectacular

django-filter

SQLite (development)

🚧 Planned Features

Order system

Checkout flow

User profile management

Payment integration

Docker support

Redis & caching

👨‍💻 Author

Developed as a learning‑driven backend project to simulate real‑world e‑commerce systems and progress from Junior+ to Mid‑level backend development.

