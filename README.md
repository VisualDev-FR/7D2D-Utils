# 7D2D Utils

This projects provides a command line interface made in python, to manage 7 days to die modding projects.

It provides usefull command for:

* Automating mods build processes, (with or without C# dll)
* creating and configuring new modding project quickly
* Starting a local game session, or with a local dedicated server

## Requirements

* Windows 10+
* [python 3.11+](https://www.python.org/downloads/)
* [.NET Framework 4.8+](https://dotnet.microsoft.com/fr-fr/download) (for building dll mods only)
* [git 2.32+](https://git-scm.com/downloads) (for auto updates only)


## Installation

Cloning the repository
```
cd path/to/7D2D-utils
git clone https://github.com/VisualDev-FR/7D2D-Utils
```

Adding the path of the [bin directory](./bin) to your environement variable `PATH`

* windows search bar/modify environement variables for your account
* user variables for `your_username`/path/edit/new
* then enter the path to `path/to/cloned/respository/bin`
* close all window by clicking `OK`

to check installation, open a new terminal the run `7D_UTILS`, it should display the cli help text.


## 7D-Utils Configuration (config.json)

Once installed, you'll need to configure the app through the file `config.json`

You can also override these variables from any `build.json` file of a modding project, to work on a specific game version.

``` json
{
    "PATH_7D2D": "path/to/dir/steamapps/common/7 Days To Die",
    "PATH_7D2D_EXE": "path/to/file/steamapps/common/7 Days To Die/7DaysToDie.exe",
    "PATH_7D2D_SERVER": "path/to/file/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer.exe",
    "PATH_7D2D_USER": "path/to/dir/AppData/Roaming/7DaysToDie"
}
```


## Mod build Configuration (build.json)

Modding projects must have their own `build.json` file.

This file must be placed in the root directory of the modding project, and will be used to configure how the mod must be built, here is an example of a `build.json` file:

```json
{
    "name": "cave-prefabs",
    "csproj": null,
    "zip_name": "",
    "include": [
        "ModInfo.xml",
        "Config",
        "Prefabs"
    ],
    "prefabs": [
        "relative/path/from/userdata/LocalPrefabs/*.*"
    ],
    "dependencies": [
        "../relative/path/to/dependency-1",
    ]
}
```

* `name`

    name of the project, used to auto-fill ModInfow.xml, code snippets and for zip archive file

    ```json
    "name": "my-mod-name"
    ```

* `csproj` [Optional]

    name of the csproj to build, null if there is no dll to build

    ```jsonc
    "csproj": null | "my-mod.csproj"
    ```

* `zip_name` [Optional]

    allow to override the name of the zip archive. The `.zip` extension must **NOT** be provided here

    ```jsonc
    "zip_name": null | "custom-zip-name"
    ```

* `Include`

    Files to copy and to include in the release archive.

    ```json
    "include": [
        "ModInfo.xml",
        "Config",
        "Prefabs"
    ]
    ```

* `prefabs`

    ```json
    "prefabs": [
        "relative/path/from/userdata/LocalPrefabs/*.*"
    ]
    ```

* `dependencies`

    ```json
    "dependencies": [
        "../relative/path/to/dependency-1",
        "C:/absolute/path/to/dependency-2"
    ]
    ```