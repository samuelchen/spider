#!/usr/bin/env python
# coding: utf-8
__author__ = 'Samuel Chen <samuel.net@gmail.com>'

import os, uuid, sys
from azure.storage.blob import BlockBlobService, PublicAccess
from conf import AzureConf


class AzureSyncManager(object):

    blob_bucket = 'https://novels.blob.core.windows.net/reader/'
    container = 'reader'

    def __init__(self, acc_name, acc_key, blob_container, local_static_root):
        self.block_blob_service = BlockBlobService(account_name=acc_name, account_key=acc_key)
        self.blob_container = blob_container
        self.local_static_root = local_static_root

    def sync_albums(self):
        prefix = 'albums'
        remote_blobs = self.block_blob_service.list_blobs(self.blob_container, prefix=prefix)
        local_files = set(os.listdir(self.local_static_root))
        print(local_files)
        remote_files = set()
        for blob in remote_blobs:
            fname = blob.name.split('/')
            fname = fname[1]
            remote_files.add(fname)
        print(remote_files)

        ex_files = local_files - remote_files
        print(ex_files)

        for fname in ex_files:
            full_path = os.path.join(self.local_static_root, fname)
            try:
                self.block_blob_service.create_blob_from_path(self.blob_container, os.path.join(prefix, fname),
                                                              full_path)
            except Exception as err:
                print(err)
#
# def run_sample():
#     try:
#         # Create the BlockBlockService that is used to call the Blob service for the storage account
#         block_blob_service = BlockBlobService(account_name='accountname', account_key='accountkey')
#
#         # Create a container called 'quickstartblobs'.
#         container_name ='quickstartblobs'
#         block_blob_service.create_container(container_name)
#
#         # Set the permission so the blobs are public.
#         block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)
#
#         # Create a file in Documents to test the upload and download.
#         local_path=os.path.expanduser("~/Documents")
#         local_file_name ="QuickStart_" + str(uuid.uuid4()) + ".txt"
#         full_path_to_file =os.path.join(local_path, local_file_name)
#
#         # Write text to the file.
#         file = open(full_path_to_file,  'w')
#         file.write("Hello, World!")
#         file.close()
#
#         print("Temp file = " + full_path_to_file)
#         print("\nUploading to Blob storage as blob" + local_file_name)
#
#         # Upload the created file, use local_file_name for the blob name
#         block_blob_service.create_blob_from_path(container_name, local_file_name, full_path_to_file)
#
#         # List the blobs in the container
#         print("\nList blobs in the container")
#         generator = block_blob_service.list_blobs(container_name)
#         for blob in generator:
#             print("\t Blob name: " + blob.name)
#
#         # Download the blob(s).
#         # Add '_DOWNLOADED' as prefix to '.txt' so you can see both files in Documents.
#         full_path_to_file2 = os.path.join(local_path, str.replace(local_file_name ,'.txt', '_DOWNLOADED.txt'))
#         print("\nDownloading blob to " + full_path_to_file2)
#         block_blob_service.get_blob_to_path(container_name, local_file_name, full_path_to_file2)
#
#         sys.stdout.write("Sample finished running. When you hit <any key>, the sample will be deleted and the sample "
#                          "application will exit.")
#         sys.stdout.flush()
#         input()
#
#         # Clean up resources. This includes the container and the temp files
#         block_blob_service.delete_container(container_name)
#         os.remove(full_path_to_file)
#         os.remove(full_path_to_file2)
#     except Exception as e:
#         print(e)


# Main method.
if __name__ == '__main__':
    # run_sample()
    azure_syncmgr = AzureSyncManager(AzureConf.ACCOUNT_NAME, AzureConf.ACCOUNT_KEY,
                                     AzureConf.BLOB_CONTAINER, AzureConf.LOCAL_STATIC_ROOT)

    azure_syncmgr.sync_albums()