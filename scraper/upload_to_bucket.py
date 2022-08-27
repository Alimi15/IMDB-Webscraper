import boto3 
s3_client = boto3.client('s3')
s3 = boto3.resource('s3')
my_bucket = s3.Bucket('imdbwebscraper')

def create_bucket_directory(dir_name):
    s3_client.put_object(Bucket='imdbwebscraper', Key=f"{dir_name}/")

def upload_to_bucket(local_file_path, bucket_file_path):
    my_bucket.upload_file(local_file_path, bucket_file_path)

def folder_exists(path:str) -> bool:
    path = path.rstrip('/')
    resp = s3_client.list_objects(Bucket='imdbwebscraper', Prefix=path, Delimiter='/',MaxKeys=1)
    return 'CommonPrefixes' in resp

