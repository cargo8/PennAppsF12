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
	k.key = str(time.localtime()) + str(random.randint(0,5000))
	print "After 1]2"
	k.send_file(instream)
	print "Before return  1"
	return k.generate_url(100000000)