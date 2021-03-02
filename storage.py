import logging
import os
import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity
#[END imports]

#[START retries]
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)
#[END retries]


class MainPage(webapp2.RequestHandler):
  """Main page for GCS demo application."""

#[START get_default_bucket]
  def get(self):
    bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Demo GCS Application running from Version: '
                        + os.environ['CURRENT_VERSION_ID'] + '\n')
    self.response.write('Using bucket name: ' + bucket_name + '\n\n')
#[END get_default_bucket]

    bucket = '/' + bucket_name
    filename = bucket + '/demo-testfile'
    self.tmp_filenames_to_clean_up = []

    try:
      self.create_file(filename)
      self.response.write('\n\n')

      self.read_partial_file(filename)
      self.response.write('\n\n')
      
      self.read_file(filename)
      self.response.write('\n\n')

      self.stat_file(filename)
      self.response.write('\n\n')

      self.create_files_for_list_bucket(bucket)
      self.response.write('\n\n')

      self.list_bucket(bucket)
      self.response.write('\n\n')

      self.list_bucket_directory_mode(bucket)
      self.response.write('\n\n')

    except Exception, e:
      logging.exception(e)
      self.delete_files()
      self.response.write('\n\nThere was an error running the demo! '
                          'Please check the logs for more details.\n')

    else:
      self.delete_files()
      self.response.write('\n\nThe demo ran successfully!\n')

#[START write]
  def create_file(self, filename):
    """Create a file.
    The retry_params specified in the open call will override the default
    retry params for this particular file handle.
    Args:
      filename: filename.
    """
    self.response.write('Creating file %s\n' % filename)

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file = gcs.open(filename,
                        'w',
                        content_type='text/plain',
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params)
    gcs_file.write('abcde\n')
    gcs_file.write('f'*1024*4 + '\n')
    gcs_file.close()
    self.tmp_filenames_to_clean_up.append(filename)
#[END write]

#[FIRST upload]
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    logger.info(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
#[END upload]