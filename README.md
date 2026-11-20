
# ShopSphere

ShopSphere is a Django-based e-commerce application built from scratch as a practical project to learn web development and DevOps.

## Project Goals

- Build an e-commerce application using Django.
- Implement product management and user authentication.
- Develop a session-based shopping cart.
- Implement checkout, orders, and payment integration.
- Containerize the application using Docker.
- Use PostgreSQL for database management.
- Build CI/CD pipelines using GitHub Actions.
- Deploy the application to a production environment.

## Technologies

- Python
- Django
- SQLite (initial development)
- Git and GitHub
- Docker (planned)
- PostgreSQL (planned)
- GitHub Actions (planned)

## Current Progress

- [x] Django project setup
- [x] Product model
- [x] Database migrations
- [x] First product created using Django ORM
- [ ] Django Admin
- [ ] Product catalog
- [ ] User authentication
- [ ] Shopping cart
- [ ] Checkout and payments
- [ ] Docker and PostgreSQL
- [ ] CI/CD and deployment

## Local Development

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate into the project:

```bash
cd ShopSphere
```

Create and activate a virtual environment on Windows CMD:

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
```

Install dependencies:

```cmd
python -m pip install -r requirements.txt
```

Apply migrations:

```cmd
python manage.py migrate
```

Start the development server:

```cmd
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Project Status

This project is under active development. Features and documentation will be updated as development progresses.
