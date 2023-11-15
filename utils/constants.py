# payment types
# UPI = 'upi'
# E_BANKING = 'e_banking'
# CARD = 'card'
# CASH_ON_DELIVARY = 'delivary'

# payment types
ONLINE_PAYMENT = 'online payment'
CASH_ON_DELIVERY = 'cash on delivery'

PAYMENT_TYPES = [
        ('online_payment', ONLINE_PAYMENT),
        ('cash_on_delivery', CASH_ON_DELIVERY),
    ]

# payment status
COMPLETED = 'completed'
PENDING = 'pending'
ERROR = 'error'
IN_PROGRES = 'in_progres'

# order status
SHIPPED = 'shipped'
DELIVERED = 'delivered'
CANCELLED = 'cancelled'

# states - districts data should be moved to database
# states
TAMIL_NADU = 'Tamilnadu'
KERALA = 'kerala'

# states array for form choices
STATES = [
    ('tamil_nadu', TAMIL_NADU),
]

# currencies
INR = "INR"

# tamil nadu districts
CHENNAI = "chennai"
KANCHEEPURAM = "kancheepuram"
TIRUVALLUR = 'tiruvallur'
CUDDALORE = 'cuddalore'
VILLUPURAM = 'villupuram'
VELLORE = 'vellore'
TIRUVANNAMALAI = 'tiruvannamalai'
DHARMAPURI = 'dharmapuri'
KRISHNAGIRI = 'krishnagiri'
SALEM = 'salem'
NAMAKKAL = 'namakkal'
ERODE = 'erode'
COIMBATORE = 'coimbatore'
OOTY = 'ooty'
TIRUPPUR = 'tiruppur'
KARUR = 'karur'
PERAMBALUR = 'perambalur'
TIRUCHIRAPPALLI = 'tiruchirappalli'
ARIYALUR = 'ariyalur'
NAGAPATTINAM = 'nagapattinam'
THANJAVUR = 'thanjavur'
TIRUVARUR = 'tiruvarur'
PUDUKKOTTAI = 'pudukkottai'
SIVAGANGA = 'sivaganga'
MADURAI = 'madurai'
THENI = 'theni'
DINDIGUL = 'dindigul'
RAMANATHAPURAM = 'ramanathapuram'
VIRUDHUNAGAR = 'virudhunagar'
THOOTHUKUDI = 'thoothukudi'
TIRUNELVELI = 'tirunelveli'
TENKASI = 'tenkasi'
KANNIYAKUMARI = 'kanniyakumari'

TAMIL_NADU_DISTRICTS = [
    ('chennai', CHENNAI),
    ('kancheepuram', KANCHEEPURAM),
    ('tiruvallur', TIRUVALLUR),
    ('cuddalore', CUDDALORE),
    ('villupuram', VILLUPURAM),
    ('vellore', VELLORE),
    ('tiruvannamalai', TIRUVANNAMALAI),
    ('dharmapuri', DHARMAPURI),
    ('krishnagiri', KRISHNAGIRI),
    ('salem', SALEM),
    ('namakkal', NAMAKKAL),
    ('erode', ERODE),
    ('coimbatore', COIMBATORE),
    ('ooty', OOTY),
    ('tiruppur', TIRUPPUR),
    ('karur', KARUR),
    ('perambalur', PERAMBALUR),
    ('tiruchirappalli', TIRUCHIRAPPALLI),
    ('ariyalur', ARIYALUR),
    ('nagapattinam', NAGAPATTINAM),
    ('thanjavur', THANJAVUR),
    ('tiruvarur', TIRUVARUR),
    ('pudukkottai', PUDUKKOTTAI),
    ('sivaganga', SIVAGANGA),
    ('madurai', MADURAI),
    ('theni', THENI),
    ('dindigul', DINDIGUL),
    ('ramanathapuram', RAMANATHAPURAM),
    ('virudhunagar', VIRUDHUNAGAR),
    ('thoothukudi', THOOTHUKUDI),
    ('tirunelveli', TIRUNELVELI),
    ('tenkasi', TENKASI),
    ('kanniyakumari', KANNIYAKUMARI)
]

HTTP = 'http://'
HTTPS = 'https://'

# Pagination limits
ORDERS_LIMIT_PER_PAGE = 5
PRODUCTS_LIMIT_PER_PAGE = 16
