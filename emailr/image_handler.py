from boto.s3.connection import S3Connection
from boto.s3.key import Key
import time
import random


def save_image(instream):
	conn = S3Connection()
	bucket = c.lookup('emailr_file_storage')
	key(bucket)
	k.key = str(time.localtime()) + str(random.randint(0,5000))
	key.send_file(instream)
	return key.generate_url(100000000)