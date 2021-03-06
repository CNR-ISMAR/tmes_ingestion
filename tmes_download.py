#!/usr/bin/env python3

import os, sys
import shutil
import requests
from requests.auth import HTTPBasicAuth

from datetime import datetime, timedelta
from ftplib import FTP


# general variables

now = datetime.now()
one_day_ago = now -timedelta(days=1)
today = now.strftime("%Y%m%d")




#today = '20200909'

#Please make a connection to ftp.arso.gov.si
#Username: Istorms
#Password:  ModelZaOcean18

#download a source  via ftp login


def download_ftp(source, model, tmpdir, filename, filedate=today):
    remotefile = model['filename'].format(prefix=source['prefix'], name=model['name'], var=model['var'], currentdate=filedate, ext=model['ext'], engine=model['engine'])
    filedir = os.path.dirname(filename)
    if not os.path.isdir(filedir):
        os.mkdir(filedir, 775)
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir, 775)
    with FTP(source['url']) as ftp:
        try:
            #test connection
            FTP(source['url'])
            ftp.login(source['username'], source['password'])
        except:
            print('could not connect to ' + source['url'])
            return
        if os.path.isfile(filename):
            print('file ' + filename + '\n already exists skipping')
        else:
            #remote dir change
            try:
                 ftp.cwd(source['ftp_dir'])
                 _list = ftp.nlst()
            except:
                print('Remote Dir not found')
                return
            #parse list of files in remote dir
            for i in _list:
                if str(i).strip().lower()==remotefile:
                    print('Downlading ' + i )
                    try:
                        ftp.retrbinary('RETR ' + i, open(tmpdir+ i, 'wb').write)
                        print('done')
                    except:
                        print('error on ftp download')
                        pass
                    try:
                        shutil.copy2(tmpdir + i, filename)
                        print('File copied as ' + filename)
                    except:
                        print('error on copying file')
                    try:
                        os.remove(tmpdir+ i)
                        print(tmpdir + i + ' removed')
                    except:
                        print(tmpdir + i + ' not removed')



def download_http(source, model, filename, filedate=today, progress=False):
    """

    :rtype: object
    """

    if source['type'] == 'http_login':
        template = model['filename']
        fileisodate = filedate[0:4] + '-' + filedate[4:6] + '-' + filedate[6:8]
        remotefile = model['filename'].format(prefix=source['prefix'],
                                              name=model['name'],
                                              engine=model['engine'],
                                              var=model['var'],
                                              currentdate=filedate,
                                              currentisodate=fileisodate,
                                              ext=model['ext']
                                              )
        print(source['url'] + remotefile)
        #TODO add basic autehntication in TDS
        sourceauth = HTTPBasicAuth(source['username'], source['password'])
        if os.path.isfile(filename):
            print('file ' + filename + ' already exists skipping')
        else:
            filedir=os.path.dirname(filename)
            if not os.path.isdir(filedir):
                os.mkdir(filedir, 775)
            with requests.get(source['url'] + remotefile, auth=sourceauth, stream=True) as r:
                total_length = r.headers.get('content-length')
                if r.status_code == 200:
                    print('Downloading')
                    with open(filename, 'wb') as fd:
                        dl = 0
                        total_length = int(total_length)
                        for chunk in r.iter_content(chunk_size=128):
                            dl += len(chunk)
                            fd.write(chunk)
                            done = int(50 * dl / total_length)
                            if progress==True:
                                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                                sys.stdout.flush()
                        print('\n')
                else:
                    print(source['url'] + remotefile + ' get a status code of ' + str(r.status_code))






