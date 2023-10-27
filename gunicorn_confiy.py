import multiprocessing

# using the below calculation for better cpu usage
# workers = multiprocessing.cpu_count() * 2 + 1

# for free tier usage   
workers = multiprocessing.cpu_count()

bind = '0.0.0.0:8000'

wsgi_app = 'e_commerce.wsgi:application'

env = 'e_commerce/.env'