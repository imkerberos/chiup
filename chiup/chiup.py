#!/usr/bin/env python #-*- coding: utf-8 -*-
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import os
import sys
import socket
import platform
import ConfigParser
import httplib
from urllib2 import urlopen, Request, HTTPError
from base64 import standard_b64encode
import urlparse
import cStringIO as StringIO
import zipfile

from pkgtools.pkg import Egg, EggDir

def zip_folder (dir_path):
    contents = os.walk (dir_path)
    zm = StringIO.StringIO ()
    zip = zipfile.ZipFile (zm, 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in contents:
        for x in files:
            relp = os.path.relpath (root, dir_path)
            zip.write (os.path.join (root, x), os.path.join (relp, x))
    zip.close ()
    return zm

class Chiup (object):
    def __init__ (self, repos, site, username, password):
        self.rcsection = repos
        self.username = username
        self.password = password
        self.repository = site
        self._readrc ()

    def _readrc (self):
        if os.environ.has_key ('HOME'):
            rc = os.path.join (os.environ['HOME'], '.pypirc')
            if os.path.exists (rc):
                print >> sys.stderr, 'Using PyPI login from %s' % rc
                config = ConfigParser.ConfigParser ({
                    'username' : '',
                    'password' : '',
                    'repository' : '',
                    })
                config.read (rc)

                if not self.repository:
                    self.repository = config.get (self.rcsection, 'repository')
                if not self.username:
                    self.username = config.get (self.rcsection, 'username')
                if not self.password:
                    self.password = config.get (self.rcsection, 'password')

    def upload (self, egg_file):
        try:
            if os.path.isdir(egg_file):
                eggfile = EggDir (egg_file)
                content = zip_folder (egg_file).getvalue()
            else:
                eggfile = Egg (egg_file)
                content = open (egg_file, 'rb').read ()
        except Exception, e:
            raise e

        if egg_file[-1] == os.path.sep:
            basename = os.path.basename (egg_file[:-1])
        else:
            basename = os.path.basename (egg_file)

        data = {
                ':action' : 'file_upload',
                'protcol_version' : '1',
                'name' : eggfile.name,
                'version' : eggfile.version,
                'content' : (basename, content),
                'filetype' : 'bdist_egg',
                'pyversion' : '%s.%s' % (sys.version_info[0], sys.version_info[1]),
                'md5_digest' : md5 (content).hexdigest(),
                'metadata_version' : '1.0',
                'summary' : eggfile.pkg_info.get ('Summary', ''),
                'home_page' : eggfile.pkg_info.get ('Home-page', ''),
                'author' : eggfile.pkg_info.get ('Author', ''),
                'author_email' : eggfile.pkg_info.get ('Author-email', ''),
                'license' : eggfile.pkg_info.get ('License', ''),
                'description' : eggfile.pkg_info.get ('Description', ''),
                'keywords' : eggfile.pkg_info.get ('Keywords', ''),
                'platform' : eggfile.pkg_info.get ('Platform', ''),
                'classifiers' : eggfile.pkg_info.get ('Classifier', ''),
                'download_url' : eggfile.pkg_info.get ('Download-url', ''),
        }
        
        auth = 'Basic ' + standard_b64encode (self.username + ":" + self.password)
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'

        sep_boundary = '\n--' + boundary
        end_boundary = sep_boundary + '--'

        body = StringIO.StringIO()
        for key, value in data.items ():
            if not isinstance (value, list):
                value = [value]
            for value in value:
                if isinstance (value, tuple):
                    fn = ';filename="%s"' % value[0]
                    value = value[1]
                else:
                    fn = ""

                body.write (sep_boundary)
                body.write ('\nContent-Disposition: form-data; name="%s"' % key)
                body.write (fn)
                body.write ("\n\n")
                body.write (value)
                if value and value[-1] == '\r':
                    body.write ("\n")

        body.write (end_boundary)
        body.write ("\n")
        body = body.getvalue ()

        print 'Submitting %s to %s' % (egg_file, self.repository)
        headers = {
                'Content-Type' : 'multipart/form-data; boundary=%s' % boundary,
                'Content-Length' : str (len(body)),
                'Authorization' : auth,
                }
        request = Request (self.repository, data=body, headers = headers)
        try:
            result = urlopen (request)
            status = result.getcode ()
            reason = result.msg
        except socket.error, e:
            print 'error: %s' % str (e)
            return
        except HTTPError, e:
            status = e.code
            reason = e.msg

        if status == 200:
            print 'Upload success!'
        else:
            print >> sys.stderr,  'Upload %s error: %s, %s' % (egg_file, status, reason)

def main ():
    from optparse import OptionParser
    usage = "usage: %prog [options] egg1 egg2 ..."
    parser = OptionParser (usage = usage)
    parser.add_option ('-r', '--repository', action = 'store', type = 'string', dest = 'repository', help = 'The repository in ~/.pypirc')
    parser.add_option ('-s', '--site', action = 'store', type = 'string', dest = 'site', help = 'The url will upload to')
    parser.add_option ('-u', '--username', action = 'store', type = 'string', dest = 'username', help = 'The username for repository will upload to.')
    parser.add_option ('-p', '--password', action = 'store', type = 'string', dest = 'password', help = 'The password of username')

    options, args = parser.parse_args ()

    chiup = Chiup (options.repository, options.site, options.username, options.password)

    if not len (args):
        parser.print_help ()
        sys.exit (1)
    for x in args:
        chiup.upload (x)

if __name__ == '__main__':
    main ()
