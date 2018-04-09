#!/bin/bash
python manage.py  shell    <<EOF
from django.contrib.auth.models import User
user=User.objects.create_superuser('admin','hequan@chain.com','1qaz.2wsx')
exit()
EOF