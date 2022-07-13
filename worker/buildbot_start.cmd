@echo off
:: Start the worker, which is configured with allow_shutdown = 'file'
:: Once a single test is done, it will initiate a graceful shutdown of the worker.
start /wait C:\Python27\Scripts\buildbot-worker.exe start C:\buildbot_config\worker
 
:: Reboot for a clean next test run
shutdown -r -t 0
