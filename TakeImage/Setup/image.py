'''
create image.sh file
python3 image.py
schedule image.sh to execute every 15min
'''
import boto3
import botocore
import subprocess
import os, shutil
import time

from datetime import datetime

racknum = '000088'
home_folder = 'Olathe'
shelves = (0, 1, 2, 3)
today = datetime.today()
Y = today.year
M = today.month
D = today.day
MM = today.minute
H = today.hour
bucket_name = 'my-rack'
temp_folder = 'temp'

s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            print('Creating Folder')
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def emptyFolder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            print('Removing '+the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def checkBucketExists():
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket='my-rack')
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
    return exists


def main():
    # fsopts = "-S 5 -D 3 --font sans:72 --no-banner -r 1280x720 --jpeg 65"
    fsopts = "-S 30 -D 5 --font sans:50 --banner-colour 0xFF$racknum --line-colour 0xFF000000 -r 1280x720 --jpeg 65"

    for a in shelves:
        command = 'fswebcam --device /dev/video{0} {1} /home/pi/{2}/temp/{3}.jpg'.format(str(a), fsopts, home_folder,
                                                                                         str(a))
        try:
            print('\n')
            print('Taking Image With Command')
            print(command)
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            print(process.stdout.read())
            print('Image Taken')
            print('--------***---------')
            process.wait(60)
        except subprocess.TimeoutExpired:
            print('Timed Out For Video' + str(a))
            pass
        filename = str(a) + '-' + str(H) + str(MM) + '.jpg'
        path = racknum + '/' + str(Y) + '/' + str(M) + '/' + str(D) + '/' + filename
        local_path = '/home/pi/{0}/temp/{1}.jpg'.format(home_folder, str(a))
        if checkBucketExists():
            msg = 'Uploading Image On -> {0}-{1}-{2} {3}:{4}'.format(str(Y), str(M), str(D), str(H), str(MM))
            print(msg)
            s3.Object(bucket_name, path).put(Body=open(local_path, 'rb'))
            print('Done Uploading At'+path)
            print('Now Sleeping for 5 Seconds')
            print('***')
            print('\n')
        time.sleep(5)
    emptyFolder(temp_folder)


# call main function
if __name__ == "__main__":
    createFolder(temp_folder)
    emptyFolder(temp_folder)
    main()
