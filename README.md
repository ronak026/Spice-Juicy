# Spice & Juicy – Django Restaurant Ordering App

An end‑to‑end restaurant ordering web app built with Django. It lets customers browse the menu, add items to cart, place orders, and complete payment (COD or Stripe). Users can manage profiles and addresses. Clean, responsive UI with a modern look and dark‑mode friendly styles.

## Features

- Menu browsing with category filter and search
- Cart with quantity updates and subtotal/total
- Order placement flow with address selection
- Payments: Cash on Delivery or Stripe Checkout (INR)
- Auth: register, login (email-based form), logout
- Profile management with picture upload and bio
- Address management and validation (pincode rules)
- Admin for managing categories and menu items

## Tech Stack

- Django 5
- PostgreSQL (configurable)
- Stripe Checkout (test mode)
- HTML templates + static CSS/JS

## Project Structure

```
restaurant/
  manage.py
  restaurant/            # project settings/urls
  backend/               # app: models, views, urls, templates
static/                  # global static assets
media/                   # uploaded profile pictures
```

Key modules:

- `backend/models.py`: `Category`, `MenuItem`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Payment`, `Review`, `Address`, `Profile`
- `backend/views.py`: menu, cart, orders, payments, auth, profile, address
- `backend/urls.py`: routes like `/`, `/menu/`, `/cart/`, `/order/place`, `/payment/<id>/`
- `backend/load_foods.py`: helper to seed menu data from `backend/data/foods.py`

## Screens (high-level)

- Home: hero, featured premium dish
- Menu: grid cards with images, price, category filter and search
- Cart: table with quantity controls and total
- Place Order: summary and address
- Payment: COD or Stripe Checkout
- Profile: view/edit profile, upload picture

Add screenshots/gifs to `static/images/` and reference them here:


<img width="1915" height="930" alt="image" src="https://github.com/user-attachments/assets/4bf2a7ed-5adf-4b30-a0dc-28df58fb5ae2" />

<img width="1919" height="1034" alt="image" src="https://github.com/user-attachments/assets/ba111c2a-ff93-4d36-b6c9-506c073da353" />

<img width="1919" height="832" alt="image" src="https://github.com/user-attachments/assets/c4280cc5-8d22-43d8-ac3a-0f830a20ce8c" />


## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 13+ (or update settings to SQLite for local quickstart)
- Node/Yarn is NOT required

### Clone and setup

```bash
# clone
git clone <your-repo-url>.git
cd restaurant

# create virtualenv (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# upgrade pip and install deps
python -m pip install --upgrade pip
pip install -r requirements.txt  # if present; otherwise install django and stripe
```

If no `requirements.txt`, install minimal deps:

```bash
pip install django==5.2.3 stripe==11.* psycopg2-binary
```

### Configure environment

Copy your secrets into environment variables or edit `restaurant/settings.py` for local dev.

Required settings:

- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`
- `DATABASES` (defaults to PostgreSQL; adjust for local)

Quick local SQLite switch (optional): in `restaurant/settings.py`:

```python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
  }
}
```

### Database setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Seed sample menu data (optional)

Open Django shell and run:

```bash
python manage.py shell
```

Then:

```python
from backend.load_foods import load_foods
load_foods()
exit()
```

### Run the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

## Core URLs

- `/` home
- `/menu/` browse menu, filter, search
- `/cart/` view cart
- `/add-to-cart/<item_id>/` add item
- `/cart/update/<cart_item_id>/` change quantity
- `/remove-from-cart/<item_id>/` remove item
- `/order/place` place order
- `/payment/<order_id>/` pay via COD or Stripe
- `/order/success/<order_id>/` confirmation
- `/register/`, `/login/`, `/logout/`
- `/profile/`, `/profile/edit/`
- `/add-address/`

## Admin

Enable staff access at `/admin/` to manage categories and menu items.

## Notes and Tips

- Images: items use `image_url`; upload profile pictures go to `media/profile_pics/`
- Currency: INR; Stripe amounts are sent in paise (`price * 100`)
- Search: case-insensitive over name and description
- Category filter: uses distinct category names from menu items

## Deployment

- Set `DEBUG = False`, configure `ALLOWED_HOSTS`
- Provide production `SECRET_KEY`, Stripe keys, and a managed Postgres
- Serve static with WhiteNoise or CDN; media via S3/GCS if needed

## License

Add a license of your choice (e.g., MIT) to clarify usage.
