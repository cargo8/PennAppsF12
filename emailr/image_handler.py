from boto.s3.connection import S3Connection
from boto.s3.key import Key
import time
import random


def save_image(instream):
	conn = S3Connection()
	print "Before 1"
	bucket = conn.get_all_buckets()[0]
	print "After 1"
	k = Key(bucket)
	k.key = str((time.time() % 1000 * 5000 + random.randint(0,5000)) / 100)[-10:] + '.jpg'
	print "After 1]2"
	k.set_contents_from_string(instream.read())
	print "Before return  1"
	return k.generate_url(10000)