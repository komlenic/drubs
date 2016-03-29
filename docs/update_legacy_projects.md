# Updating legacy (pre-Drubs) projects to use Drubs

This documentation is only for projects that existed prior to the development of
Drubs (using similar, more primitive scripts and tools).  If you don't know why
you would need this information, you probably don't need it.

1.  Create a new branch in your 'config repository' named 'drubs':

    ```bash
    git checkout -b drubs
    ```

2.  Remove all existing files.  (Obviously you'll need to copy some of these
    back in, either with or without modification, but it's easier to remove them
    all and place them back.)

    ```bash
    rm -rf *
    ```

3.  Initialize default Drubs config files for the necessary environments:

    ```bash
    drubs init <node1> <node2> ...
    ```

    For example:

    ```bash
    drubs init localdev dev demo apps
    ```

4.  Edit project.yml file with information obtained from the previously existing
    .yml files per node.  Note that for all nodes specified in the project.yml
    file, all attributes must have values supplied (as of Drubs 0.2.0).  This
    may not be strictly necessary in future versions of Drubs with better error
    checking.

5.  Copy previously existing .make files into the repository, either overwriting
    the default files that 'drubs init' created, or copy/paste the contents of
    the previously existing files into the files that 'drubs init' created.

6.  Copy any other directories that may have previously existed (such as
    'scripts', 'tests', 'import', etc.) back into the repository *into the
    _files_ directory*.  Previously these directories, if present, likely
    existed in the root of the config repository.  Drubs requires any such
    files/directories to be placed in the 'files' directory.

7.  Copy previously existing .py files into the repository, either overwriting
    the default files that 'drubs init' created, or copy/paste the contents of
    the previously existing files into the files that 'drubs init' created.

8.  Convert the .py files for use with Drubs using the provided bash script:

    [convert_py_files.sh](util/convert_py_files.sh)

    For easiest usage, copy this script into your project/config repository and
    execute it:

    ```bash
    # You may need to make the script executable.
    chmod +x convert_py_files.sh
    # Convert the .py files.
    ./convert_py_files.sh
    ```

    Additionally, you may need to correct any pathing issues in your .py files
    to scripts, data import files, etc, as these files and directories now
    reside in the 'files' directory. (See #6 above.)
