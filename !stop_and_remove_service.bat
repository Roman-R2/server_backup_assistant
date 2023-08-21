set WIN_SERVICE_NAME=server-watcher-assistant-win-service.exe

cd %~dp0
:: echo Stop R2ZiD server assistant service...
%~dp0%WIN_SERVICE_NAME% stop
:: echo Remove R2ZiD server assistant service...
%~dp0%WIN_SERVICE_NAME% remove
pause