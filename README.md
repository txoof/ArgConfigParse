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


## ConfigFile()
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

## CmdArg()
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

## merge_dict()
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


## Limitations
Configuration file section names cannot contain the following characters:
* `'__'` -- two or more underscores consecutively
    - OK: `main_section`
    - OK: `waiter_configuration_settings`
    - Not OK: `main__section` -- this will result in an unintended nested section in the options dictionary
* `' '` -- one or more literal space