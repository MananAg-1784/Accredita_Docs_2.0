
from flask import Blueprint, request, url_for, render_template, current_app, redirect, flash, abort, get_flashed_messages, Response, send_file
from datetime import timedelta
from json import loads, dumps
import uuid
import random
import requests
import os

from flask_app.database import connection

from flask_app.other_func.global_variables import *
from flask_app.other_func.authentication import *
from flask_app.other_func.send_email import send_mail
from flask_app.config import *
from flask_app.other_func.enc_dec import encrypt_fernet, decrypt_fernet
from flask_app.other_func.upload_files import aws_bucket, get_file_name_data

from flask_app.logger import logger

main = Blueprint('main', __name__)

@main.before_request
def before_request_func():
    logger.info(
        "URL : %s | method : %s",
        request.path,
        request.method
    )

@main.route('/')
def home_page():
    user_id = request.cookies.get('user_id')
    if user_id is not None:
        return redirect('/profile')
    else:
        logger.info('New User has visted the site')
    return render_template('home.html')

@main.route('/login')
def login():
    print("Returning page")
    return render_template('login.html')

@main.route('/login',methods = ['POST'])
def login_post():
    try:
        email = request.form['email']
        password = request.form['password']
        if not email or not password:
            flash("Missing values enter both username and password")
            raise Exception

        print("New login : ",email, password)
        sql = f"SELECT unique_id, otp FROM users WHERE email = '{email}' AND password = '{password}' "
        result = connection.execute_query(sql)
        if result:
            if result[0]['otp']:
                flash("Email id is not yet verified, Verification link is in the email",'danger')
                raise Exception

            user_id = result[0]["unique_id"]
            print("Unique id for the user is : ",user_id)

            # making the user_id cookie 
            expire_date = date_now(onlyDate=False)
            expire_date = expire_date + timedelta(days=365)

            response = redirect('/profile')
            cookie_id = encrypt_fernet(data = user_id, key = current_app.config['SECRET_KEY']).decode()
            response.set_cookie('user_id', cookie_id, expires= expire_date)
            return response
        else:
            print("User not present")
            flash('Invalid username or password', 'danger')
    except:
        print("Exception occured")
    
    return render_template('login.html')

@main.route('/register')
def register():
    print("Returning page")
    return render_template("register.html")

@main.route('/register',methods = ['POST'])
def register_post():
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get("password")
        print("registering new user : ", email)

        # Check if any field is empty
        if not first_name or not last_name or not email or not password:
            print("All fields not present")
            flash('All fields are required!','danger')
            raise Exception()

        if not email.endswith("christuniversity.in"):
            flash("Unauthorised Email","danger")
            raise Exception()

        sql = f"select unique_id from users where email = '{email}'; "
        result = connection.execute_query(sql)
        if result:
            print("Email already registered")
            flash("Email is already registered",'danger')
            raise Exception()
        
        user_id = str(uuid.uuid4())
        while True:
            if not connection.execute_query(f'select unique_id from users where unique_id = "{user_id}" '):
                print("user_id is present")
                break
            user_id = str(uuid.uuid4())

        name = f"{first_name} {last_name}"
        otp = random.randint(100000, 999999)
        print(user_id, otp)

        message = f"Verification otp number is : {otp}\n Verifitaion link : {os.getenv('WEBSITE_LINK')}/verify/{user_id} "
        if send_mail(email,"Verification OTP",message):
           print("Verification Email sent")
           flash("Verification Email sent","success")
        else:
            print("Cannot send registration email")
            flash("Error try again",'danger')
            raise Exception 

        # Insert data into the table (assume table name is 'users')
        query = f"INSERT INTO users (name, email, password, unique_id,otp) VALUES ('{name}','{email}','{password}','{user_id}',{otp})"
        connection.execute_query(query)

        print("Registration successfull")
        flash('Registration successful!','success')
        return redirect(f'/verify/{user_id}')

    except Exception as e:
        print("Exception occured", e)
        pass
    return render_template("register.html")

@main.route("/verify/<uid>")
def verify_email(uid):
    print(uid)
    user_details = connection.execute_query(f"select email, password, otp from users where unique_id = '{uid}' ")
    if not user_details:
        return abort(404)
    return render_template("verify.html", uid=uid)

@main.route('/verify/<uid>',methods=["POST"])
def verify_post(uid):
    try:
        user_details = connection.execute_query(f"select unique_id, email, password, otp from users where unique_id = '{uid}' ")
        if not user_details:
            return abort(404)

        email = request.form.get('email')
        otp = request.form.get('otp')   
        user_details = user_details[0]
        if not email or not otp:
            flash("Enter all fields" 'danger')
            raise Exception

        if user_details["email"] == email and str(user_details["otp"]) == str(otp):
            flash("Verfication Successfull, You can now Login",'success')
            connection.execute_query(f"update users set otp = NULL where email = '{email}' ")
            
            user_id = user_details["unique_id"]
            print("Unique id for the user is : ",user_id)

            # making the user_id cookie 
            expire_date = date_now(onlyDate=False)
            expire_date = expire_date + timedelta(days=365)
            response = redirect('/profile')
            cookie_id = encrypt_fernet(data = user_id, key = current_app.config['SECRET_KEY']).decode()
            response.set_cookie('user_id', cookie_id, expires= expire_date)
            return response

        else:
            flash("Incorrect credentials",'danger')
            raise Exception
    except Exception as e:
        print("Exception occured",e)
    return render_template("verify.html")


@main.route('/logout')
@login_required('logout')
def logout(user, **kwags):
    print(user.id)
    email = connection.execute_query(f"select email from users where unique_id = '{user.id}' ")[0]["email"]
    logger.info(f"Log-out user >> {email}")

    try:
        if users.get(user.id):
            users.pop(user.id)
        else:
            print("user not present in the users list")
    except:
        pass
    response = redirect('/')
    response.set_cookie('user_id', '', expires=0)
    return response

@main.route('/profile')
@login_required('profile')
def user_profile(user,**kwargs):
    print("Profile Page")
    data = connection.execute_query('select dept_name from department')
    depts = [ _['dept_name'] for _ in data]
    return render_template('profile.html', user = user, depts=depts, **kwargs)

@main.route('/search')
@login_required('search')
def search_files(user, **kwargs):
    try:
        dept_id = connection.execute_query(f'select dept_id from department where dept_name = "{user.dept}" ')[0]['dept_id']

        accreditions = [ x['accredition'] for x in connection.execute_query('select accredition from accreditions') ]
        category = connection.execute_query('SELECT category, definition FROM category;')
        sql = '''
            SELECT c.criteria_number as cr, c.definition as def, a.accredition as acc from criteria as c
            join accreditions as a
            on a.accredition_id = c.accredition_id;
        '''
        criterias_details =  connection.execute_query(sql)
        criterias = {_:[] for _ in accreditions}
        for i in criterias_details:
            criterias[i['acc']].append({"criteria":i['cr'],'definition':i['def']})
    except Exception as e:
        print("Exception : ",e)
    return render_template('search.html', user = user, **kwargs, accreditions = accreditions, category = category, criteria = criterias)

@main.route('/upload')
@login_required('upload')
def upload_files(user, **kwargs):
    _ = connection.execute_query('select * from mimeType')
    mimeTypes = {}
    for x in _:
        mimeTypes[x['mimeType_name']] = x['link']

    dept_id = connection.execute_query(f'select dept_id from department where dept_name ="{user.dept}" ')[0]["dept_id"]
    categories = connection.execute_query('SELECT category, definition FROM category;')

    return render_template('upload.html', user = user, mimeType = mimeTypes,categories = categories, **kwargs)

@main.route('/update')
@login_required('update')
def update_(user, **kwargs):
    data_dict = {
        'categories': connection.execute_query('SELECT category, definition FROM category;'),
        'accredition' : [ x['accredition'] for x in connection.execute_query('select accredition from accreditions') ]
    }
    return render_template('update.html', user = user, data_dict = data_dict, **kwargs)

@main.route('/view/file')
@login_required('search')
def view_file(user,**kwargs):
    try: 
        dept_id = request.args.get('e')
        file_id = decrypt_fernet(request.args.get('q'), current_app.config['SECRET_KEY'])
        if not dept_id or not file_id:
            return abort(404)

        file_present = connection.execute_query(f'select file_id, file_name,m.mimeType_name from files f join mimeType m on f.mimeType_id = m.mimeType_id where unique_id = "{file_id}" and dept_id = {dept_id} ')

        if not file_present[0]['file_id']:
            return abort(405)

        dept = connection.execute_query(f"select dept_name from department where dept_id = {dept_id}")[0]['dept_name']
        if dept != user.dept or user.privilage == 'denied':
            raise Exception("User not authorised")

        try:
            extension = get_file_name_data(file_present[0]['file_name'], True)[-1]
            url = aws_bucket.get_file_link(f"{dept}/{file_id}{extension}")
            print(url)
            if not url:
                raise Exception()
        except:
            abort(500)

    except Exception as e:
        print("Cannot access the file : ",e)
        abort(401)

    return redirect(url)

@main.route('/admin')
@login_required('profile')
def admin_access(user, **kwargs):
    try:
        email = kwargs.get("email")
        if not email:
            email = connection.execute_query(f"select email from users where user_id = {user.id}")[0]["email"]
        perm_email = connection.execute_query("select * from admin_email")
        perm_email = [ x["email"] for x in perm_email ]
        if email in perm_email:
            depts = connection.execute_query(f'select dept_name, dept_id, owner from department')
            dept_data = []
            for dept in depts:
                users = connection.execute_query(f'select email from users where dept_id = {dept["dept_id"]}')
                users = [x["email"] for x in users]
                dept_data.append({
                    'name': dept["dept_name"],
                    'owner': dept["owner"],
                    'id':dept["dept_id"],
                    'users': users 
                })
            accredition = [ x['accredition'] for x in connection.execute_query('select accredition from accreditions') ]
            return render_template('admin.html',dept = dept_data,acc = accredition, user = user, **kwargs)
        raise Exception()
    except Exception as e:
        print(e)
        return abort(401)

@main.route('/add_acc', methods=['POST'])
def admin_page_actions():
    try:
        acc = request.form.get('acc')
        accredition = [ x['accredition'].lower().strip().replace(" ","") for x in connection.execute_query('select accredition from accreditions') ]
        if acc:
            if acc.lower().strip().replace(" ","") not in accreditions:
                connection.execute_query(f'insert into accreditions(accredition) values("{acc}") ')
                accredition.append(acc)
                flash("Accredition Added")
            else:
                flash("Accredition already added")
        else:
            flash("No Accredition Mentioned")
    except Exception as e:
        print("Add accreditions : ", repr(e))
        flash("Error, Try Again")

    return redirect('/admin')

@main.route('/add_dept', methods=['POST'])
def _admin_page_actions():
    try:
        dept = request.form.get('dept')
        if dept:
            depts = connection.execute_query(f'select dept_name from department ')
            x = [ j["dept_name"].lower().strip().replace(" ","") for j in depts ]
            if dept.lower().strip().replace(" ","") not in x:
                connection.execute_query(f'insert into department(dept_name)values("{dept}") ')
                flash("New Department Added")
            else:
                flash("Deprament already added")
        else:
            flash("No Department Mentioned")
    except Exception as e:
        print("Add department : ", repr(e))
        flash("Error, Try Again")

    return redirect('/admin')