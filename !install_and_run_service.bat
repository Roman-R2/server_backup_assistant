set WIN_SERVICE_NAME=server-watcher-assistant-win-service.exe

cd %~dp0
:: echo Install R2ZiD server assistant service...
%~dp0%WIN_SERVICE_NAME% --startup auto install
:: echo Start R2ZiD server assistant service...
%~dp0%WIN_SERVICE_NAME% start
:: echo Debug R2ZiD server assistant service...
:: app-build\service\dist\r2zid-server-assistant-win-service\r2zid-server-assistant-win-service.exe debug
pause