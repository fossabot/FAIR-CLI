# FAIR Data Pipeline Command Line Interface

| **DISCLAIMER:**                                                                                                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The following document is largely conceptual and therefore does *not* represent a manual for the final interface. Statements within the following are likely to change, further details of possible changes are given throughout. |

**Table of Contents**
   * [Installation](#installation)
   * [Structure](#structure)
      * [Global and Local Directories](#global-and-local-directories)
      * [Data Directory](#data-directory)
      * [Sessions Directory](#sessions-directory)
      * [Logs Directory](#logs-directory)
      * [Staging File](#staging-file)
   * [Command Line Usage](#command-line-usage)
      * [init](#init)
      * [run](#run)
      * [log](#log)
      * [view](#view)
   * [Template Variables](#template-variables)

FAIR-CLI forms the main interface for synchronising changes between your local and shared remote FAIR Data Pipeline registries, it is also used to instantiate model runs/data submissions to the pipeline.

The project is still under development with many features still pending review. Available commands are summarised below along with their usage.

## Installation

The project makes use of [Poetry](https://python-poetry.org/) for development which allows quick and easy mangement of dependencies, and provides a virtual environment exclusive to the project. Ultimately the project will be built into a pip installable module (using `poetry build`) meaning users will not need Poetry. You can access this environment by installing poetry:
```bash
$ pip install poetry
```
and, ensuring you are in the project repository, running:
```
$ poetry install
```
which will setup the virtual environment and install requirements. You can then either launch the environment as a shell using:
```bash
$ poetry shell
```
or run commands within it externally using:
```bash
$ poetry run <command>
```

## Structure

The layout of FAIR-CLI on a simplified system looks like this:
```bash
$HOME
├── .fair
│   ├── cli
│   │   ├── cli-config.yaml
│   │   └── sessions
│   ├── data
│   │   └── coderun
│   └── $REGISTRY_HOME
│
└─ Documents
   └─ my_project
      └─ .fair
         ├── cli-config.yaml
         ├── logs
         └── staging
```
### Global and Local Directories
FAIR-CLI stores information for projects in two locations. The first is a *global* directory stored in the user's home folder in the same location as the registry itself `$HOME/.fair/cli`, and the second is a *local* directory which exists within the model project itself `$PROJECT_HOME/.fair`.

The CLI holds metadata for the user in it's own configuration file (not to be confused with the user modifiable `config.yaml`), `cli-config.yaml`, the *global* version of which is initialised during first use. In a manner similar to `git`, FAIR-CLI has repositories which allow the user to override these *global* configurations, this then forming a *local* variant.

### Data Directory
The directory `$HOME/.fair/data` is the default data store initialised by FAIR-CLI, this can be later changed on a per-run basis if the user so desires. The subdirectory `coderun` contains timestamped directories of submission script/model runs.

### Sessions Directory
The directory `$HOME/.fair/sessions` is used to keep track of ongoing queries to the registry as a safety mechanism to ensure the registry is not shutdown whilst processes are still occuring.

### Logs Directory
The directory `$PROJECT/.fair/logs` stores `stdout` logs for runs also giving information on who launched the run and how long it lasted.

### Staging File
Not yet fully implemented, the file `$PROJECT/.fair/staging` keeps track of which runs/files the user wishes to "commit" for synchronisation between local and remote registries.
Simply contains a dictionary of booleans where items for sync (staged) are marked true `True` and those to be held only locally `False`.
The file uses paths relative to the *local* `.fair` folder as keys, to behave in a manner identical to `git` staging.

### 

| **NOTE**                                                                                                                                                                                                                                            |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| This layout is subject to possible change depending on whether or not multiple aliases for the same user will be allowed in the registry itself. The main reason for having a *local* version is to support separate handling of multiple projects. |

## Command Line Usage
As mentioned, all of the subcommands within FAIR-CLI are still under review with many still serving as placeholders for future features. Running `fair` without arguments or `fair --help` will show all of these.

### `init`
Initialises a new FAIR repository within the given directory. This should ideally be the same location as the `.git` folder for the current project. The command will ask the user a series of questions which will provide metadata for tracking run authors, and also allow for the creation of a starter `config.yaml`.

The first time this command is launched the *global* CLI configuration will be populated. In subsequent calls the *global* will provide default suggestions towards creating the CLI configuration for the repository (*local*).

A repository directory matching the structure above will be placed in the current location and a starter `config.yaml` file will be generated (see below).

**Example: First call to `fair init`**

This example shows the process of setting up for the first time. Note the default suggestions for each prompt, in the case of `Full name` and `Default output namespace` this is the hostname of the system and an abbreviated version of this name.
```
$ fair init
Initialising FAIR repository, setup will now ask for basic info:

Remote API URL: https://data.scrc.uk/api/
Local API URL [http://localhost:8000/api/]: 
Full name [jbloggs-pc]: Joe Bloggs
Email: jbloggs@noreply.uk
ORCID [None]: 
Default input namespace [None]: SCRC
Default output namespace [jbloggs]: 
Project description: A test project
Initialised empty fair repository in /home/kristian/Documents/UKAEA/SCRC/fair/.fair
```
**Example: Subsequent runs**

In subsequent runs the first time setup will provide further defaults.
```
$ fair init
Initialising FAIR repository, setup will now ask for basic info:

Project description: A new project
Remote API URL [https://data.scrc.uk/api/]: 
Local API URL [http://localhost:8000/api/]: 
Default output namespace [jbloggs]: 
Default input namespace [SCRC]: 
Initialised empty fair repository in /home/kristian/Documents/UKAEA/SCRC/fair/temp/.fair
```

**Generated `config.yaml`**

```yaml
fail_on_hash_mismatch: true
run_metadata:
  data_store: /home/kristian/.fair/data
  default_input_namespace: SCRC
  default_output_namespace: jbloggs
  description: A new project
  local_data_registry: http://localhost:8000/api/
  local_repo: /home/jbloggs/Documents/my_project
  script: null
```

the user then only needs to update `script` for this to be a valid `config.yaml`.


### `run`

The purpose of `run` is to execute a model/submission run to the local registry. The command fills any specified template variables of the form `${{ fair.VAR }}` to match those outlined [below](#template-variables). Outputs of a run will be stored within the `coderun` folder in the directory specified under the `data_store` tag in the `config.yaml`, by default this is `$HOME/.fair/data/coderun`.

### `log`

Runs are logged locally within the local FAIR repository. A full list of runs is shown by running:
```
$ fair log
```
This will present a list of runs in a summary analogous to a `git log` call:
```
run 0db35c20946a1ebeaafdc3b30103cd74a57eb6b6
Author: Joe Bloggs <jbloggs@noreply.uk>
Date:   Wed Jun 30 09:09:30 2021
```

| **NOTE**                                                                                                                            |
| ----------------------------------------------------------------------------------------------------------------------------------- |
| The SHA for a run is *not* yet related to a registry run ID. This value is calculated from the contents of the `stdout` of the run. |

### `view`
To view the `stdout` of a run given its SHA as shown by running `fair log` use the command:
```
$ fair view <sha>
```
you do not need to specify the full SHA but rather the first few characters:
```
--------------------------------
 Commenced = Wed Jun 30 09:09:30 2021 
 Author    = Joe Bloggs <jbloggs@noreply.uk>
 Namespace = jbloggs
 Command   = bash -eo pipefail /home/jbloggs/.fair/data/coderun/2021-06-30_09_09_30_721358/run_script
--------------------------------
0
1
2
3
4
5
6
7
8
9
10
------- time taken 0:00:00.011910 -------
```

## Template Variables
Within the `config.yaml` file, template variables can be specified by using the notation `${{ fair.VAR }}`, the following variables are currently recognised:

| **Variable**        | **Description**                                                                  |
| ------------------- | -------------------------------------------------------------------------------- |
| `DATE`              | Date in the form `%Y%m%d` if the key contains the word `version` else `%Y-%m-%d` |
| `DATETIME`          | Date and time in the form `%Y-%m-%s %H:%M:S`                                     |
| `USER`              | The current user as defined in the CLI                                           |
| `REPO_DIR`          | The FAIR repository root directory                                               |
| `CONFIG_DIR`        | The directory containing the `config.yaml` after template substitution           |
| `SOURCE_CONFIG`     | Path of the user defined `config.yaml`                                           |
| `GIT_BRANCH`        | Current branch of the `git` repository                                           |
| `GIT_REMOTE_ORIGIN` | The URI of the git repository under the tag `origin`                             |
| `GIT_TAG`           | The latest tag on `git`                                                          |
