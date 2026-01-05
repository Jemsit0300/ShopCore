# 🛒 ShopCore API

ShopCore is an e-commerce backend API project developed using Django REST Framework.

⚠️ **This project is under active development.**

---

## 📌 Current Features
- User registration system
- JWT Authentication (login / refresh)
- Product CRUD operations
- Admin-only product management
- Filtering and search
- Swagger & Redoc API documentation

---

## 🧱 Project Structure


---

## 🛠 Installation


ShopCore/
├── config/
│ ├── manage.py
│ ├── login/
│ ├── product/
│ └── config/
├── requirements.txt
├── README.md
└── venv/


---

## 🛠 Installation

```bash
git clone https://github.com/Jemsit0300/ShopCore.git
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



🧱 Technologies Used

Python

Django

Django REST Framework

drf-spectacular

Simple JWT

SQLite

django-filter



🚧 Planned Features

Order system

Shopping cart

User profile

Docker support