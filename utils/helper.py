import razorpay
import os
from dotenv import load_dotenv
import datetime

load_dotenv()


# login to razor pay
def razorpay_login():
    return razorpay.Client(auth=(os.getenv('RAZOR_KEY_ID'), os.getenv('RAZOR_KEY_SECRET')))


# razor pay will get amount in paise
def getRazorPayAmount(amount):
    return float(amount) * 100


# check the transaction status
def verify_signature(response_data):
    client = razorpay_login()
    return client.utility.verify_payment_signature(response_data)
