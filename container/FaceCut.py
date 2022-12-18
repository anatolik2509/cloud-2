import io
import json
import os
import uuid
import random

from PIL import Image
import boto3
from sanic import Sanic
from sanic.response import empty
import ydb
import ydb.iam

PHOTO_TABLE_NAME = 'photo'

app = Sanic(__name__)

ydb_driver: ydb.Driver
config: dict


@app.after_server_start
async def after_server_start(app, loop):
    print(f"App listening at port {os.environ['PORT']}")
    global config
    config = {
        'PHOTO_BUCKET': os.environ['PHOTO_BUCKET'],
        'FACE_BUCKET': os.environ['FACE_BUCKET'],
        'DB_ENDPOINT': os.environ["DB_ENDPOINT"],
        'DB_PATH': os.environ["DB_PATH"]
    }
    global ydb_driver
    ydb_driver = get_driver()
    ydb_driver.wait(timeout=5)


@app.post("/")
async def hello(request):
    print(f"Received request: {request.json}")
    messages = request.json['messages']
    for message in messages:
        try:
            process_message(message)
        except Exception as e:
            print(e)
    print("success")
    return empty(status=200)


@app.after_server_stop
async def shutdown():
    print('shutdown')
    ydb_driver.close()


def add_image_info_to_db(original_id, face_id):
    rand = random.Random()
    query = f"""
    PRAGMA TablePathPrefix("{config['DB_PATH']}");
    INSERT INTO {PHOTO_TABLE_NAME} (id, original_id, face_id)
    VALUES ({rand.getrandbits(64)}, '{original_id}', '{face_id}');
    """
    print(f"Trying execute query: {query}")
    session = ydb_driver.table_client.session().create()
    session.transaction().execute(query, commit_tx=True)
    session.closing()


def get_image(bucket, name):
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )
    response = s3.get_object(
        Bucket=bucket,
        Key=name
    )
    return response['Body'].read()


def put_image(bucket, name, content):
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )
    s3.put_object(
        Body=content,
        Bucket=bucket,
        Key=name,
        ContentType='application/octet-stream'
    )


def get_driver():
    endpoint = config["DB_ENDPOINT"]
    path = config["DB_PATH"]
    creds = ydb.iam.MetadataUrlCredentials()
    driver_config = ydb.DriverConfig(
        endpoint, path, credentials=creds
    )
    return ydb.Driver(driver_config)


def process_message(message):
    body = json.loads(message['details']['message']['body'])
    image = Image.open(io.BytesIO(get_image(config['PHOTO_BUCKET'], body['object_key'])))
    face = body['face']
    face_num = 0
    x = set()
    y = set()
    for coordinate in face:
        x.add(int(coordinate['x']))
        y.add(int(coordinate['y']))
    sorted_x = sorted(x)
    sorted_y = sorted(y)
    left = sorted_x[0]
    right = sorted_x[1]
    top = sorted_y[0]
    bottom = sorted_y[1]
    face_id = f"{body['object_key'].removesuffix('.jpg')}_{face_num}.jpg"
    cut_face = image.crop((left, top, right, bottom))
    img_byte_arr = io.BytesIO()
    cut_face.save(img_byte_arr, format='JPEG')
    put_image(config['FACE_BUCKET'], face_id, img_byte_arr.getvalue())
    face_num += 1
    add_image_info_to_db(body['object_key'], face_id)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ['PORT']), motd=False, access_log=False)
