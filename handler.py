import boto3
import io
from PIL import Image,ImageOps
import os

s3 = boto3.client('s3')
size = int(os.environ['THUMBNAIL_SIZE'])

def s3_thumbnail_generator(event, context):
    # print event
    print('hi2')
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # generate thumbnail only on non thumbnail images
    if ("_thumbnail." not in key):
        # get the image
        image = get_s3_image(bucket, key)
        # resize the image
        thumbnail = image_to_thumbnail(image)
        # get the new filename
        thumbnail_key = new_filename(key)
        # upload the thumbnail
        url = upload_to_s3(bucket, thumbnail_key, thumbnail)
        return url

def get_s3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    imagecontent = response['Body'].read()

    file = io.BytesIO(imagecontent)
    img = Image.open(file)
    return img

def image_to_thumbnail(image):
    #return ImageOps.fit(image, (size, size), Image.ANTIALIAS)
    return ImageOps.fit(image, (size, size), Image.LANCZOS)

def new_filename(key):
    key_split = key.rsplit('.', 1)
    return key_split[0] + "_thumbnail." + key_split[1]

def upload_to_s3(bucket, key, image):
    # We're saving the image into a cStringIO object to avoid writing to disk
    out_thumbnail = io.BytesIO()
    # You MUST specify the file type because there is no file name to discern
    # it from
    file_extension = key.rsplit('.', 1)[1].upper()
    image.save(out_thumbnail, file_extension)
    out_thumbnail.seek(0)

    response = s3.put_object(
        ACL='public-read',
        Body=out_thumbnail,
        Bucket=bucket,
        ContentType='image/{}'.format(file_extension.lower()),
        Key=key
    )
    print(response)

    url = '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key)
    return url
