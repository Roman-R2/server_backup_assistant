set WIN_SERVICE_NAME=server-watcher-assistant-win-service.exe

cd %~dp0
:: echo Debug R2ZiD server assistant service...
%~dp0%WIN_SERVICE_NAME% debug
pause