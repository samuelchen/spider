#!/usr/bin/env python
# coding: utf-8
__author__ = 'Samuel Chen <samuel.net@gmail.com>'

import os, uuid, sys
from azure.storage.blob import BlockBlobService, PublicAccess
from conf import AzureConf


class AzureSyncManager(object):

    # blob_bucket = 'https://novels.blob.core.windows.net/reader/'
    container = 'reader'

    def __init__(self, acc_name, acc_key, blob_container, local_static_root):
        self.block_blob_service = BlockBlobService(account_name=acc_name, account_key=acc_key)
        self.blob_container = blob_container
        self.local_static_root = local_static_root.rstrip('/\\')

    def sync_albums(self):
        prefix = 'albums'
        local_path = os.path.join(self.local_static_root, prefix)
        print('Local albums path: ' + local_path)

        local_files = set(os.listdir(local_path))
        print('local files: ', local_files)

        remote_blobs = self.block_blob_service.list_blobs(self.blob_container, prefix=prefix)
        remote_files = set()
        for blob in remote_blobs:
            fname = blob.name.split('/')
            fname = fname[1]
            remote_files.add(fname)
        print('remote blobs: ', remote_files)

        ex_files = local_files - remote_files
        print(ex_files)

        for fname in ex_files:
            full_path = os.path.join(local_path, fname)
            try:
                print(full_path)
                self.block_blob_service.create_blob_from_path(self.blob_container, os.path.join(prefix, fname), full_path)
            except Exception as err:
                print(err)
#

    def sync_folder(self, folder, del_remote=False, del_local=False):
        root_path = os.path.join(self.local_static_root, folder)
        print('Local folder path: ' + root_path)

        prefix = ''
        local_files = set()
        for root, dirs, files in os.walk(root_path, followlinks=True):
            print('-' * 70)
            head = root
            prefix = ''
            while head != self.local_static_root:
                head, tail = os.path.split(head)
                prefix = '/'.join([tail, prefix])
            files = set(prefix + name for name in files)
            print(prefix)
            print('files:', files)
            local_files.update(files)

        print('='*70)
        remote_blobs = self.block_blob_service.list_blobs(self.blob_container, prefix=folder)
        remote_files = set(blob.name for blob in remote_blobs)
        print('local files:', local_files)
        print('remote blobs: ', remote_files)


        print('='*70)
        local_extra = local_files - remote_files
        remote_extra = remote_files - local_files
        # print('new files:', new_files)
        # print('del files:', del_files)

        for fname in local_extra:
            local_path = os.path.join(self.local_static_root, fname)
            remote_path = fname
            try:
                if del_local:
                    print(' ^^ \tDEL\t', local_path, ' <-- ', '(remote)')
                    os.remove(local_path)
                else:
                    print(' ^^ \tUPLOAD\t', local_path, ' --> ', remote_path)
                    self.block_blob_service.create_blob_from_path(self.blob_container, remote_path, local_path)
            except Exception as err:
                print(err)

        for fname in remote_extra:
            local_path = os.path.join(self.local_static_root, fname)
            remote_path = fname
            try:
                if del_remote:
                    print(' xx \tDEL\t', '(local)', ' --> ', remote_path)
                    self.block_blob_service.delete_blob(self.blob_container, remote_path)
                else:
                    print(' ^^ \tDOWNLOAD\t', local_path, ' <-- ', remote_path)
                    self.block_blob_service.get_blob_to_path(self.blob_container, remote_path, local_path)
            except Exception as err:
                print(err)

# Main method.
if __name__ == '__main__':
    # run_sample()
    azure_syncmgr = AzureSyncManager(AzureConf.ACCOUNT_NAME, AzureConf.ACCOUNT_KEY,
                                     AzureConf.BLOB_CONTAINER, AzureConf.LOCAL_STATIC_ROOT)

    folder = ''
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        print('You are synchronizing %s folder.' % os.path.join(AzureConf.LOCAL_STATIC_ROOT, folder))
    else:
        folder = ''
        print('You are synchronizing FULL %s folders !!' % AzureConf.LOCAL_STATIC_ROOT)
    if input('Sure to sync ? (yes/no)').lower() == 'yes':
        azure_syncmgr.sync_folder(folder, del_remote=True, del_local=False)
    else:
        print('abort.')
        exit(1)

