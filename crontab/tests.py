from django.test import TestCase

# Create your tests here.

import datetime
import time

now = datetime.datetime.now().strftime('%Y-%m-%d')
last_time = (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y-%m-%d')

print(now)
print(last_time)

