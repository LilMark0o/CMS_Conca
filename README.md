# Proveo: Inventory Management Web Application

## Introduction
Proveo is a web application designed to help store owners keep track of their inventory and manage product orders efficiently. It allows users to monitor stock levels, set reorder thresholds, and automatically send WhatsApp messages to suppliers when stock needs replenishing. This ensures that stores never run out of essential products and can maintain smooth operations.

## Features
- **Inventory Tracking**: Keep real-time records of stock levels for all products.
- **Reorder Alerts**: Set threshold levels for products to receive notifications when stock is low.
- **Automated Supplier Messaging**: Automatically send WhatsApp messages to suppliers to reorder products.
- **User Authentication**: Secure login and registration system for store managers and staff.
- **Supplier Management**: Maintain a database of suppliers with contact information and product details.
- **Reporting**: Generate reports on inventory levels, reorder history, and supplier performance.

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Django, Django REST Framework
- **Database**: SQLite
- **Messaging Service**: Twilio API for WhatsApp messaging
- **Hosting**: Google Cloud (here's just the code of the Django app)
- **Version Control**: Git, GitHub

## Installation

### Prerequisites
- Python 3.x
- Django 3.x or later
- SQLite
- Twilio Account (for WhatsApp messaging)
- Git

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/proveo.git
   cd proveo
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
   
5. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**
   Open your web browser and navigate to `http://127.0.0.1:8000/`

## Usage

The app is very intuitive and you will get alonge with it pretty easy

## Contributing
We welcome contributions to improve Proveo. To contribute:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License
Proveo is open-sourced software licensed under the MIT license.

## Contact
For any questions or support, please contact us at marcoalejandroramirezc@gmail.com
