import os

from twisted.application import service
from buildslave.bot import BuildSlave

basedir = r'/srv/buildbot_cmake'
rotateLength = 10000000
maxRotatedFiles = 10

# note: this line is matched against to check that this is a buildslave
# directory; do not edit it.
application = service.Application('buildslave')

try:
  from twisted.python.logfile import LogFile
  from twisted.python.log import ILogObserver, FileLogObserver
  logfile = LogFile.fromFullPath(os.path.join(basedir, "twistd.log"), rotateLength=rotateLength,
                                 maxRotatedFiles=maxRotatedFiles)
  application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
except ImportError:
  # probably not yet twisted 8.2.0 and beyond, can't set log yet
  pass

buildmaster_host = 'build.reactos.org'
port = 9989
slavename = 'SLAVENAME_HERE'
passwd = 'PASSWORD_HERE'
keepalive = 60
usepty = 1
umask = 022
maxdelay = 30

s = BuildSlave(buildmaster_host, port, slavename, passwd, basedir,
               keepalive, usepty, umask=umask, maxdelay=maxdelay)
s.setServiceParent(application)
