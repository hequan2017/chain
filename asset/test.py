from jms import UserService
username = 'admin'
password="rebrCnM7PEVmktcE"

user_service = UserService(app_name='coco', endpoint='http://54.249.102.43')

user, token = user_service.login(username=username, password=password,
                public_key=None, login_type='ST', remote_addr='54.249.102.43')
print(user)