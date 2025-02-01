7D2D Utils
========

This projects provides a command line interface made in python, to manage 7 days to die modding projects.

It provides usefull command for:

* Automating mods build processes, (with or without C# dll)
* creating and configuring new modding project quickly
* Starting a local game session, or with a local dedicated server

Requirements
------------

* Windows 10+
* [python 3.11+](https://www.python.org/downloads/)
* [.NET Framework 4.8+](https://dotnet.microsoft.com/fr-fr/download)


Installation
------------

Cloning the repository
```
cd path/to/7D2D-utils
git clone https://github.com/VisualDev-FR/7D2D-Utils
```

Adding the path to the [bin directory](./bin) of the cloned repository to your `PATH` environement variable

* windows search bar/modify environement variables for your account
* user variables for `your_username`/path/edit/new
* then enter the path to `path/to/cloned/respository/bin`
* close all window by clicking `OK`

to check installation, open a new terminal the run `7D_UTILS`, it should display the cli help text.


Configuration
------------

``` json
{
    "PATH_7D2D": "path/to/dir/steamapps/common/7 Days To Die",
    "PATH_7D2D_EXE": "path/to/file/steamapps/common/7 Days To Die/7DaysToDie.exe",
    "PATH_7D2D_SERVER": "path/to/file/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer.exe",
    "PATH_7D2D_USER": "path/to/dir/AppData/Roaming/7DaysToDie"
}
```