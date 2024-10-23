

from flask_socketio import rooms, join_room, leave_room, close_room, emit
from flask import render_template, url_for, request, current_app
from json import dumps
from time import sleep
import os
from datetime import datetime, timedelta
import concurrent.futures
import threading
import uuid

from flask_app.database import connection
from flask_app.socket_connection import socketio

from flask_app.other_func.enc_dec import encrypt_fernet, decrypt_fernet
from flask_app.other_func.authentication import validate_user_access, create_user_object
from flask_app.other_func.global_variables import *
from flask_app.other_func.upload_files import *
from flask_app.other_func.filters import *
from flask_app.other_func.files import *


def check_file_data(name,categories):
    file_name = get_file_name_data(name)
    print("File_name : ", file_name)
    file_creation_date = getCreationDate(file_name[0] ,None)
    print("File_date : ", file_creation_date)

    if not file_creation_date:
        return 'File naming Error'

    category = file_name[1]
    print("File Category : ", category)
    # multiple categories...
    if not category:
        print("No category for the file...")
        return 'File naming Error'
    else:
        category = category.split(',')
        category_id = []
        for cat in category:
            if cat:
                cat_id = connection.execute_query(f'select category_id from category where category = "{cat}" ')
                print("Ccategory _id : ", cat_id)
                if cat_id and (cat not in categories):
                    return 'File naming Error'
                elif not cat_id:
                    return 'Category not present'
    return None

def upload_file_toDrive(file_index, url, user, sid):
    print(user)
    try:
        file_data = user.uploading_files[file_index]
        itemNo = file_data.itemNo

        file_name_data = get_file_name_data(file_data.name, True)
        sleep(1)
        socketio.emit('progress_report', dumps({'progress' : 'upload', 'itemNo' : itemNo}),namespace='/upload', room=sid) 
        sleep(1)
        print("Starting upload... background_task....")

        resp = {'itemNo' : itemNo, 'progress': ''}
        
        if os.path.isfile(url):
            print("File path : ", url)
            file_data.uploadingLock = 1
            file_content = None
            file_id = str(uuid.uuid4())

            # upload the file content
            response = 1
            while True:
                if not connection.execute_query(f"select file_id from files where unique_id = '{file_id}' "):
                    break
                file_id = str(uuid.uuid())

            name = f"{user.dept}/{file_id}{file_name_data[len(file_name_data)-1]}"
            print("#####", name)
            dept_id = connection.execute_query(f"select dept_id from department where dept_name = '{user.dept}' ")[0]['dept_id']

            if aws_bucket.upload_file(file_path = url, file_name = name):
                print("File uploaded", file_data.mimeType)
                mimeType = connection.execute_query(f'select mimeType_id from mimeType where mimeType_name = "{file_data.mimeType}" ')
                if mimeType:
                    mimeType = mimeType[0]['mimeType_id']
                else:
                    mimeType = 1
                print(mimeType)
                user_id = connection.execute_query(f"select user_id from users where unique_id = '{user.id}' ")[0]["user_id"]
                connection.execute_query(f'''
                insert into files(unique_id, file_name, period_date, size, dept_id, owner_id, mimeType_id, description, last_modified)
                values('{file_id}','{"".join(file_name_data[len(file_name_data)-2:])}','{getCreationDate(file_name_data[0])}','{file_data.size}','{dept_id}','{user_id}','{mimeType}','{file_data.desc}','{datetime.now()}')
                ''')
                file_id_ = connection.execute_query(f'select file_id from files where unique_id = "{file_id}"')[0]["file_id"]
                print(file_id_)

                # Iterate over the list of category names
                print(file_data.categories)
                for category_name in file_data.categories:
                    query = f"SELECT category_id FROM category WHERE category = '{category_name}' "
                    result = connection.execute_query(query)
                    if result:
                        category_id = result[0]["category_id"]
                        print(category_id)
                        # Insert into file_category
                        insert_query = f"INSERT INTO file_category (file_id, category_id) VALUES ({file_id_},{category_id})"
                        connection.execute_query(insert_query)
                
                connection.execute_query(f'insert into activities(file_id,activity_type,activity_timestamp,performed_by) values({file_id_},"Uploaded","{datetime.now()}",{user_id})')

            else:
                response = 0

            file_data.uploadingLock = 0
            print(response)
            print("............................")
            if response:
                resp['progress'] = 'uploaded'

            elif not response:
                print("File cannot be uploaded")
                resp['error'] = 'Cannot be uploaded'
            else:
                print("File not found....")
                resp['error'] = 'Server Error, Try Again'

    except Exception as e:
        print("Exception ...", e)
        resp['error'] = 'Server Error, Try Again'

    print("............................")
    remove_upload_file_data(url, file_index, user.uploading_files)
    print("Response to emit ...", resp)
    if resp.get('error'):
        resp['progress'] = ''
    socketio.emit('progress_report', 
                   dumps(resp),
                   namespace='/upload', room=sid) 

@socketio.on("connect", namespace='/upload')
def connection_made_upload():
    user_id = request.cookies.get('user_id')
    user_id = decrypt_fernet(user_id,current_app.config['SECRET_KEY'])
    print("Client Connected..")
    users[user_id] = create_user_object(user_id)
    try:
        dept = connection.execute_query(f'select dept_id from users where user_id = "{user_id}" ')[0]['dept_id']
        room_name = f"{dept}_upload"
        join_room(room_name)
    except:
        pass

@socketio.on("disconnect", namespace='/upload')
def upload_connection_closed():
    print("Client disconnected !")
    user_id = request.cookies.get('user_id')
    user_id = decrypt_fernet(user_id, current_app.config['SECRET_KEY'])
    try:
        if users.get(user_id):
            user = users[user_id]
            remove_cache(user = user)
            users.pop(user_id, None)
        dept = connection.execute_query(f'select dept_id from users where user_id = "{user_id}" ')[0]['dept_id']
        room_name = f"{dept}_upload"
        leave_room(room_name)
        print("Client disconnected !")
    except:
        pass


@socketio.on('send_file_data', namespace='/upload')
@validate_user_access
def recieve_file_data(data_dict, **kwargs):
    sid = request.sid
    #{itemNo: file.itemNo, name:file.name, size:file.size, mimeType:file.mimeType , categories:file.categoies , segment:segment , data:'' }
    user_socket_id = request.sid
    print()
    print()
    user = kwargs.get('user')
    try:
        if not user:
            print("User not found")
            error = 1
            raise Exception
            
        print("Data recieving for the file ....")

        categories = data_dict.get('categories')
        print('item_no', data_dict['itemNo'])

        name = data_dict['name']
        url = create_url(user.id, name)
        file_uploading = None
        index = None
        error = None

        # find the index for the uploading files if it exists
        for i,x in enumerate(user.uploading_files):
                if x.name == name and x.size == data_dict['size'] and x.mimeType == data_dict['mimeType']:
                    file_uploading = x
                    index = i
                    break

        if(categories and data_dict.get('new_file_upload') and data_dict['segment'] == 1):
            # new file is being send
            print(categories)
            if index:
                del user.uploading_files[x]

            if data_dict['size'] <= 200*1024*1024:
                # validate folders categories and file_name
                response =check_file_data(name, categories)
                if response:
                    print("Error while validating data for the file")
                    return {'error' : response}
                else:
                    print('file_naming is correct')

                print("Creating new file_data....")
                user.uploading_files.append(
                    FileDataDetails(
                        sid = user_socket_id, itemNo = data_dict['itemNo'],categories =categories, name = name, size = data_dict['size'], mimeType = data_dict['mimeType'], segment = data_dict['segment'], desc = data_dict.get('desc')
                    )
                )
                index = len(user.uploading_files) - 1
                file_uploading = user.uploading_files[index]

                if os.path.isfile(url):
                    print("Exsisting file... deleting..")
                    try:
                        os.remove(url)
                    except :
                        print(f"The file '{url}' error while deleting")
                with open(url, 'wb') as f:
                    f.write(data_dict['data'])
                print("New file created at : ", url)
            else:
                return dumps({'error' : 'File Size too Big'})

        # adding to previous file data
        else:
            # check and get the url for the file
            print("Finding new file_data....")
            # instance of file_uploading
            if file_uploading and file_uploading.sid == user_socket_id:
                try:
                    if data_dict['segment'] == file_uploading.segment + 1:
                        print("Segmnet in sequence...")
                        with open(url, 'ab') as f:
                            f.write(data_dict['data'])
                        file_uploading.segment += 1
                    else:
                        print("Segmnet not in sequence...")
                        file_uploading.extraSegment[data_dict['segment']] = data_dict['data']

                    keys_= list(file_uploading.extraSegment.keys())
                    x = 0
                    while x < len(keys_):
                        if keys_[x] == file_uploading.segment + 1:
                            print("Found segement :....", keys_[x])
                            with open(url, 'ab') as f:
                                f.write(file_uploading.extraSegment[keys_[x]])
                            file_uploading.segment += 1
                            del file_uploading.extraSegment[keys_[x]]
                            x = 0
                        else:
                            x += 1

                except:
                    print("Exception while adding data to file....")
                    error = 1

            # file data not found in the user uploading files
            elif not file_uploading:
                print("File not found...")
                error = 1
            
            else:
                print("User connection changed...")
                error =  1

        # all the data has been uploaded ... processing and uploading the file
        if data_dict.get('finished'):
            if index>=0:
                print("Sending progress log...")
                # upload the file from the url
                upload_file = threading.Thread(target = upload_file_toDrive, args=(index, url, user,sid)).start()
            else:
                print("File data not found in users object...")
                error = 1
    except Exception as e:
        print('Exception...',e)

    if error:
        remove_upload_file_data(url, index, user.uploading_files)
        return {'error' : 'Server Error, Try Again'}
    return 1


@socketio.on('clear_cache', namespace='/upload')
@validate_user_access
def remove_cache_datas(data_dict, **kwargs):
    # ... recieve error if a file upload has error... scrapes of the entire file data..
    print("Request to remove all data for the user...")
    print(kwargs)
    user = kwargs['user']
    remove_cache(user)
    print(user.uploading_files)
    try:
        users.pop(user_id, None)
    except:
        pass
    return 1


# delete files which are greater than 7 days - 1 mnth and trashed alag se
# if a file is trashed do not allow any options to below acitvities for the file
# Descption for the renamed files

@socketio.on('load_activity', namespace='/upload')
@validate_user_access
def load_acitivity(data_dict, **kwargs):
    sid = request.sid
    print("Recieved request to load upload activity....", data_dict)
    time_period = data_dict["time_period"]
    print("\n\n",time_period)
    if time_period == "month":
        now = datetime.now()
        current_date = now.day
        time_period = f"WHERE a.activity_timestamp BETWEEN CURDATE() - INTERVAL {current_date} DAY AND CURDATE() + Interval 1 Day - interval 1 second"
    elif time_period == "trashed":
        print("Getting trashed files")
        time_period = -1
    elif time_period == "all":
        time_period = ""
    else:
        time_period = time_period = f"WHERE a.activity_timestamp BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE() + Interval 1 Day - interval 1 second"

    priv = kwargs['user'].privilage

    user_id = None
    if priv != 'admin':
        user_id = connection.execute_query(f'select user_id from user where unique_id = "{kwargs["user"].id}" ')[0]['user_id']

    dept_id = connection.execute_query(f'select dept_id from department where dept_name ="{kwargs["user"].dept}" ')[0]['dept_id']

    # data_item_id : unique_id -> for the folders
    activity_details = []
    recent_activity = []
    data_item = {}
    data_item_no = 0

    try:
        activity_data = None
        trashed_files = '''
            SELECT 
            CONCAT(
                DATE_FORMAT(a.activity_timestamp, '%Y%m%d'), '_',
                GROUP_CONCAT(DISTINCT c.category ORDER BY c.category SEPARATOR ','), '_',
                f.file_name
            ) AS formatted_file_name,
            u.email, 
            f.unique_id,
            a.file_id, 
            a.description, 
            a.activity_type, 
            date(a.activity_timestamp) as period,
            m.link
            FROM activities a
            JOIN users u ON a.performed_by = u.user_id
            JOIN files f ON a.file_id = f.file_id
            JOIN file_category fc ON f.file_id = fc.file_id
            JOIN category c ON fc.category_id = c.category_id
            JOIN mimeType m on m.mimeType_id = f.mimeType_id
            JOIN (
                -- Subquery to get the latest activity for each file
                SELECT file_id, MAX(activity_timestamp) AS latest_timestamp
                FROM activities
                GROUP BY file_id
            ) AS latest_activity ON a.file_id = latest_activity.file_id 
            AND a.activity_timestamp = latest_activity.latest_timestamp
            WHERE a.activity_type = 'Trashed'
            GROUP BY a.file_id, a.activity_timestamp, a.performed_by, a.description, a.activity_type ORDER BY a.activity_timestamp DESC;
            '''
        trashed_files = connection.execute_query(trashed_files)
        trashed_files_id = [ x["file_id"] for x in trashed_files]
        print("Trashed file id", trashed_files_id)

        if time_period != -1:
            query = f'''
                SELECT 
                CONCAT(
                    DATE_FORMAT(a.activity_timestamp, '%Y%m%d'), '_',
                    GROUP_CONCAT(DISTINCT c.category ORDER BY c.category SEPARATOR ','), '_',
                    f.file_name
                ) AS formatted_file_name,
                f.file_id,
                f.unique_id,
                u.email, 
                a.file_id, 
                a.description, 
                a.activity_type, 
                date(a.activity_timestamp) as period,
                m.link
                FROM activities a
                JOIN users u ON a.performed_by = u.user_id
                JOIN files f ON a.file_id = f.file_id
                JOIN file_category fc ON f.file_id = fc.file_id
                JOIN category c ON fc.category_id = c.category_id
                JOIN mimeType m on m.mimeType_id = f.mimeType_id
                {time_period}
            '''
            if priv != 'admin':
                query = query + f''' AND u.user_id = {user_id} '''
            else:
                query = query + f" AND u.dept_id = {dept_id} "
            query = query + "GROUP BY a.file_id, a.activity_timestamp, a.performed_by, a.description, a.activity_type ORDER BY a.activity_timestamp DESC; "

            activity_data = connection.execute_query(query)
        else:
            activity_data = trashed_files
        today_date = datetime.today().date().strftime('%Y-%m-%d')

        for activity in activity_data:
            data_item_no +=1
            file_link = encrypt_fernet(data = str(activity["unique_id"]), key = current_app.config['SECRET_KEY']).decode()
            data = {
                'data_item': data_item_no,
                'name': activity["formatted_file_name"],
                'icon': activity["link"],
                'owner': activity["email"],
                'action': activity["activity_type"].strip(),
                'time': activity["period"],
                'link': f"/view/file?q={file_link}&e={dept_id}",
                "desc": activity["description"]
            }
            if time_period != -1 and activity["file_id"] in trashed_files_id:
                data["trashed"] = 1
            else:
                data["trashed"] = 0

            data_item[data_item_no] = encrypt_fernet(data = str(activity["file_id"]), key = current_app.config['SECRET_KEY']).decode()
            if str(activity["period"]) == today_date:
                recent_activity.append(data)
            else:
                activity_details.append(data)

                
    except Exception as exc:
        print("Exception getting activity call...", exc)

    return {
        'html_data' : render_template(
                'upload/upload_activity.html', 
                activity = activity_details,
                recent_activity = recent_activity, 
                date = datetime.now().strftime('%Y-%m-%d'), priv=priv, 
                time_period = time_period
                ), 
        'data': data_item
    }


@socketio.on('delete_file',namespace='/upload')
@validate_user_access
def delete_file_data_(data_dict, **kwargs):
    print("Recieved request to load upload activity....", data_dict)
    try:
        unique_id = data_dict['drive_id']
        unique_id = decrypt_fernet(unique_id, current_app.config['SECRET_KEY'])
        action = data_dict['action']

        if unique_id:
            file_id = connection.execute_query(f'select owner_id from files where file_id = {unique_id} ')[0]
            owner_id = file_id['owner_id']
            file_id = unique_id

            user_details = connection.execute_query(f'select user_id,privilage from users where unique_id = "{kwargs["user"].id}" ')[0]

            if action == 'delete':
                print(user_details['privilage'])
                print(owner_id, user_details['user_id'])
                if user_details['privilage'] == 'admin' or owner_id == user_details['user_id']:

                    if delete_file(file_id):
                        connection.execute_query(f'delete from activities where file_id = {file_id}')    
                        connection.execute_query(f'delete from file_category where file_id = {file_id}')            
                        connection.execute_query(f'delete from files where file_id = {file_id}')
                        return "File deleted"
                    else:
                        print("Cannot delete file from aws")
                        return "Cannot delete file"
                else:
                    return "No permission to delete the file"

            elif action == 'trash':
                print("Moving the file to trash..")
                # move the file to trash
                print("Updating activities....")
                connection.execute_query(f"insert into activities(file_id, activity_type,performed_by) values({file_id},'Trashed',{user_details['user_id']})")
                return "File deleted"
            else:
                return "Cannot Delete File"
        else:
            return "Cannot Delete File"
    except Exception as e:
        print("Exception in deleting file : ", e)
        return "Cannot Delete File"

@socketio.on('rename_file',namespace='/upload')
@validate_user_access
def rename_file_data_(data_dict, **kwargs):
    print(data_dict)
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

@socketio.on('restore_file',namespace='/upload')
@validate_user_access
def restore_file_data_(data_dict, **kwargs):
    print("Recieved request to load upload activity....", data_dict)
    try:
        unique_id = data_dict['drive_id']
        unique_id = decrypt_fernet(unique_id, current_app.config['SECRET_KEY'])
        print(unique_id)
        file_name = get_file_name_data(data_dict['file_name'], extension = True)
        file_name = "".join(file_name[len(file_name)-2:])
        print(file_name)

        data = connection.execute_query(f"select * from files where file_id = {unique_id} and file_name = '{file_name}' ")
        print(data)
        if unique_id and data:
            
            user_id = connection.execute_query(f'select user_id from users where unique_id = "{kwargs["user"].id}" ')[0]['user_id']
            print("Updating activities....")
            connection.execute_query(f"insert into activities(file_id, activity_type,performed_by) values({unique_id},'Restored',{user_id})")

            return 'File restored'
        else:
            return "Cannot Restore File"
    except Exception as e:
        print("Exception in deleting file : ", e)
        return "Cannot Restore File"
