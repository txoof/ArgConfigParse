# ArgConfigParse
Merge command line arguments and config file(s) into a single dictionary using python standard argparse and configparser modules.

ArgConfigParse provides the following Classes and functions:

**Classes** 
* `ConfigFile()`
* `CmdArg()`

**Functions**
* `merge_dict()`
* `fullPath()`

ConfigFile reads one or more config files and destructively merges each configuration file with the following file. Any keys/value pairs that are repeated in each subsequent config file will effectively over write the previous values for the same key. This is useful for handling system-wide configuration files that can be over-ridden with individual user configuration files.

CmdArg parses sys.argv command line arguments and creates nested dictionaries that can be easily merged with the values from the ConfigFiles.

Command line arguments that do not appear in the configuration file are stored in `__cmd_line` 

## Examples
### ConfigFile() Examples
Class for handling multiple similar configuration files and merging the contents sequentially.

**system wide configuration file**
```
    #/etc/spam_sketch
    [Main]
    menu = ["spam", "eggs and spam"]
    debug = INFO
    output_device = dead_parrot


    [waiter]
    name = Terry
    tone = shrill
    attempts = 10
    pause = False
```
**user configuration file**
```
    #/home/monty/.config/spam_sketch
    [Main]
    menu = ["spam", "eggs and spam", "spam; spam; spam and eggs", "eggs; spam spam and toast"]
    debug = DEBUG

    [waiter]
    name = John
    tone = shrill
    attempts = 10
    pause = False

    [customer1]
    name = Eric
    patience = .8
    order = "anything but spam"

    [customer2]
    name = Graham
    patience = .2
    order = "toast"
```

**Read Configuration Files**
```
    import ArgConfigParse
    # read /etc/spam_sketch followed by ~/.config/spam_sketch 
    # values in ~/.config/spam_sketch override /etc/spam_sketch
    config = ConfigFile(['/etc/spam_sketch', '~/.config/spam_sketch'])
    
    config.parse_config()
    print(config.config_dict)
    >>> {'Main': {'menu': '["spam", "eggs and spam", "spam; spam; spam and eggs", "eggs; spam spam and toast"]', 'debug': 'DEBUG', 'output_device': 'dead_parrot'}, 'waiter': {'name': 'John', 'tone': 'shrill', 'attempts': '10', 'pause': 'False'}, 'customer1': {'name': 'Eric', 'patience': '.8', 'order': '"anything but spam"'}, 'customer2': {'name': 'Graham', 'patience': '.2', 'order': '"toast"'}}

```

### CmdArg() Examples
**Parse Command Line Arguments**
```
    import ArgConfigParse
    # create the argument parser object
    cmd_args = CmdArgs()
    # set some toy sys.arv values
    sys.argv = ['-V', '-m', ['spam', 'toast and spam', 'one dead parrot']]
    
    # add arguments to be accepted from the command line
    
    # this option will be stored in {'main': {'menu': <list>'}}
    cmd_args.add_argument('-m', '--menu', ignore_none=True, 
                          metavar='["item one", "item two", "item three"]', 
                          type=list,
                          dest='main__menu', 
                          help='list of menu items')
                          

    # this option will be stored in {'waiter':{'tone': <value>'}}
    cmd_args.add_argument('-t', '--tone', ignore_none=True, metavar='TONE', type=str,
                           choices=['kind', 'shrill', 'annoying', 'loud'], dest='waiter__tone', 
                           help='tone of waiter')
                           
    # this option will be stored in __cmd_line 
    cmd_args.add_argument('-V', '--version', action='store_true', dest='version', 
                          default=False, help='display version nubmer and exit')
    
    
    # parse sys.argv values
    cmd_args.parse_args()
    
    # show parsed values
    print(cmd_args.options)
    >>> Namespace(main__menu=['spam', 'toast and spam', 'one dead parrot'], main__output_device=None, version=True, waiter__tone=None)
    
    # show nested dictionary
    print(cmd_args.nested_opts_dict)
    >>> {'__cmd_line': {'version': True}, 'main': {'menu': ['spam', 'toast and spam', 'one dead parrot']}}
```

### merge_dict() Examples
**Merge command line arguments and config files**
```
    # command line options override config files
    options = merge_dict(config.config_dict, cmd_args.nested_opts_dict)
    print(options)
    >>> {'__cmd_line': {'version': True}, 'main': {'menu': ['spam', 'toast and spam', 'one dead parrot']}, 'Main': {'menu': '["spam", "eggs and spam", "spam; spam; spam and eggs", "eggs; spam spam and toast"]', 'debug': 'DEBUG', 'output_device': 'dead_parrot'}, 'waiter': {'name': 'John', 'tone': 'shrill', 'attempts': '10', 'pause': 'False'}, 'customer1': {'name': 'Eric', 'patience': '.8', 'order': '"anything but spam"'}, 'customer2': {'name': 'Graham', 'patience': '.2', 'order': '"toast"'}}
    


    # config files override command line options
    options merge_dict(cmd_args.nested_opts_dict, config.config_dict,)
    print(options)
    >>> {'Main': {'menu': '["spam", "eggs and spam", "spam; spam; spam and eggs", "eggs; spam spam and toast"]', 'debug': 'DEBUG', 'output_device': 'dead_parrot'}, 'waiter': {'name': 'John', 'tone': 'shrill', 'attempts': '10', 'pause': 'False'}, 'customer1': {'name': 'Eric', 'patience': '.8', 'order': '"anything but spam"'}, 'customer2': {'name': 'Graham', 'patience': '.2', 'order': '"toast"'}, '__cmd_line': {'version': True}, 'main': {'menu': ['spam', 'toast and spam', 'one dead parrot']}}    
```

## Documentation

### class CmdArgs(builtins.object)
     |  CmdArgs(args=None)
     |  
     |  command line argument parser object 
     |  
     |  
     |  
     |  
     |  Args:
     |      args(`list`): sys.argv is typically passed here
     |      
     |  Properties:
     |      parser(`argparse.ArgumentParser`): argument parser object
     |      args(`list`): list of arguments
     |      unknown(`list`): list of unknown arguments that are ignored
     |      options(NameSpace): argument parser generated namespace of arguments
     |      opts_dict(`dict`): namespace -> dictionary
     |  
     |  Methods defined here:
     |  
     |  __init__(self, args=None)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  add_argument(self, *args, **kwargs)
     |      add arguments to the parser.argparse.ArgumentParser object 
     |          use the standard *args and **kwargs for argparse
     |          
     |          arguments added using the kwarg `dest=section__option_name`
     |          note the format [[section_name]]__[[option_name]]
     |          will be nested in the `opts_dict` property in the format:
     |          {'section': 
     |                      {'option_name': 'value'
     |                       'option_two': 'value'}}
     |                       
     |          the `nested_opts_dict` property can then be merged with a ConfigFile 
     |          `config_dict` property using the merge_dicts() function:
     |          merge_dicts(obj:`ConfigFile.config_dict`, obj:`Options.nested_opts_dict`) 
     |          to override the options set in the configuration file(s) with
     |          commandline arguments
     |      
     |      Args:
     |          ignore_none(`bool`): ignore this option if set to `None` when building configuration dictionary
     |          ignore_false(`bool`): ignore this option if set to `False` when building configuation dictionary
     |          *args, **kwargs
     |  
     |  parse_args(self)
     |      parse arguments and set dictionaries
     |          
     |      Sets:
     |          args(`list`): list of arguments
     |          unknown_args: args that have been passed, but are not known
     |          options(Nampespace): namespace of parsed known arguments
     |          opts_dict(`dict`): flat dictionary containing arguments
     |          nested_opts_dict(`dict` of `dict` of `str`): parsed arguments
     |              nested to match ConfigFile.opts_dict:
     |              {'section_name': {'option1': 'valueY'
     |                                'option2': 'valueZ'}
     |                                
     |               'section_two':  {'optionX': 'setting1'
     |                                'optionY': 'other_setting'}}
     |                                
     |          see add_argument() for more information
     

### class ConfigFile(builtins.object)
     |  ConfigFile(config_files=None)
     |  
     |  Read and parse one or more INI style configuration files
     |  
     |      Creates a configparser.ConfigParser() object and reads multiple
     |      configuration files. Settings in each file supersedes pervious files
     |      `config_files`=[default, system, user] 
     |      * default - read first
     |      * system - read second and overwrites default
     |      * user - read last and overwrites system
     |      
     |  Args:
     |      config_files(`list`): list of configuration files to read
     |  Properties:
     |      config_files(`list` of `str` or `pathlib.PosixPath`): str or Path() objects to read
     |      parser(`configparser.ConfigParser obj`): config parser object
     |      config_dict(`dict` of `dict`): nested configuration dict following INI file format:
     |          Sample config.ini:
     |          
     |              [Section]
     |              option = value
     |              option2 = True
     |  
     |              [Main]
     |              log_level = DEBUG
     |          
     |          Yeilds -> config_dict:
     |          
     |              {'Section': {'option': 'value', 'option2': True}
     |               'Main': {'log_level': 'DEBUG'}}
     |  
     |  Methods defined here:
     |  
     |  __init__(self, config_files=None)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  parse_config(self)
     |      reads and stores configuration values from `config_files` in left-to-right order
     |          right-most section/option/values overwrite left-most section/option/values
     |      
     |      Returns:
     |          config_dict(`dict` of `dict`)
     |      Sets: config_dict
     
### merge_dict(a, b)
    recursivley merge two dictionarys overwriting values
        known issue: if `a` contains a different data type than `b`, 
        `b` will completely overwrite the data in `a`

    Args:
        a(`dict`): nested dictionary
        b(`dict`): nested dictionary 

    Returns:
        `dict`


## Limitations
Configuration file section names cannot contain the following characters:
* `'__'` -- two or more underscores consecutively
    - OK: `main_section`
    - OK: `waiter_configuration_settings`
    - Not OK: `main__section` -- this will result in an unintended nested section in the options dictionary
* `' '` -- one or more literal space


```python

```
