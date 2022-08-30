import boto3 
s3_client = boto3.client('s3')
s3 = boto3.resource('s3')
my_bucket = s3.Bucket('imdbwebscraper')

def create_bucket_directory(dir_name):
    """Creates a directory in the AWS S3 Bucket
    
    Parameters
    ----------
    dir_name: str
        The name of the directory to be created

    """
    s3_client.put_object(Bucket='imdbwebscraper', Key=f"{dir_name}/")

def upload_to_bucket(local_file_path, bucket_file_path):
    """Uploads a file to the AWS S3 Bucket
    
    Parameters
    ----------
    local_file_path: str
        The file path on the local computer where the file to upload is located
    bucket_file_path: str
        The file path in the bucket to where the file will be uploaded

    """
    my_bucket.upload_file(local_file_path, bucket_file_path)

def folder_exists(path:str) -> bool:
    """Checks if a folder in the AWS S3 Bucket with a specified name already exists
    
    Parameters
    ----------
    path: str
        The path of the directory to be checked

    Returns
    -------
    bool
        True if the directory exists

    """
    path = path.rstrip('/')
    resp = s3_client.list_objects(Bucket='imdbwebscraper', Prefix=path, Delimiter='/',MaxKeys=1)
    return 'CommonPrefixes' in resp

