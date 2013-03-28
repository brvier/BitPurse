#!/usr/bin/python
# -*- coding: utf-8 -*-

#KhtNotes Setup File
import sys
import os
reload(sys).setdefaultencoding("UTF-8")

from distutils.core import setup


#Remove temporary files
for root, dirs, fs in os.walk(os.path.join(os.path.dirname(__file__),
                                           'bitpurse')):
    for filename in [filename for filename
                     in fs if filename.endswith(('~', '.pyo', '.pyc', ))]:
        os.remove(os.path.join(root, filename))

files = []
for root, dirs, filenames in os.walk(os.path.join(os.path.dirname(__file__),
                                                  'bitpurse')):
    files.append((os.path.join('/opt', root),
                  [os.path.join(root, filename)
                  for filename in filenames]))

print files

setup(name='bitpurse',
      version='1.9.0',
      license='GNU GPLv3',
      description='A nice looking Blockchain.info Bitcoin Wallet Client',
      long_description=("A nice looking Bitcoin Wallet client"
                        " for MeeGo, SailfishOS, NemoMobile, and Harmattan."),
      author=u'Benoît HERVIER',
      author_email='khertan@khertan.net',
      maintainer=u'Benoît HERVIER',
      maintainer_email='khertan@khertan.net',
      url='http://www.khertan.net/BitPurse',
      requires=['python', 'pyside', 'pycrypto'],


      data_files=[('/usr/share/dbus-1/services', ['net.khertan.bitpurse.service']),
                  ('/usr/share/applications/', ['bitpurse.desktop']),
                  ('/usr/share/icons/hicolor/80x80/apps', ['bitpurse.png']),
                  ('/usr/share/icons/hicolor/128x128/apps',
                   ['bitpurse_128.png']),
                  ('/usr/share/icons/hicolor/64x64/apps', ['bitpurse_64.png']),
                  ('/usr/share/icons/hicolor/scalable/apps', ['bitpurse.svg']),
                  ] + files,
      )  
