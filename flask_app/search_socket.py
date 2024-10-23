

from flask_socketio import rooms, join_room, leave_room, close_room, emit
from flask import render_template, render_template_string, url_for, request, current_app
from json import loads,dumps
from time import sleep
import concurrent.futures
import threading

from flask_app.database import connection
from flask_app.socket_connection import socketio

from flask_app.other_func.authentication import *
from flask_app.other_func.enc_dec import encrypt_fernet, decrypt_fernet
from flask_app.other_func.global_variables import *
from flask_app.other_func.filters import *
from flask_app.other_func.files import *
from flask_app.other_func.upload_files import *


@socketio.on("connect", namespace='/search')
def connection_made():
    user_id = request.cookies.get('user_id')
    user_id = decrypt_fernet(user_id,current_app.config['SECRET_KEY'])
    try:
        dept = connection.execute_query(f'select dept_id from users where user_id = "{user_id}" ')[0]['dept_id']
        room_name = f"{dept}_search"
        join_room(room_name)
        print("Client Connected..")
    except:
        pass

@socketio.on("disconnect", namespace='/search')
def connection_closed():
    print(rooms())
    user_id = request.cookies.get('user_id')
    user_id = decrypt_fernet(user_id,current_app.config['SECRET_KEY'])
    try:
        dept = connection.execute_query(f'select dept_id from users where user_id = "{user_id}" ')[0]['dept_id']
        room_name = f"{dept}_search"
        leave_room(room_name)
        print("Client disconnected !")
        print(rooms())
    except:
        pass


@socketio.on('search_using_category', namespace='/search')
@validate_user_access
def search_category(data_dict, **kwargs):
    sid = request.sid
    response = {'error' : 0, 'response' : {'data_list' : ''}}
    try:
        user = kwargs.get('user')
        dept_id = connection.execute_query(f'select dept_id from department where dept_name ="{user.dept}" ')[0]['dept_id']
        print(data_dict)
        if check_filters(data_dict, dept_id):
            raise Exception("Filter values are Broken, Reload and Try again... ")
        
        # data_dict => year month folders:list category:list
        files_list = search_folder_files( user = user, category = data_dict['category'], year = data_dict['year'], month = data_dict['month'])
        files_data = files_list.get('data')
        category_data = files_list.get('filter_data')
        data_item_list = files_list.get("data_item")

        # sort the category_data based on decreasing order of no of files
        category_data.sort(key=lambda key: len(files_data[key['category']]), reverse=True)

        if files_list:
            for x in data_item_list.keys():
                _data_ = encrypt_fernet(data_item_list[x], current_app.config['SECRET_KEY']).decode()
                data_item_list[x] = _data_

            response['response']['data_list'] = render_template('search/search_category_layout.html', data = files_data, category_data = category_data, data_item_list =  data_item_list, dept_id = dept_id)
            response['error'] = files_list.get('error')
            
            response['response']['data_item_list'] = data_item_list
                
    except Exception as e:
        print("Exception in searching using category ...", e)
        response['error'] = "Server Error, Try Again.."

    return dumps(response)

@socketio.on('search_using_criteria', namespace='/search')
@validate_user_access
def search_criteria(data_dict, **kwargs):
    sid = request.sid
    response = {'error' : 0, 'response' : {'data_list' : ''}}
    try:
        user = kwargs.get('user')
        dept_id = connection.execute_query(f'select dept_id from department where dept_name ="{user.dept}" ')[0]['dept_id']
        if check_filters(data_dict, dept_id):
            raise Exception("Filter values are Broken, Reload and Try again... ")

        # data_dict => year month folders:list criteria:list
        files_list = search_folder_files( user = user, criteria = data_dict['criteria'], year = data_dict['year'], month = data_dict['month'])
        
        files_data = files_list.get('data')
        criteria_data = files_list.get('filter_data')
        data_item_list = files_list.get("data_item")

        if files_list:
            for x in data_item_list.keys():
                _data_ = encrypt_fernet(data_item_list[x], current_app.config['SECRET_KEY']).decode()
                data_item_list[x] = _data_

            response['response']['data_list'] = render_template('search/search_criteria_layout.html', data = files_data, criteria_data = criteria_data, data_item_list =  data_item_list, dept_id = dept_id)
            response['error'] = files_list.get('error')

            response['response']['data_item_list'] = data_item_list
        
    except Exception as e:
        print("Exception in searching using criteria ...", e)
        response['error'] = "Server Error, Try Again.."
    return dumps(response)

# File visit link

@socketio.on('rename_file',namespace='/search')
@validate_user_access
def rename_file_data_search(data_dict, **kwargs):
    try:
        unique_id = data_dict.get('drive_id')
        unique_id = decrypt_fernet(unique_id, current_app.config['SECRET_KEY'])
        if unique_id:
            if data_dict['new_name'] == data_dict['name']:
                return 'Same File name'
            else:
                file_name_data = get_file_name_data(data_dict["name"], True)
                file_name = "".join(file_name_data[len(file_name_data)-2:])
                print("Only file name : ",file_name)
                file_id = connection.execute_query(f'select file_id from files where unique_id = "{unique_id}" and file_name = "{file_name}" ')
                if file_id:
                    file_id = file_id[0]["file_id"]
                    
                    # check if file naming format is correct or not
                    name_format = get_file_name_data(data_dict["new_name"], True)
                    print("New name : ",name_format)
                    creationTime = name_format[0]
                    creationTime = getCreationDate(creationTime)
                    if not creationTime:
                        return 'File format is incorrect'
                    else:
                        # change the file anem and creation Time
                        print("Renaming the file...", data_dict['new_name'])
                        
                        connection.execute_query(f'''
                        update files 
                        set file_name = '{"".join(name_format[len(name_format)-2:])}', 
                        period_date = "{creationTime}"
                        where file_id = {file_id}
                        ''')

                    # delete and add all categories
                    connection.execute_query(f'delete from file_category where file_id = {file_id}')
                    category = name_format[1]
                    # multiple categories...
                    if not category:
                        print("No category for the file...")
                    else:
                        category = category.split(',')
                        category_id = []
                        for cat in category:
                            if cat:
                                cat_id = connection.execute_query(f'select category_id from category where category = "{cat}" ')
                                if cat_id:
                                    category_id.append(cat_id[0]['category_id'])
                                else:
                                    print("category not present ...", cat)
                        for cat_id in category_id:
                            connection.execute_query(f'insert into file_category values({file_id},{cat_id})')
                        
                        user_id = connection.execute_query(f'select user_id from users where unique_id = "{kwargs["user"].id}" ')[0]['user_id']
                        print("Updating activities....")
                        connection.execute_query(f"insert into activities(file_id, activity_type,performed_by, description) values({file_id},'Renamed',{user_id},'File renamed from {data_dict['name']}')")

                        return 'File Renamed'
                else:
                    return 'Cannot Rename File'
        else:
            return 'Cannot Rename File'
       
    except Exception as e:
        print("Exception in renaming file : ", e)
        return "Cannot Rename File"

@socketio.on('delete_file',namespace='/search')
@validate_user_access
def delete_file_data_search(data_dict, **kwargs):
    try:
        unique_id = data_dict.get('drive_id')
        unique_id = decrypt_fernet(unique_id, current_app.config['SECRET_KEY'])
        action = data_dict['action']

        if unique_id:
            if action == 'trash':
                print("Moving the file to trash..")
                # move the file to trash
                file_data = connection.execute_query(f'select file_id from files where unique_id = "{unique_id}" ')
                if file_data:
                    file_data = file_data[0]
                    file_id = file_data['file_id']
                    print(file_id)
                    query = f'''
                    SELECT 
                        CASE 
                            WHEN last_activity.activity_type = 'Trashed' 
                            AND NOT EXISTS (
                                SELECT 1 
                                FROM activities fa_restored
                                WHERE fa_restored.file_id = last_activity.file_id
                                AND fa_restored.activity_type = 'Restored'
                                AND fa_restored.activity_timestamp > last_activity.activity_timestamp
                            ) 
                            THEN true
                            ELSE false
                        END AS trash_status
                    FROM (
                        SELECT fa.file_id, fa.activity_type, fa.activity_timestamp
                        FROM activities fa
                        WHERE fa.file_id = {file_id}
                        ORDER BY fa.activity_timestamp DESC
                        LIMIT 1
                    ) last_activity;
                    '''
                    trashed = connection.execute_query(query)
                    print(trashed)
                    if trashed[0]['trash_status']:
                        return 'File already in Trash'
                    else:
                        user_id = connection.execute_query(f'select user_id from users where unique_id = "{kwargs["user"].id}" ')[0]['user_id']
                        print("Updating activities....")
                        connection.execute_query(f"insert into activities(file_id, activity_type,performed_by) values({file_id},'Trashed',{user_id})")
                    
                    return 'File moved to Trash'
                else:
                    return 'File not present'
            else:
                return "Cannot Delete File"
        else:
            return "Cannot Delete File"
    except Exception as e:
        print("Exception in deleting file : ", e)
        return "Cannot Delete File"

