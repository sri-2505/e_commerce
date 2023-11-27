# e_commerce 
Live preview(srikanth.world) is not avaialable as of now. Due to some aws cost. Sorry for the inconvenience.

Created a basic e-commerce website for learning the django.

Django - 4.2.3

# To start
pip install -r requirements.txt

cp .env-example .env

Enter the db details

python manage.py migrate

python manage.py runserveer

# Features

- Payment integration with Razorpay (India's most used payment cateway)
  - It supports UPI, Card transaction and Internet banking.


- Celery tool integrated for sending periodic email for abundant cart


- boto used to download the .env copy from AWS S3 for development and production stage



- django-jazzmin theme used for admin interface


- Customized user model implemented for email based authentication


- Rollbar and slack integrated for receiving logs.

# upcoming features

- Customised payment gateway
- Class based view
- Separate models and view to separate files.
- User profile
- Email verification
- Separate branches for development and production

 🙏 Thanks for view!!!

Give me a star, if you like my work.

Happy coding... 👋
