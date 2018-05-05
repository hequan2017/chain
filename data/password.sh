#!/bin/bash
python manage.py  shell    << EOF
from  name.models import Names
user=Names.objects.create_superuser('admin','hequan@chain.com','1qaz.2wsx')
exit()
EOF