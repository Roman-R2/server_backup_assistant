include .env
export

check-code:
	isort services/ main.py
	flake8 --extend-ignore E501,F401 services/ main.py

test-code:
	python -m unittest discover -v -s tests -p '*_test.py'

clean-app-build-dir:
	rmdir /S /Q "app-build\"
	mkdir "./app-build"
	mkdir "./app-build/gui"
	mkdir "./app-build/service"
	mkdir "./app-build/compile-app"

create-versionfile:
	python create-gui-versionfile.py

gui-app-build:
	pyinstaller \
	--specpath ./app-build/gui/spec \
	--distpath ./app-build/gui/dist \
	--workpath ./app-build/gui/build \
	--noconfirm \
	--onedir \
	--windowed \
	--version-file=../${VERSIONFILE_GUI_NAME} \
	--icon="../../../assets/icons/app.ico" \
	--add-data "../../../.env;." \
	--add-data "../../../assets;assets/" \
	--add-data "../../../customtkinter;customtkinter/" \
	--add-data "../../../db/.gitkeep;db" \
	--add-data "../../../db/assistant.sqlite3;db/." \
	--add-data "../../../logs/server_assistant_gui_logs/.gitkeep;logs/server_assistant_gui_logs" \
	--add-data "../../../logs/server_assistant_windows_service_logs/.gitkeep;logs/server_assistant_windows_service_logs" \
	--add-data "../../../data/default_server_url.txt;data" \
	--add-data "../../../!install_and_run_service.bat;." \
	--add-data "../../../!stop_and_remove_service.bat;." \
	--add-data "../../../!debug_service.bat;." \
	-n ${ASSISTANT_NAME_GUI} \
	main-gui.py

service-app-build:
	pyinstaller.exe \
	--specpath ./app-build/service/spec \
	--distpath ./app-build/service/dist \
	--workpath ./app-build/service/build \
	--onedir \
	--runtime-tmpdir=. \
	--hidden-import win32timezone \
	--version-file=../${VERSIONFILE_SERVICE_NAME} \
	--icon="../../../assets/icons/app.ico" \
	--add-data "../../../.env;." \
	--add-data "../../../assets;assets/" \
	--add-data "../../../customtkinter;customtkinter/" \
	--add-data "../../../db/.gitkeep;db" \
	--add-data "../../../logs/server_assistant_gui_logs/.gitkeep;logs/server_assistant_gui_logs" \
	--add-data "../../../logs/server_assistant_windows_service_logs/.gitkeep;logs/server_assistant_windows_service_logs" \
	--add-data "../../../data/default_server_url.txt;data" \
	-n ${ASSISTANT_NAME_SERVICE} \
	main-win-service.py

full-app-build: clean-app-build-dir create-versionfile gui-app-build service-app-build
	python create-versionfile-to-app-dir.py
	python copy-app-to-common-folder.py




