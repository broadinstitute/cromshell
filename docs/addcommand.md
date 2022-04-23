# Adding a Command

This document describes the process of adding a command to Cromshell. Before following
the process below be sure to have properly set up your dev environment, which is 
described in [./development.md](../docs/README.md).

### Create A Command Directory 
Create a directory that will hold your command scripts. The name of the directory 
should match the name of your command and should be created under the `/src/cromshell` 
directory. For example:

    > src
       > cromshell
          > my_new_command
          > commanda
          > commandb
          > commandc
          __init__.py
          __main__.py

Within the newly created directory add two files `__init__.py` and `command.py`. 
The `__init__.py` will stay empty but the `command.py` will house the script for your command. 


    > src
        > cromshell
            > my_new_command
                __init__.py
                command.py


Here is an example of the contents of a command.py which can be used as a template.

    import logging
    
    import click
    
    LOGGER = logging.getLogger(__name__)
    
    @click.command(name="my-new-command")
    @click.pass_obj
    def main(config):
        """My-new-command does things."""
    
        LOGGER.info("my-new-command")
        print("hello world")


### Expose your command to Cromshell
In order to have your command be executable by Cromshell, your command will 
need to be imported to the `__main__.py` file. 

    > src
       > cromshell
          > my_new_command
          > commanda
          > commandb
          > commandc
          __init__.py
          __main__.py  # <-Edit

You need to make 2 changes to the `__main__.py` file
- Add an import statement near the top of the file, following this format
  - `from .<command directory name> import command as <command name>`
  - E.g. `from .my_new_command import command as my_new_command`
- Use the Clicks add_command function near the bottom with the following format
  - `main_entry.add_command(<command name>.main)`
  - E.g. `main_entry.add_command(my_new_command.main)`

You should now be able to call on your command through the command line. 
    
    cromshell-alpha --help
    Usage: cromshell-alpha [OPTIONS] COMMAND [ARGS]...
    
      Cromshell is a script for submitting workflows to a cromwell server and
      monitoring / querying their results.
    
      Notes:
    
          - A hidden folder will be created on initial run. The hidden folder
          (.../.cromshell) will be placed in users home directory but can be
          overridden by setting environment variable 'CROMSHELL_CONFIG'.
    
    Options:
      --help                          Show this message and exit.
    
    Commands:
      abort          Abort a running workflow.
      **my-new-command My-new-command does things.**
      alias          Label the given workflow ID or relative id with the...
      version        Print the version of cromshell



### Command Arguments

Cromshell uses Click decorators to add [arguments](https://click.palletsprojects.com/en/8.1.x/arguments/) 
and [options](https://click.palletsprojects.com/en/8.1.x/options/) for commands. 
These are placed in the command.py file, under the click name decorator. Also, the 
arguments and options will need to be passed to the main command function 
to make them available for your command. 

    import logging
    
    import click
    
    LOGGER = logging.getLogger(__name__)
    
    @click.command(name="my-new-command")
    @click.argument("workflow_id")
    @click.option(
        "-p",  # <- short option name
        "--print_workflow",  # <- long option name
        is_flag=True,
        default=False,
        help="Print workflow id",
    )
    
    @click.pass_obj
    def main(config, workflow_id, print_workflow):
        """My-new-command does things."""
    
        LOGGER.info("my-new-command")
        print("hello world")

        if print_workflow:
            print("workflow_id")




### Using existing functions

Cromshell already has several generic functions that can be reused for you command, 
they are located under the utility directory separated into different files 
based on function. You are encouraged to use the functions when possible or 
add to the list of functions. 

    > src
       > cromshell
          > commanda
          > commandb
          > commandc
          > utility
             __init__.py
             cromshellconfig.py
             http_utils.py
             io_utils.py
             submissions_file_utils.py
             workflow_id_utils.py 
          __init__.py
          __main__.py


- cromshellconfig.py : Holds function associated with Cromshells configurations, such as getting the Cromwell server api, getting Cromshells hidden directory, etc
- http_utils.py : Common functions that relate to running HTTP calls, e.g. checking whether its possible to connect with the provided Cromwell server
- io_utils.py : Functions used to write to the terminal 
- submissions_file_utils.py : Functions related to the file holding all the workflows lunched by user
- workflow_id_utils.py : Functions that check, resolve, get workflow IDs

Here is an example of importing the modules to your command.py

`from cromshell.utilities import http_utils, io_utils, workflow_id_utils`