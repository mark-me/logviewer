set original_dir=%CD%
set venv_root_dir=".venv"

call %venv_root_dir%\Scripts\activate.bat

python main.py

call %venv_root_dir%\Scripts\deactivate.bat

cd %original_dir%

exit /B 1