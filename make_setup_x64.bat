@echo off

call "make_package_base.bat"

@echo off

IF %result%=="false" (
    goto break
)

python setup.py py2exe

set /p var= <version

makensis.exe /DVERSION=%var% /DGIT=%git_commit_id% /DAUTHOR=%git_user_name% /DTIME=%timestamp% setup_x64.nsi

:break
@echo on
