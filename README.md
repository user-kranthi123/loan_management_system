# loan_management_system
## Setup Instructions
### 1. Clone the Repository
 ```
    git clone https://github.com/user-kranthi123/loan_management_system.git
    cd loan-management-system
```
### 2. Set Up a Virtual Environment
```
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate     # Windows
```
### 3. Install Dependencies
    pip install -r requirements.txt
### 4. Configure the Database
    configure the database properties in settings.py
### 5. Apply Migrations
```
    python manage.py makemigrations
    python manage.py migrate

```
### 6. Create a superuser
```
    python manage.py createsuperuser
```
### 7. Run the server
```
    python manage.py runserver
```

## Library Details

The application includes custom library <strong>lms_core</strong>
```
    cd lms_core
```