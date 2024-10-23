
from datetime import datetime, timedelta
from time import sleep
from flask import url_for, current_app
import concurrent.futures

from flask_app.database import connection
from flask_app.other_func.global_variables import *


def convert_bytes(size_bytes):
    # Define the units and their respective sizes
    units = ['B', 'KB', 'MB']
    # Initialize variables
    index = 0
    size = 0
    try:
        size = float(size_bytes)
    except:
        return ''
    # Convert bytes to larger units
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    # Return the formatted result
    return f"{round(size)} {units[index]}"

def check_filters(data, dept_id):
    try:
        keys = data.keys()
        # check if all keys contains value in it
        for key in keys:
            if not data[key]:
                print("Keys do not have value")
                return 1
        
        # checking for all the categories
        if data.get('category'):
            categories = connection.execute_query(f'select category from category')
            categories = [ x['category'] for x in categories ]
            for x in data['category']:
                if x not in categories:
                    print("Category brokwn value")
                    return 1

        # checking for all the criteria
        if data.get('criteria'):
            try:
                acc_id = connection.execute_query(f'select accredition_id from accreditions where accredition = "{data["accredition"]}" ')[0]['accredition_id']
                criterias = connection.execute_query(f'select criteria_number from criteria where accredition_id = {acc_id}')
                criterias = [ x['criteria_number'] for x in criterias ]
                for x in data['criteria']:
                    if x not in criterias:
                        print("Criteria broken value")
                        return 1
            except: 
                return 1

        # checking for datetime for academic year
        today_date = date_now()
        if data['year'] > today_date.year:
            print("Academic year broken value")
            return 1
        else:
            if data['year'] == today_date.year and data['month'] > today_date.month:
                print("Academic year broken value")
                return 1

    except Exception as e:
        print("Exception in checking the filters...", e)
        return 1

# start and end dates for the academic year
def academic_year_dates(start_year, start_month):
    # Start of academic year
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(start_year+1, start_month, 1) - timedelta(days=1)
    return start_date, end_date

'''
def new_file_details(file_name, file_id, drive_id, folder_id, service, action = None):
    try:
        # retriving the data for the file
        file_data = None
        flag = 0
        files_data = get_files(parent_id=drive_id, service=service, name = file_name)
        print('Drive_id to be checked : ',file_id )
        print("Files data :", len(files_data))
        for file_data in files_data:
            print("Files data_id :", file_data['id'])
            if file_data["id"] == file_id:
                print("New file is created...")
                update_file_data(file_data, folder_id, newEntry =True)
                flag = 1
                break
        if flag == 0:
            print("File not found in the drive, Not to be Added...")
    except Exception as e:
        print("Exception in adding new file_data :",e)

def delete_file_data_for_folder(drive_id, file_id=None):
    if drive_id: 
        file_id = connection.execute_query(f'select file_id from files where drive_id = "{drive_id}" ')
        if file_id:
            file_id = file_id[0][0]
    if file_id:
        connection.execute_query(f'delete from file_category where file_id = {file_id}')
        connection.execute_query(f'delete from files where drive_id = "{drive_id}" ')
        connection.execute_query(f'delete from upload_activity where file_id = "{file_id}" ')
        connection.execute_query(f'delete from ignored_files where file_id = {file_id}')
        if trash:
            connection.execute_query(f'delete from trashed where drive_id = "{drive_id}" ')
    else:
        print("File data not present...")
  

'''
# Searching the files for each folder
def search_folder_files(user, **kwargs):
    response_data = {}
    error = ''
    data_item = 1
    response_filter_data = []

    if kwargs.get('category'):
        for x in kwargs['category']:
            response_filter_data.append(
                connection.execute_query(f'select category, definition from category where category = "{x}" ')[0]
            )
    
    elif kwargs.get('criteria'):
        category_ = set()
        print(kwargs['criteria'])
        for x in kwargs['criteria']:
            desc = connection.execute_query(f'select criteria_id, definition from criteria where criteria_number = "{x}" ')[0]
            
            resp = {'criteria' : x, 'definition' : desc['definition'], 'category' : []}
            
            # adding the categories of the criteria
            criteria_category = connection.execute_query(f'select category, definition from criteria_category join category on criteria_category.category_id = category.category_id where criteria_id = "{desc["criteria_id"]}" ')
            
            for category in criteria_category:
                category_.add(category['category'])
                resp['category'].append({'category' :category['category'], 'def' : category['definition']})
            
            kwargs['category'] = list(category_)
            response_filter_data.append(resp)

    else:
        return None
    data_item_list = {}
    try:
        file_data = filter_files(category = kwargs.get('category'), year = kwargs.get('year'), month = kwargs.get('month'), dept_id = user.dept_id)
        # print("Total files found for folder : ", folder_name , " : ", len(file_data))
        if file_data:
            for x in file_data.keys():
                for y in file_data[x]:
                    y["data_item"] = data_item
                    data_item_list[data_item] = y["unique_id"]
                    data_item += 1
                    del y["unique_id"]

            for x in kwargs['category']:
                if response_data.get(x):
                    response_data[x].extend(file_data.get(x))
                else:
                    response_data[x] = file_data.get(x)
        else:
            error += f'No files for the department'

    except Exception as e:
        print(e)
        error += f'Error while seraching for files in department'

    # returns the list of all the files
    if not error:
        error = None
    print()
    return {'data':response_data,'filter_data': response_filter_data, 'error' : error, 'data_item' :data_item_list}

# filter file data based on the criterias
def filter_files(**kwargs):
    try:
        categories = kwargs['category']
        start_date, end_date = academic_year_dates(kwargs['year'], kwargs['month'])
        print(start_date, end_date)
        print("Academic start and end_date :",start_date, end_date)
    except Exception as e:
        print("All filters are not present ...")
        return None

    response = {}
    for x in categories:
        response[x] = []
    
    try:
        category_list_str = ','.join(f"'{category}'" for category in categories)
        query = f'''
        SELECT f.file_id,
            CONCAT(DATE_FORMAT(f.period_date, '%Y%m%d'), '_', GROUP_CONCAT(c.category ORDER BY c.category SEPARATOR ','), '_', f.file_name) AS formatted_file_name,
            GROUP_CONCAT(c.category ORDER BY c.category SEPARATOR ',') AS categories,
            f.unique_id,
            f.file_name,
            f.size,
            f.period_date,
            f.owner_id,
            u.email,
            m.link,
            f.description,
            latest_trash.*
        FROM files f
        JOIN file_category fc ON f.file_id = fc.file_id
        JOIN category c ON fc.category_id = c.category_id
        JOIN mimeType m ON m.mimeType_id = f.mimeType_id
        JOIN users u ON u.user_id = f.owner_id
        LEFT JOIN (
            SELECT fa.file_id, fa.activity_type, fa.activity_timestamp
            FROM activities fa
            JOIN (
                -- Subquery to get the latest activity for each file
                SELECT file_id, MAX(activity_timestamp) AS latest_timestamp
                FROM activities
                GROUP BY file_id
            ) latest_activity ON fa.file_id = latest_activity.file_id
                            AND fa.activity_timestamp = latest_activity.latest_timestamp
            WHERE fa.activity_type = 'Trashed' 
            AND NOT EXISTS (
                SELECT 1
                FROM activities fa_restored
                WHERE fa_restored.file_id = fa.file_id
                AND fa_restored.activity_type = 'Restored'
                AND fa_restored.activity_timestamp > fa.activity_timestamp
            )
        ) latest_trash ON f.file_id = latest_trash.file_id
        WHERE f.dept_id = '{kwargs["dept_id"]}'
        AND c.category IN ({category_list_str})
        AND f.period_date BETWEEN '{start_date}' AND '{end_date}'
        AND latest_trash.file_id IS NULL  -- Exclude files that are in the trash
        GROUP BY f.file_id;

        '''
        result = connection.execute_query(query)
        for i in result:
            for c_ in i["categories"].split(','):
                response[c_].append({
                    "data_item": 0,
                    "unique_id": i["unique_id"],
                    "name" : i["formatted_file_name"],
                    "time" : i["period_date"],
                    "size" : convert_bytes(i["size"]),
                    "icon" : i["link"],
                    "email" : i["email"],
                    "desc": i["description"]
                })

        return response
    except Exception as e:
        print("Exception while filtering the files...", e)
        return None