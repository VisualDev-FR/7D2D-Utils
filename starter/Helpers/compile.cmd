@echo off

set MOD_NAME=@MODNAME

if not defined PATH_7D2D (
    echo Missing env variable: 'PATH_7D2D'
    exit /b 1
)

set MOD_PATH=%PATH_7D2D%\Mods\%MOD_NAME%

dotnet build --no-incremental

if ERRORLEVEL 1 exit /b 1

if exist "%MOD_NAME%.zip" DEL "%MOD_NAME%.zip"

if exist ".\%MOD_NAME%" rmdir ".\%MOD_NAME%" /s /q

MKDIR .\%MOD_NAME%

xcopy %MOD_NAME%.dll %MOD_NAME%\ > nul
xcopy %MOD_NAME%.pdb %MOD_NAME%\ > nul
xcopy README.md %MOD_NAME%\ > nul
xcopy ModInfo.xml %MOD_NAME%\ > nul
xcopy UIAtlases %MOD_NAME%\UIAtlases\ /s > nul
xcopy Resources %MOD_NAME%\Resources\ /s > nul
xcopy Config %MOD_NAME%\Config\ /s > nul

7z.exe a "%MOD_NAME%.zip" %MOD_NAME% > nul

rmdir ".\%MOD_NAME%" /s /q

DEL *.dll
DEL *.pdb
