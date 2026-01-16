# ShopCore API

Modern e‑commerce backend with Django REST Framework, JWT auth, cart/order flow, and production‑minded settings (security, caching, logging).

## What’s Inside
- Auth & Users: registration, JWT login/refresh, role-based perms (admin/user)
- Products: CRUD, search/filter, cache on list, throttling
- Cart: one cart per user, add/update/remove items, stock & quantity validation
- Orders: build order from cart, stock decrease/restore, cancel flow, fake payment hook
- Docs: Swagger/Redoc via drf-spectacular
- Ops: custom exception handler, structured logging, security headers when DEBUG=False

## Tech Stack
- Python 3.10, Django, Django REST Framework
- Simple JWT, drf-spectacular, django-filter
- SQLite (dev), LocMem cache (dev) — pluggable for Redis in prod

## Quickstart
```bash
git clone https://github.com/Jemsit0300/ShopCore.git
cd ShopCore
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # doldur
python manage.py migrate
python manage.py runserver
```

### .env example
```
SECRET_KEY=dev-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

## Authentication (JWT)
- Login: `POST /Authentication/login/` → { access, refresh }
- Refresh: `POST /Authentication/token/refresh/`
- Header: `Authorization: Bearer <access>`
- Protects cart, cart-items, orders, product write ops; product read is public.

## Order & Payment Flow
```
[Add to cart] POST /api/cart-items/
[Review cart] GET  /api/cart/
[Place order] POST /api/orders/  # moves cart items -> order items, recalculates total
[Payment hook] (stub/fake payment endpoint in order flow)
[Order status] GET /api/orders/  # user sees own; admin sees all
[Cancel order] POST /api/orders/{id}/cancel/  # restores stock
```

## API Docs
- Swagger UI: http://127.0.0.1:8000/api/docs/
- Redoc: http://127.0.0.1:8000/api/schema/redoc/

## Performance
- Product list caching (LocMem, 5 min)
- Throttling (user/anon + order/payment specific buckets)
- Query optimizations on cart/cart-items (select_related/prefetch_related)

## Security
- SECRET_KEY, DEBUG, ALLOWED_HOSTS, CORS from env
- When DEBUG=False: HSTS, secure cookies, SSL redirect, XSS/NoSniff headers
- JWT auth for write ops; role-based permissions; CORS configured via env

## Error Handling
Uniform error shape: `{ success: False, status, error, message, details }`
- Validation → `error=validation_error`, details per field
- Auth → `authentication_error`
- 403 → `permission_denied`
- 404 → `not_found`
- Fallback 500 → `server_error`
(Handler: product/exceptions.py)

## Project Structure
```
ShopCore/
├── config/            # Django project
│   ├── config/        # settings/urls
│   ├── login/         # auth app
│   └── product/       # products, cart, orders, throttles, permissions
├── requirements.txt
└── README.md
```

## CI / Next Steps
- Add Redis cache + Docker for prod
- Add payment provider integration
- Add metrics/health endpoints
- Harden rate limits per endpoint group

## Credits
Built as a learning-oriented, production-aware e‑commerce API.

