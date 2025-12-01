# Retail Inventory Manager (Online Store Edition)

## Project Overview
A full-stack e-commerce web application where customers can browse products and place orders, while staff manage inventory and sales via a dedicated admin panel.

## Features
-   **Client Interface (Online Store):**
    -   **Home Page:** Featured products and company info.
    -   **Catalog:** Browse products by category with real-time stock status.
    -   **Shopping Cart:** Session-based cart to manage items before purchase.
    -   **User Accounts:** Registration and login for order tracking.
    -   **Order History:** Customers can view their past orders.
-   **Admin Panel (Staff Only):**
    -   **Dashboard:** Comprehensive management of Products, Categories, and Orders.
    -   **Visuals:** Product thumbnails and status indicators.
    -   **Management:** Full CRUD capabilities.

## Project Structure
-   `core/`: Project settings.
-   `inventory/`: Product catalog and store views.
-   `orders/`: Order processing logic.
-   `templates/store/`: Frontend templates (Home, Catalog, Cart).
-   `templates/registration/`: Authentication templates.

## Setup Instructions

### Production (Docker)
For production environments, we use `docker-compose.prod.yml`.

1.  **Build and Run Containers:**
    ```bash
    docker compose -f docker-compose.prod.yml up -d --build
    ```

2.  **Access the Container:**
    To perform administrative tasks, you need to access the running web container:
    ```bash
    docker exec -it cw2-project-web-1 /bin/bash
    ```

3.  **Load Initial Data:**
    Inside the container, load the test/initial data:
    ```bash
    python manage.py loaddata inventory/fixtures/initial_data.json
    ```

4.  **Create Admin User:**
    Inside the container, create a superuser to access the admin panel:
    ```bash
    python manage.py createsuperuser
    ```

### Local Development
For local development, you can run the database in Docker and the Django application locally.

1.  **Start Database:**
    ```bash
    docker compose up -d
    ```
    This starts the PostgreSQL database defined in `docker-compose.yml`.

2.  **Setup Virtual Environment:**
    ```bash
    # Create virtual environment (if not exists)
    python -m venv .venv
    
    # Activate virtual environment
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    # source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Load Initial Data:**
    ```bash
    python manage.py loaddata inventory/fixtures/initial_data.json
    ```

6.  **Create Admin User:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run Server:**
    ```bash
    python manage.py runserver
    ```

## Docker Commands Cheat Sheet

-   **Stop Containers:**
    ```bash
    docker compose down
    ```
-   **View Logs:**
    ```bash
    docker compose logs -f
    ```
-   **Rebuild Containers (Prod):**
    ```bash
    docker compose -f docker-compose.prod.yml up -d --build --force-recreate
    ```

## Usage
-   **Storefront:** Access at `http://127.0.0.1:8000/`.
-   **Admin Panel:** Access at `http://127.0.0.1:8000/panel/` (Note: Default Django admin is disabled).
