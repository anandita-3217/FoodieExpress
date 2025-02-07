# FoodieExpress - A Food Delivery Web Application
![BasicIdea](https://github.com/user-attachments/assets/02f11ab5-d261-4100-92c7-ef775bb0105b)
## Description
FoodieExpress is a food delivery web application that connects customers, restaurants and delivery partners.
The platform allows users to browse restaurants, explore menus, place orders, and track them in real time. 
Built using Django, HTML, CSS, and JavaScript, FoodieExpress offers a seamless and user-friendly experience designed to enhance food delivery efficiency

## File Structure

 - **foodieExpress**: Is the main directory that conatains the neccessary files such as settings.py and urls.py 
    
 - **core**: Is the main application directory.
    -**static** - Is the directory that contains all of the JavaScript and CSS files
    -**templates** - Is the directory that contains all of the HTML files
    -**admin.py** - Is where all the Django models are registered
    -**models.py** - Is where all the Django models are defined
    -**views.py** - Is where all the Django views are defined to ensure that the application runs smoothly
    -**urls.py** - Is where all the application's URLs are defined
    -**forms.py** - Is where all the application's forms are defined

## Models
- **User**
    - This model handles all users in the application, including customers, restaurant owners, and delivery partners. Each user has a specific role, such as:
        - Customer: Places orders and tracks deliveries
        - Restaurant Owner: Manages restaurant details, menu, and orders
        - Delivery Partner: Delivers orders and tracks earnings
- **Restaurant**
    - This model represents restaurants registered on the platform. It connects each restaurant with its owner and includes details like:
        -Name, description, and type of cuisine
        -Whether the restaurant offers only vegetarian dishes
        -The number of delivery partners it can accommodate  
- **MenuItem**
    -Each dish or food item offered by a restaurant is stored in this model. It includes:
        - The name, description, and price of the item
        - Whether the item is vegetarian and/or a bestseller
        - The availability status ( available, out of stock,removed )
- **DeliveryPartner**
    -This model tracks delivery partners who pick up and deliver orders. It stores:
        - The partner’s availability status
        - Their assigned restaurant and current delivery
        - Earnings and total completed deliveries
- **Order**
    - This model represents customer orders, storing details such as:
        - The customer who placed the order and the restaurant it’s from.
        - The delivery partner handling the order.
        - The status of the order (e.g., received, picked up, delivered).
        - The total amount and delivery address.
- **OrderItem**
    -Each order consists of one or more items, and this model stores those details:
        - The food items in the order, their quantity, and subtotal price.
        - Links the items to their respective orders.

  
## Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/me50/anandita-3217.git
```

2. Set up the database:
```bash
python manage.py makemigrations core
python manage.py migrate
```

3. Create a superuser:
```bash
python manage.py createsuperuser
```

4. Start the development server:
```bash
python manage.py runserver
```
## Requirements
- Python 3.8+
- Django 4.0+

### Restaurant Features
- Menu management system
- Order acceptance and preparation tracking
- Sales analytics and reporting
- Profile and settings management

### Customer Features
- Restaurant and menu browsing
- Order placement and tracking
- Delivery status monitoring
- Order history and reordering

### Delivery Partner Features
- Real-time availability toggling
- Order pickup and delivery management
- Earnings tracking
- Route optimization suggestions

