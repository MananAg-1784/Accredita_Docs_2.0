
from flask import render_template, url_for, request, current_app
from json import dumps
from time import sleep
from io import BytesIO
import openpyxl
import threading

from flask_app.database import connection
from flask_app.socket_connection import socketio
from flask_app.other_func.global_variables import priv, FileData
from flask_app.other_func.enc_dec import *
from flask_app.other_func.authentication import validate_user_access, create_user_object
from flask_app.other_func.filters import * 


def process_file_(*args, **kwargs):
    # Process the sheet as needed
    print("\n Background Task ... Processing the Excel File")
    error = "Error while Processing ... Try Again"
    try:
        user_id = kwargs['user_id']
        user = users[user_id]
        dept_id = connection.execute_query(f'select dept_id from department where dept_name = "{user.dept}" ')[0]["dept_id"]
        sheet = kwargs['sheet']
        c = 0
        file_data = []
        header = {}
        # get all the rows and header from the excel file
        for row in sheet.iter_rows(values_only=True):
            c=c+1
            if c == 1:
                fields_not_present = []
                row = [ x.lower() for x in row ]

                # check if the excel file is from criteria or not
                if 'criteria' in row and user.file.acc:
                    print("The Excel file is from criteria")
                    pass
                # check if the excel file is from category or not
                elif 'criteria' not in row and not user.file.acc:
                    print("The Excel file is from Category")
                    pass
                else:
                    error = "Columns are incorrect ..."
                    raise Exception(error)

                for field in user.file.fields:
                    if field not in row:
                        fields_not_present.append(field)
                    else:
                        header[field] = row.index(field)
                # mandatory field is not present
                if fields_not_present:
                    error = f"Field not Present :  {fields_not_present}"
                    raise Exception(f'Fields not present :  {fields_not_present}')
            else:
                # Process the file data...
                file_data.append(row)
        sheet = None

        # Process the entire file data
        html_data = ''
        # for categories
        if not user.file.acc :
            html_data = process_categories(file_data, dept_id, header)
        # for criteria
        else:
            html_data = process_criteria(file_data, dept_id, header, user.file.acc)

        if not html_data:
            raise Exception('Error while processing the file')
        else:
            print("File Proccessed and data added to the database ...")
        file_data = f"<strong>Excel File data Updated Successfully</strong><div>Total data uploaded : {c-1}</div>{html_data}"
        socketio.emit('processed_file_data', dumps({'data' : file_data}), namespace = '/update' )

    except Exception as e:
        print("Error while Processing the excel file :", e)
        socketio.emit('processed_file_data', dumps({'error' : error}), namespace = '/update')
    user.file = None


@socketio.on('dept_users', namespace="/profile")
@validate_user_access
def get_dept_users(data_dict, **kwargs):
    try:
        privilage = kwargs.get('user').privilage
        user_dept = connection.execute_query(f'select dept_id from department where dept_name = "{ kwargs.get("user").dept}" ')
        user_dept = user_dept[0]['dept_id'] if user_dept else None

        if privilage == 'admin':
            # all the users that are under the admins department
            response = {}
            response['dept_users'] = []
            data = connection.execute_query(f'select unique_id,email,name, privilage from users where dept_id = "{user_dept}" ')
            if data:
                for _ in data:
                    if _['email'] != data_dict['email']:
                        response['dept_users'].append( {
                            'name' : _['name'],
                            'email' : _['email'],
                            'privilage' : _['privilage']
                        } )   
            response['available-privs'] = list(priv.keys())
            response['dept_users'] = render_template('profile/dept_users.html', dept_users = response['dept_users'], available_privs = response['available-privs'])
            return response
        else:
            return None
    except Exception as e:
        print("Exception while getting dept_users", e)
        return None
 

@socketio.on('dept_access', namespace="/profile")
@validate_user_access
def dept_access(data_dict, **kwargs):
    try:
        dept = data_dict['department']
        user_id = kwargs.get('user').id
        print("Requested dept : ",dept)
        print("Requested user_id : ",user_id)

        data = connection.execute_query(f'select dept_id from department where dept_name = "{dept}" ')
        dept_id = data[0]['dept_id'] if data else None
        if not dept_id:
            dept = None
        else:
            connection.execute_query(f"update users set dept_id = {dept_id} where unique_id = '{user_id}' ")

        try:
            if users.get(user_id):
                del users[user_id]
        except:
            pass
        return 1
    
    except Exception as e:
        print("Exception while updating department ..", e)
        return None


@socketio.on('priv_grant', namespace="/profile")
@validate_user_access
def priv_grant(data_dict, **kwargs):
    try:
        privilage =  data_dict['privilage']
        email = data_dict['email']
        print("Set Privilage : ", privilage)
        print("Email :", email )

        data = connection.execute_query(f'select unique_id, dept_id, privilage from users where email = "{email}" ')

        if data:
            user_id = data[0]['unique_id']
            if privilage not in priv.keys():
                privilage = 'denied'
            connection.execute_query(f'update users set privilage = "{privilage}" where unique_id = "{user_id}" ')
            try:
                if users.get(user_id): 
                    del users[user_id]
            except:
                pass
            return privilage
        else:
            raise Exception("Email id is not registered")

    except Exception as e:
        print("Exception while updating privilage ...", e)
        return None


@socketio.on('remove_user', namespace="/profile")
@validate_user_access
def remove_user(data_dict, **kwargs):
    try:
        email = data_dict
        data = connection.execute_query(f'select unique_id, privilage from users where email = "{email}" ')
        if data:
            user_id = data[0]['unique_id']
            connection.execute_query(f'update users set privilage = null, dept_id = null where unique_id = "{user_id}" ')
            try:
                if users.get(user_id):
                    del users[user_id]
            except:
                pass
            return "Removed"
        else:
            raise Exception("Email id is not registered")

    except Exception as e:
        print("Exception while updating privilage ...", e)
        return None



@socketio.on("connect", namespace='/update')
def connection_made_update():
    user_id = request.cookies.get('user_id')
    user_id = decrypt_fernet(user_id,current_app.config['SECRET_KEY'])
    print("Client Connected..")
    users[user_id] = create_user_object(user_id)
    try:
        dept = connection.execute_query(f'select dept_id from users where user_id = "{user_id}" ')[0]['dept_id']
        room_name = f"{dept}_update"
        join_room(room_name)
    except:
        pass

@socketio.on("disconnect", namespace='/update')
def connection_closed_update():
    print("Client disconnected !")
    user_id = request.cookies.get('user_id')
    user_id = decrypt_fernet(user_id, current_app.config['SECRET_KEY'])
    try:
        if users.get(user_id):
            user = users[user_id]
            remove_cache(user = user)
            users.pop(user_id, None)
        dept = connection.execute_query(f'select dept_id from users where user_id = "{user_id}" ')[0]['dept_id']
        room_name = f"{dept}_update"
        leave_room(room_name)
        print("Client disconnected !")
    except:
        pass


@socketio.on('add-new-category', namespace='/update')
@validate_user_access
def new_category(data_dict, **kwargs):
    print("Recieved : ", data_dict)
    # check for the category_name and def and if it exists or not
    # else return error --> category already present | incorrect value
    # return 1 if everything correct
    try:
        category = data_dict['name'].upper()
        definition = data_dict['def']

        if not category and not definition:
            return {"error":"Missing data values"}

        cat_present = connection.execute_query(f'select category from category where category = "{category}" ')
        flag = 1  if cat_present else 0

        if flag == 1:
            return {"error" : f"Category {category} already present.."}
        else:
            print(category)
            print(len(category))
            if len(category) > 5 or len(category) < 3:
                return {"error":"Cateogry naming Error"}

            connection.execute_query(f'insert into category(category, definition) values("{category}","{definition}")')
            category_id = connection.execute_query(f'select category_id from category where category = "{category}" ')

            if category_id:
                categories = connection.execute_query("select category, definition from category")
                return {'response': categories}
            else:
                raise Exception()
    except Exception as e:
        print("Exception while creating new category", e)
        return {"error":"Cannot add Category"}

@socketio.on('modify_old_category', namespace='/update')
@validate_user_access
def modify_category_def(data_dict, **kwargs):
    print("Recieved : ", data_dict)
    try:
        category = connection.execute_query(f'select * from category where category = "{data_dict["category"]}" ')
        if not category or not data_dict['definition']:
            return {"error":"Category is not present, Add new Category"}
        
        connection.execute_query(f"update category set definition = '{data_dict['definition']}' where category_id = {category[0]['category_id']} ")
        categories = connection.execute_query('select category,definition from category')
        return {'response':categories}

    except Exception as e:
        print("Exception while modifying the category", e)
        return {"error":"Cannot Modify Category"}

@socketio.on('delete-category', namespace='/update')
@validate_user_access
def delete_category(data_dict, **kwargs):
    print("Recieved : ", data_dict)
    # check for the category_name and def and if it exists or not
    # else return error --> category already present | incorrect value
    # return 1 if everything correct
    try:
        if data_dict:
            cat_id = connection.execute_query(f'select category_id from category where category = "{data_dict}" ')
            if cat_id:
                cat_id = cat_id[0]["category_id"]
                folder_cat = connection.execute_query(f"select file_id from file_category where category_id = {cat_id}")
                if folder_cat:
                    return {"error":"Cannot delete, Some files contains the category"}
                else:
                    connection.execute_query(f"delete from criteria_category where category_id = {cat_id}")
                    connection.execute_query(f"delete from category where category_id = {cat_id} ")

                categories = connection.execute_query('select category,definition from category')
                return {'response':categories}
            else:
                return {"error":"Category not present"}
        else:
            return {"error":"Cannot Delete Category"}
    except Exception as e:
        print("Exception while creating new category", e)
        return {"error":"Cannot Delete Category"}


@socketio.on('criteria-data', namespace='/update')
@validate_user_access
def criteria_details(data_dict, **kwargs):
    print("Recieved data... ,", data_dict)
    acc = data_dict['accredition']
    try:
        acc_id = connection.execute_query(f'select accredition_id from accreditions where accredition = "{acc}" ')
        if acc_id:
            acc_id = acc_id[0]["accredition_id"]
            criteria = get_criteria_data(acc_id)
            data = render_template('update/update-criteria.html', criteria = criteria)
            return {'error' : 0, 'response' : {'criteria': criteria, 'data' : data}}
        else:
            print("invalid Accredition")
            return {'error' : "Invalid Accredition"}

    except Exception as e:
        print("Exception while criteria_details()", e)
        return {'error' : "Reload and Try Again"}


@socketio.on('add-criteria', namespace='/update')
@validate_user_access
def add_new_criteria(data_dict, **kwargs):
    sleep(1)
    print("Recieved data... ", data_dict)
    try:
        if data_dict.get('criteria') and data_dict.get('definition') and data_dict.get('accredition'):
            try:
             float(data_dict['criteria'].replace('.',''))
            except:
                return {"error":"Criteria Name can only contain numbers or (.)"}
            acc_id = connection.execute_query(f'select accredition_id from accreditions where accredition = "{data_dict["accredition"]}" ')
            criteria_id = connection.execute_query(f'select criteria_id from criteria where criteria_number = "{data_dict["criteria"]}" ')

            # Validate the code for the criteria

            if acc_id: 
                if not criteria_id:
                    acc_id = acc_id[0]["accredition_id"]
                    connection.execute_query(f'insert into criteria(criteria_number, definition, accredition_id) values("{data_dict["criteria"]}", "{data_dict["definition"]}", {acc_id} )')

                    criteria_id = connection.execute_query(f'select criteria_id from criteria where criteria_number = "{data_dict["criteria"]}" ')[0]["criteria_id"]

                    if data_dict.get('categories'):
                        for x in data_dict.get('categories'):
                            cat_id = connection.execute_query(f'select category_id from category where category = "{x}" ')
                            if cat_id:
                                cat_id = cat_id[0]["category_id"]
                                flag = connection.execute_query(f'select criteria_id from criteria_category where criteria_id = {criteria_id} and category_id = {cat_id} ')
                                if not flag:
                                    connection.execute_query(f'insert into criteria_category values({criteria_id},{cat_id})')
                    return 1
                else:
                    return {"error":"Criteria already present"}
            else:           
                return {"error":"Accredition not present"}
        else:
            return {"error":"All the Fields are not filled"}
    
    except Exception as e:
        print("Exception while criteria_details()", e)
        return {"error":"Cannot Add new Criteria"}


@socketio.on('modify-criteria', namespace='/update')
@validate_user_access
def modify_criteria(data_dict, **kwargs):
    print("Recieved data... ,", data_dict)
    try:
        if data_dict.get('criteria') and data_dict.get('definition'):
            criteria_id = connection.execute_query(f'select criteria_id from criteria where criteria_number = "{data_dict["criteria"]}" ')

            # Validate the code for the criteria
            if criteria_id:
                criteria_id = criteria_id[0]["criteria_id"]
                # Updating the new definition
                connection.execute_query(f'update criteria set definition = "{data_dict["definition"]}" where criteria_id = {criteria_id} ')

                connection.execute_query(f'delete from criteria_category where criteria_id = {criteria_id}')
                rejected_categories = []

                for x in data_dict.get('categories'):
                    cat_id = connection.execute_query(f'select category_id from category where category = "{x}" ')
                    if cat_id:
                        cat_id = cat_id[0]["category_id"]
                        connection.execute_query(f'insert into criteria_category values({criteria_id},{cat_id})')
                        print("Added category...", x)
                    else:
                        rejected_categories.append(x)

                if rejected_categories:
                    return {"error":f"Category not present{rejected_categories}"}

                return 1
            else:
                return {"error":"Criteria is not present, add new Criteria"}
        else:
            return {"error":"Code and Definition are not filled"}
    except Exception as e:
        print("Exception while modifying criteria_details()", e)
        return {"error":"Cannot Modify Criteria"}

@socketio.on('remove-criteria', namespace='/update')
@validate_user_access
def remove_criteria(data_dict, **kwargs):
    print("Recieved data... ,", data_dict)
    try:
        if data_dict:
            criteria_id = connection.execute_query(f'select criteria_id from criteria where criteria_number = "{data_dict}" ')

            # Validate the code for the criteria
            if criteria_id:
                criteria_id = criteria_id[0]["criteria_id"]
                # Updating the new definition
                connection.execute_query(f'delete from criteria_category where criteria_id = {criteria_id} ')
                connection.execute_query(f'delete from criteria where criteria_id = {criteria_id} ')
                return 1
            else:
                return {"error":"Criteria is not present"}
        else:
            return {"error":"Cannot delete Criteria"}
    except Exception as e:
        print("Exception while modifying criteria_details()", e)
        return {"error":"Cannot delete Criteria"}

@socketio.on('change_dept_owner', namespace='/admin')
@validate_user_access
def change_owner(data_dict, **kwargs):
    print("Changing owner...", data_dict)
    try:
        dept = data_dict.get("dept")
        email = data_dict.get("email")
        if dept and email:
            if connection.execute_query(f'select * from users where email = "{email}" '):
                connection.execute_query(f'update department set owner = "{email}" where dept_name = "{dept}" ')
                connection.execute_query(f'update users set privilage="admin" where email = "{email}" ')
                return "Updated"
        else:
            return {'error' : "Missing data values"}
    except Exception as e:
        print("Exception...", repr(e))
        return {'error': 'Cannot change department owner'}

@socketio.on('recieve_file_data', namespace='/update')
@validate_user_access
def recieve_file(data_dict, **kwargs):

    user_socket_id = request.sid
    user = kwargs.get('user')
    print("Data recieved for the file ....")

    try:
        print(user.file.sid)
        if (user.file.sid != user_socket_id) and not(data_dict.get('file_size') and data_dict.get('file_name')) :
            print("Not same sid..")
            user.file = None
            return {"error":"Try Again"}

        if data_dict.get('file_size') and data_dict.get('file_name') and not user.file.Lock:
            print("Has the FileData object..")
            user.file = FileData(user_socket_id, data_dict['file_size'], data_dict['file_name'])

            if data_dict.get('acc'):
                user.file.acc = data_dict['acc']
                user.file.fields = ['serial no', 'criteria', 'definition', 'category']
            else:
                user.file.fields = ['serial no', 'category', 'definition']

    except:
        print("User has no FileData object... Creating...")
        user.file = FileData(user_socket_id, data_dict['file_size'], data_dict['file_name'])
        print(user.file.name, user.file.total_size)
        if data_dict.get('acc'):
                user.file.acc = data_dict['acc']
                user.file.fields = ['serial no', 'criteria', 'definition', 'category']
        else:
            user.file.fields = ['serial no', 'category', 'definition']

        if not user.file.name.endswith('.xlsx') and not user.file.name.endswith('.csv'):
            return {"error":"Not an Excel or csv File"}
        
        if user.file.total_size == 0:
            return {"error":"File has no data"}
        
        # limit size if 50 MB
        if user.file.total_size > (50*1024*1024):
            return {"error":"File is Too Large"}

    user.file.file_data += data_dict['file_data']
    print("length of recieved file : ", len(data_dict['file_data']))
    user.file.read_size += len(data_dict['file_data'])
    print("Data read till now :", user.file.read_size)

    if( data_dict.get('finished') == 1 ):
        print("All data Collected..")
        print(user.file.total_size, user.file.read_size)

        if user.file.total_size > user.file.read_size:
            return {"error":"Try Again"}

        if user.file.name.endswith('.xlsx'):
            print("Excel file it is ...")

            try:
                # Convert the received chunk back to a BytesIO object
                chunk_bytes_io = BytesIO(user.file.file_data)
                user.file.file_data = None
                # Load the Excel file using openpyxl
                wb = openpyxl.load_workbook(chunk_bytes_io)
                # Access a specific sheet (modify as needed)
                sheet = wb.active
                
                # starting background task for processing the file
                socketio.start_background_task(target = process_file_, sheet = sheet,user_id = user.id)

            except Exception as e:
                user.file = None
                print("Exception while reading the excel file", e)
                return {"error":"Corrupt File, Try Again.."}

        elif user.file.name.endswith('.csv'):
            print("CSV file it is ...")
            return {'error': "CSV file not supporeted"}
            user.file = None

    return 1

@socketio.on('reload-category', namespace='/update')
@validate_user_access
def reload_category_(data_dict, **kwargs):
    try:
        categories = connection.execute_query('select category,definition from category')
        return {'response':categories}

    except Exception as e:
        print("Exception while modifying the category", e)
        return {"error":"Cannot Get Category"}

