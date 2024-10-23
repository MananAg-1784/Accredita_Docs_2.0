from flask_app.S3_bucket.bucket import Bucket
from flask_app.config import *
import os
from flask import current_app

from flask_app.database import connection
from datetime import datetime, timedelta
from flask_app.other_func.global_variables import date_now
import pytz


aws_bucket = Bucket(aws_credentials={
    "access key": os.getenv("ACCESS_KEY"),
    "secret key": os.getenv("SECRET_KEY"),
    "bucket_name": os.getenv("BUCKET_NAME"),
    "region": os.getenv("REGION"),
})

def get_file_name_data(file_name, extension = False):
    try:
        print(file_name)
        file_name = file_name.replace(' ','')
        file_ = file_name
        if file_name.rfind('.') != -1:
            file_name = file_name[ : file_name.rfind('.')  ]
        name_format = file_name.split('_')
        _ = 3 - len(name_format)
        if _ > 0:
            for i in range(0,_):
                name_format.append('')
        if extension:
            name_format.append(file_[file_.rfind('.'):])
        return name_format
    except Exception as e:
        return None

def getCreationDate(fileDate, createdTime=None):
    # checking for the data of creation time
    flag = 1
    print("Date : ", fileDate)
    try:
        if fileDate and len(fileDate) == 8 and fileDate.isdigit():
            print("The file has a valid inbulilt date")
            try:
                date_object = datetime(int(fileDate[:4]), int(fileDate[4:6]), int(fileDate[6:8]))
                flag = 0
                if date_object > date_now():
                    flag =1
                else:
                    #print("File date in file_name")
                    print("Date object : ", date_object)
                    return date_object.strftime("%Y-%m-%d")
            except ValueError as e:
                print("Value error: ",e)
                flag = 1
        
        if flag == 1 and createdTime:
            print("Fields name does not have any date")
            # Given RFC 3339 date-time string
            rfc3339_datetime_str = createdTime
            rfc3339_datetime = datetime.strptime(rfc3339_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            utc_timezone = pytz.utc

            # Convert the UTC time to IST
            ist_timezone = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
            ist_datetime = utc_timezone.localize(rfc3339_datetime).astimezone(ist_timezone)

            standard_datetime_str = ist_datetime.strftime("%Y-%m-%d")

            return standard_datetime_str
            
        return None
    except Exception as e:
        print("getting creation date :", e)
        return None

def delete_file(unique_id):
    try:
        file_details = connection.execute_query(f'select unique_id,dept_id,file_name from files where file_id = {unique_id} ')[0]

        dept = connection.execute_query(f'select dept_name from department where dept_id = {file_details["dept_id"]} ')
        print(dept)

        file_name = file_details["file_name"]
        file_extension = file_name[file_name.rfind('.'):]
        print(file_extension)

        object_name = f"{dept[0]['dept_name']}/{file_details['unique_id']}{file_extension}"
        print(object_name)
        return aws_bucket.delete_object(object_name)
    except Exception as e:
        print(e)
        return False