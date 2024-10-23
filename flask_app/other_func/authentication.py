from functools import wraps
from json import loads, dumps
from flask import request, abort, url_for, redirect, current_app
import uuid
import random
import string

# flask_app modules
from flask_app.other_func.global_variables import *
from flask_app.other_func.enc_dec import encrypt_fernet, decrypt_fernet
from flask_app.database import connection

from flask_app.logger import logger

def allowed_routes(privilage, request_url):
    priv = {'admin': ['search', 'upload', 'update'], 'viewer' : ['search'], 'editor' : ['search', 'upload']}
    try:
        route = priv.get(privilage,[])
        if ['profile','logout'] not in route:
            route.extend(['profile','logout'])
        if not privilage and request_url not in ['profile', 'logout']: 
            raise Exception("denied")
        elif privilage:
            if request_url not in route:
                raise Exception("denied")
        else:
            pass
        return route
    except Exception as e:
        logger.warning(f"Access to route : {request_url} -> Denied")
        return None

def create_user_object(user_id):
    user = None
    user_data = connection.execute_query(f"select unique_id, email,name,dept_id, privilage from users where unique_id = '{user_id}'")
    if not user_data:
        return False
    user_data = user_data[0]

    if not users.get(user_id):
        user = User(user_id)
    else:
        user = users[user_id]

    # Checking and creating the User object
    if user_data["dept_id"]:
        dept = connection.execute_query(f'select dept_name from department where dept_id = {user_data["dept_id"]}')

        user.dept = dept[0]["dept_name"] if dept else None
        if user.dept:
            user.dept_id = user_data["dept_id"]
        user.privilage = user_data["privilage"] if user_data["privilage"] else None
        if user.privilage and not priv.get(user.privilage):
            connection.execute_query(f'update users set privilage = "denied" where unique_id = "{user_id}" ')
            user.privilage = 'denied'
            logger.warning(f"Privialge for the user : {user_data['privilage']} : DENIED")

    else:
        user.dept = None
        user.privilage = None
    return user

# Authentication decorator
def login_required( request_url = None ):
    def authenticate_user(func):
        @wraps(func)
        def validate_user_id(**kwargs):
            user_id = request.cookies.get('user_id')
            user_id = decrypt_fernet(user_id, current_app.config['SECRET_KEY'])

            # user_id is wrong cannot be decrypted
            if not user_id:
                logger.warning(f"Broken Cookie Value -> {request.cookies.get('user_id')} ")
                return abort(403)
            
            user_data = connection.execute_query(f"select unique_id, email,name,dept_id, privilage from users where unique_id = '{user_id}'")

            # the user_id does not exists in the database
            if not user_data:
                logger.warning(f"Broken Cookie Value -> {request.cookies.get('user_id')} ")
                return abort(403)

            user_data = user_data[0]
            user = create_user_object(user_id)

            # privilage checking
            route = allowed_routes(user.privilage, request_url)
            if not route:
                print("Aborting...")
                abort(401)
            return func(user = user, email = user_data["email"], name = user_data["name"], routes = route)

        return validate_user_id
    return authenticate_user

# decrypt the user_id and check 
def validate_user_access(func):
    @wraps(func)
    def get_user_data(data_dict):
        response = {'error' : 0, 'response' : '', 'status' : 200}
        try: 
            namespace = request.namespace.replace('/', '')
            user_id = request.cookies.get('user_id')
            user_id = decrypt_fernet(user_id, current_app.config['SECRET_KEY'])
            user = create_user_object(user_id)
            if not user:
                raise Exception(1)

            access_routes = priv.get(user.privilage, [])
            access_routes = [x.lower() for x in access_routes]
            if ['profile','logout'] not in access_routes:
                access_routes.extend(['profile', 'logout'])

            if user.privilage != 'admin':
                event_name = request.event['message']
                if namespace == 'profile' and event_name != 'dept_access':
                    raise Exception('Unauthorised Access')

            if namespace not in access_routes and namespace != 'admin':
                raise Exception('Unauthorised Access')
            else:
                data =  func(data_dict = data_dict, user = user)
                
                if data:
                    
                    if type(data) == str:
                        try: 
                            data = loads(data)
                        except: 
                            response['response'] = data

                    if type(data) == dict:
                        keys = list(data.keys())
                        if 'error' in keys:
                            response['error'] = data.get('error')
                            data.pop('error')

                        keys = list(data.keys())
                        if len(keys) == 1 and 'response' in keys:
                            response['response'] = data.get('response')
                        else:
                            response['response'] = data
                    
                    else:
                        response['response'] = data
                    
                # no data is recieved == None
                else:
                    
                    response['error'] = 1

        except Exception as e:
            print("Exception while validating data access", e)
            if e.args[0] == 1:
                logger.warning("----- Session Expired -----")
                response = {'status' : 400, 'error' : 'Session Expired, Please Reload'}
            else:
                logger.warning("---- Unauthorised access -----")
                response = {'status' : 400, 'error' : 'Unauthorised access, Please Login Again'}
        
        return dumps(response)
    return get_user_data

def random_generator(length=6):
    # Define the character set for the password
    characters = string.ascii_letters + string.digits + string.punctuation
    # Generate the password using random.choice to pick characters
    password = ''.join(random.choice(characters) for _ in range(length))
    return password