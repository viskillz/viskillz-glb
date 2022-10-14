# `viskillz-glb`

The aim of package `viskillz-glb` is to encode GLB assets representing Mental Cutting Test exercises, created with the use of our [`viskillz-blender`](https://github.com/viskillz/viskillz-blender) package.

## Setup

### Install a Python interpreter

We recommend two options to download and install a Python interpreter:

* [Download](https://www.python.org/downloads/) and install a Python interpreter directly.
* [Download](https://docs.conda.io/en/latest/miniconda.html) Miniconda and create an environment 

    1. Create an environment with name `mct` (the name can be changed):

        ```
        conda create --name mct python=3.10
        ```
    2. Activate the environment (to access command `pip` in command-line):

        ```
        conda activate mct
        ```
    
    For further commands and configuration, see the official [Conda Cheat Sheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf).

### Install packages

We have added the dependencies to file [`requirements.txt`](requirements.txt). Thus, you can install the requirements using the following `pip` command:

```
pip -r requirements.txt
```

Alternatively, you can install the dependencies manually:

1. Install package [`viskillz-common`](https://github.com/viskillz/viskillz-common)

    The wrapper script uses functions of our package `viskillz-common`. Thus, install this package directly from our GitHub repository, using the following `pip` command:

    ```
    pip install git+https://github.com/viskillz/viskillz-common#egg=viskillz-common
    ```

1. Install package [`wakepy`](https://github.com/np-8/wakepy)

    To prevent your computer from falling asleep during the rendering or exporting process, we use package `wakepy` in the wrapper script. Install this package using the following `pip` command:

    ```
    pip install wakepy
    ```

### Install the package

The easiest way to install our package is to execute the following `pip` command, downloading the latest version from our GitHub repository:

```
pip install git+https://github.com/viskillz/viskillz-glb#egg=viskillz-glb
```


### The reference environment

Our package was developed and tested in an environment having the following properties:

* Conda version: 4.14.0
* Python interpreter version: 3.10.6
* `wakepy` version: 0.5.0
* OS: Windows 11 Home

## Usage

### Runner

Our package contains a command-line runner, that can be invoked using the following command:

```
viskillz-glb <path-of-configuration>
```

### Goals

With the use of the command-line runner, users can specify their workflow in a JSON document, specifying the following goals:

* `material` - Adds the reference material to the given group(s) of assets. The material is defined in module `viskillz.mct.glb.constants`.

    Parameters:

    * `src`: the path of the folder that contains the original assets
    * `dist`: the path of the folder in which the script writes the assets having the new material
    * `groups`: the list of IDs specifying that which groups should be processed

    Example:

    ```json
    {
        "type": "material",
        "src": "00-original",
        "dist": "01-material",
        "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    }
    ```

* `clean` - Removes metadata from the given group(s) of assets.

    Parameters:

    * `src`: the path of the folder that contains the original assets
    * `dist`: the path of the folder in which the script writes the assets without their metadata
    * `groups`: the list of IDs specifying that which groups should be processed

    Example:

    ```json
    {
        "type": "material",
        "src": "01-material",
        "dist": "02-cleaned",
        "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    }
    ```

* `texture` - Removes the textures from the given group(s) of assets.

    Parameters:

    * `src`: the path of the folder that contains the original assets
    * `dist`: the path of the folder in which the script writes the assets without the textures
    * `groups`: the list of IDs specifying that which groups should be processed

    Example:

    ```json
    {
        "type": "material",
        "src": "02-cleaned",
        "dist": "03-non-textured",
        "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    }
    ```

* `encode` - Encodes the given group(s) of assets. Each execution consumes a set of plain assets and executes the sequence of the required invocations of the encoding functions.

    Parameters:

    * `src`: the path of the folder that contains the original assets
    * `dist`: the path of the folder in which the encoded documents should be written
    * `groups`: the list of IDs specifying that which groups should be processed
    * `level`: the level of the encoding (`1`, `2`, `3`, or `4`)

    Example:

    ```json
    {
        "type": "encode",
        "src": "02-cleaned",
        "dist": "911-encoded",
        "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 ,16, 17, 18, 19, 20, 21, 22, 23, 24],
        "level": 1
    }
    ```

* `decode` - Decodes the given group(s) of assets.

    Parameters:

    * `src`: the path of the folder that contains the encoded documents
    * `dist`: the path of the folder in which the decoded assets should be written
    * `groups`: the list of IDs specifying that which groups should be processed
    * `level`: the level of the encoding (`1`, `2`, `3`, or `4`)

   Example:

    ```json
    {
        "type": "decode",
        "src": "911-encoded",
        "dist": "912-decoded",
        "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 ,16, 17, 18, 19, 20, 21, 22, 23, 24],
        "level": 1
    }
    ```

* `validate` - Validates the given group(s) of assets.

    Parameters:

    * `src`: the path of the folder that contains original assets
    * `dist`: the path of the folder that contains the decoded assets
    * `groups`: the list of IDs specifying that which groups should be processed
    * `epsilon`: the threshold to be used in the comparison

   Example:

    ```json
    {
        "type": "validate",
        "src": "02-cleaned",
        "dist": "912-decoded",
        "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 ,16, 17, 18, 19, 20, 21, 22, 23, 24],
        "epsilon": 0.00000005
    }
    ```

### Configuration

#### Structure

The JSON document contains two properties:

* `working-directory`: the path of the working directory
* `goals`: the goals that should be executed in the given order

#### Example

```json
{
    "working-directory": "d:\\tmp\\0-glb",
    "goals": [
        {
            "type": "material",
            "src": "00-original",
            "dist": "01-material",
            "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 ,16, 17, 18, 19, 20, 21, 22, 23, 24]
        },
        {
            "type": "clean",
            "src": "01-material",
            "dist": "02-cleaned",
            "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 ,16, 17, 18, 19, 20, 21, 22, 23, 24]
        },
        {
            "type": "texture",
            "src": "02-cleaned",
            "dist": "03-non-textured",
            "groups": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 ,16, 17, 18, 19, 20, 21, 22, 23, 24]
        }
    ]
}
```