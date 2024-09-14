# Django Ecommerce App

Welcome to the Django Ecommerce App! This application allows users to purchase products with a seamless checkout experience. It features Stripe payments, promo code functionality, and comprehensive order tracking system.

## Features

- **User Login and Registration**: Secure user authentication for making purchases.
- **Product Listings**: Browse through products categorized with discounted prices.
- **Advanced Checkout**: Complete the purchase with shipping and billing address functionality.
- **Stripe Payment Integration**: Secure payments via Stripe.
- **Promo Code Functionality**: Apply discount codes during checkout.
- **Order Tracking**: Track orders with a delivery timeline.

## Tech Stack

- **Frontend**: Django Templates
- **Backend**: Django, PostgreSQL
- **Payment Gateway**: Stripe

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/ecommerce-app.git

2. Navigate to the project directory:

   ```bash
   cd ecommerce-app

3. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   venv\Scripts\activate  # For Windows
   source venv/bin/activate  # For Linux/Mac

4. Install the dependencies:

   ```bash
   pip install -r requirements.txt

5. Create a .env file in the root directory and add the following environment variables:

   ```bash
   SECRET_KEY=your_app_secret_key  
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=_your_db_port
   STRIPE_PUBLIC_KEY=your_stripe_public_key
   STRIPE_SECRET_KEY=your_stripe_secret_key

6. Run database migrations to set up your database schema:

   ```bash
   python manage.py migrate

7. Run the development server:

   ```bash
   python manage.py runserver

## Configuration

- **Database**: Set up your PostgreSQL connection using `DATABASE_URL` in the `.env` file.
- **Stripe**: Add your Stripe secret key to the `STRIPE_SECRET_KEY` environment variable.

## Usage

- **User Registration and Login**: Users can register an account and log in to make purchases.
- **Browse Products**: Explore various products with categorized listings and discounted prices.
- **Checkout Process**: Add products to the cart, enter billing and shipping details, and pay using Stripe.
- **Promo Codes**: Apply promotional codes at checkout for discounts.
- **Order Tracking**: After placing an order, users can track their orders through a timeline displayed on their account page.

## Contributing

Feel free to fork the repository and submit pull requests. Please ensure your contributions adhere to the project's coding standards and guidelines.

## Contact

For any inquiries or issues, please reach out to [developer.kamraniqbal@gmail.com](developer.kamraniqbal@gmail.com).
