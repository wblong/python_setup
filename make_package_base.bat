@echo off

:: 1. prepare
:: git commit id
:: SET git_version_cmd="git describe --abbrev=7 --dirty --always --tags"
SET git_version_cmd="git describe --abbrev=7 --always --tags"
FOR /F "tokens=*" %%i IN (' %git_version_cmd% ') DO SET git_commit_id=%%i

:: include dirty?
Echo.%git_commit_id% | findstr /C:"dirty">nul && (
    @echo on
    Echo "Hi Guy, your operator was canceled due to local modifications that were not commit to git repository!"
    @echo off
    SET result="false"
    goto end
)

SET result="true"

:: git username
FOR /F "tokens=*" %%i IN (' git config user.name ') DO SET git_user_name=%%i

:: git branch name
FOR /F "tokens=*" %%i IN (' git symbolic-ref --short -q HEAD ') DO SET git_branch_name=%%i

:: 2. system timestamp
SET hour=%time:~0,2%

IF "%hour:~0,1%"==" " (
	SET hour_prefix=0
) ELSE (
	SET hour_prefix="%hour:~0,1%"
)
SET hour=%hour_prefix%%hour:~1,1%

SET timestamp=%date:~0,4%%date:~5,2%%date:~8,2%%hour%%time:~3,2%%time:~6,2%

:end
@echo on