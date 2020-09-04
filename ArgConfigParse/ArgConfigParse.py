#!/usr/bin/env python
# coding: utf-8


# In[3]:


#get_ipython().run_line_magic('alias', 'nbconvert nbconvert ArgConfigParse.ipynb ./ArgConfigParse/')
#get_ipython().run_line_magic('nbconvert', '')




# In[4]:


import configparser
import argparse
import logging
from pathlib import Path
import sys
import re




# In[5]:


# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)




# In[6]:


def write(dictionary, file, create=False):
    '''write a configuration dictionary to a file; skip over sections that begin with `__`
    
    Args: 
        dictionary(`dict`): nested dictionary
        file(`string` or `Path`): path to config file
        create(`bool`): create the file and path if it does not exist
        
    Returns:
        file(`Path`): path to config file
    '''
    file = Path(file)
    
    if create:
        file.parent.mkdir(parents=True, exist_ok=True)
    
    config = configparser.ConfigParser()
    for each in dictionary:
        if each.startswith('__', 0, 2):
            logger.debug(f'skipping: {each}')
            continue
        logger.debug(f'adding {each} to config')
        config[each] = dictionary[each]
        
    logger.debug(f'writing configuration to {file}')
    with open (file, 'w') as configfile:
        config.write(configfile)
    return(file)




# In[7]:


def merge_dict(a, b):
    '''recursivley merge two dictionarys overwriting values
        known issue: if `a` contains a different data type than `b`, 
        `b` will completely overwrite the data in `a`
        
    Args:
        a(`dict`): nested dictionary
        b(`dict`): nested dictionary 
        
    Returns:
        `dict`
    '''
    c = dict(a) # make a copy of dict `a`
    for key in b:
        if key in a:
            if isinstance(b[key], dict) and isinstance(a[key], dict):
                c[key] = merge_dict(a[key], b[key])
            else:
                c[key] = b[key]
        else:
            c[key] = b[key]
    return c




# In[8]:


def fullPath(path):
    '''expand user paths and resolve string into a path
    
    Args:
        path(`str`): string representation of a path 
            `~`, `.` and `..` notation will be expanded
            and resolved
    Returns:
        `path.Path()`'''
    if path is None:
        path = None
    else:
        path = Path(path).expanduser().resolve()
    return path




# In[28]:


class ConfigFile():
    '''Read and parse one or more INI style configuration files
    
        Creates a configparser.ConfigParser() object and reads multiple
        configuration files. Settings in each file supersedes pervious files
        `config_files`=[default, system, user] 
        * default - read first
        * system - read second and overwrites default
        * user - read last and overwrites system
        
    Args:
        config_files(`list`): list of configuration files to read
    Properties:
        config_files(`list` of `str` or `pathlib.PosixPath`): str or Path() objects to read
        parser(`configparser.ConfigParser obj`): config parser object
        config_dict(`dict` of `dict`): nested configuration dict following INI file format:
        ignore_missing(`bool`): True: ignore missing configuration files; default: False
        
            Sample config.ini:
            
                [Section]
                option = value
                option2 = True

                [Main]
                log_level = DEBUG
            
            Yeilds -> config_dict:
            
                {'Section': {'option': 'value', 'option2': True}
                 'Main': {'log_level': 'DEBUG'}}
        '''
    def __init__(self, config_files=None, ignore_missing=False):
        self.config_dict = {}
        self.ignore_missing = ignore_missing
        self.parser = configparser.ConfigParser()
        self.config_files = config_files
        
    @property
    def ignore_missing(self):
        '''ignore missing configuration files (boolean)'''
        return self._ignore_missing
    
    @ignore_missing.setter
    def ignore_missing(self, val):
        if not isinstance(val, bool):
            raise TypeError(f'ignore_missing must be a boolean')
        else:
            self._ignore_missing = val
    
    @property
    def config_files(self):
        '''list of configuration files
        
        Args:
            config_files(`list` of `str` or `pathlib.PosixPath`): list of INI files to read
            ignore_missing(`bool`): True: ignore any missing config files; default: False
        Sets:
            config_files(`list`)
            '''
        return self._config_files
    
    @config_files.setter
    def config_files(self, config_files):
        self._config_files = []
        logger.debug(f'received config_file list: {config_files}')
        if not config_files:
            return
            
        if config_files and not isinstance(config_files, (list, tuple)):
            raise TypeError(f'Type mismatch: expected list like object, but received {type(config_files)}: {config_files}')
        
#         self._config_files = []
        bad_files = []
        
        for i in config_files:
            f = fullPath(i)
            if f.exists():
                logger.debug(f'{f} exists')
                self._config_files.append(f)
            else:
                logger.debug(f'{f} does not exist')
                bad_files.append(f)

            
        logger.debug(f'processing existing config files: {self._config_files}')
        logger.debug(f'bad files: {bad_files}')
        if (len(bad_files) > 0) and not self.ignore_missing:
            raise(FileNotFoundError(f'config files not found: {bad_files}'))
        else:
            logger.debug(FileNotFoundError(f'config files not found: {bad_files}'))
            
    def parse_config(self):
        '''reads and stores configuration values from `config_files` in left-to-right order
            right-most section/option/values overwrite left-most section/option/values
        
        Returns:
            config_dict(`dict` of `dict`)
        Sets: config_dict
        Raises: FileNotFoundError if config file cannot be found'''
        
        for file in self.config_files:
            if file.exists():
                self.parser.read(file)
            else:
                raise FileNotFoundError(f'config file not found: {file}')
        
        if self.parser.sections():
            self.config_dict = self._config_to_dict(self.parser)
        
        return self.config_dict
        
    
    def _config_to_dict(self, configuration):
        '''convert an argeparse object into a nested dictionary
        
        Args: 
            configuration(`configparser.ConfigParser`)
            
        Returns:
            `dict`'''
        
        d = {}
        
        for section in configuration.sections():
            d[section] = {}
            for opt in configuration.options(section):
                d[section][opt] = configuration.get(section, opt)
                
        return d
    
    




# In[19]:


class CmdArgs():
    '''command line argument parser object 
    
    
    
    
    Args:
        args(`list`): sys.argv is typically passed here
        
    Properties:
        parser(`argparse.ArgumentParser`): argument parser object
        args(`list`): list of arguments
        unknown(`list`): list of unknown arguments that are ignored
        options(NameSpace): argument parser generated namespace of arguments
        opts_dict(`dict`): namespace -> dictionary'''

    def __init__(self, args=None):
        self.parser = argparse.ArgumentParser()
        self.ignore_none = []
        self.ignore_false = []
        self.args = args
        self.unknwon = None
        self.options = None
        self.opts_dict = None
        self.nested_opts_dict = None
    
    @property
    def options(self):
        '''argparser Namespace of the parsed arguments'''
        return self._options
    
    @options.setter
    def options(self, options):
        if options:
            self._options = options
        else:
            self._options = None
    
    def parse_args(self): #, discard_false=[], discard_none=[]):
        '''parse arguments and set dictionaries
            
        Sets:
            args(`list`): list of arguments
            unknown_args: args that have been passed, but are not known
            options(Nampespace): namespace of parsed known arguments
            opts_dict(`dict`): flat dictionary containing arguments
            nested_opts_dict(`dict` of `dict` of `str`): parsed arguments
                nested to match ConfigFile.opts_dict:
                {'section_name': {'option1': 'valueY'
                                  'option2': 'valueZ'}
                                  
                 'section_two':  {'optionX': 'setting1'
                                  'optionY': 'other_setting'}}
                                  
            see add_argument() for more information'''
            
        unknown = False
        
#         if args:
#             my_args = args
#         else:
#             my_args = self.args
        
#         if my_args:
        options, unknown = self.parser.parse_known_args()
        logger.debug(f'options: {options}')
        self.options = options
        self.opts_dict = options            
        self.nested_opts_dict = self.opts_dict
            
        if unknown:
            logger.info(f'ignoring unknown options: {unknown}')
            self.unknown = unknown
 
    
    @property
    def opts_dict(self):
        '''dictionary of namespace of parsed options
        
        Args:
            options(namespace): configparser.ConfigParser.parser.parse_known_args() options
        
        Returns:
            `dict` of `namespace` of parsed options
            '''
        return self._opts_dict
    
    @opts_dict.setter
    def opts_dict(self, options):
        if options:
            self._opts_dict = vars(self.options)
        else:
            self._opts_dict = None

    @property
    def nested_opts_dict(self):
        '''nested dictionary of configuration options
            `nested_opts_dict` format follows the same format as ConfigFile.config_dict
            see add_argument for more information 
            
        Args:
            opts_dict(`dict`): flat dictionary representation of parser arguments'''
        return self._nested_opts_dict
    
    @nested_opts_dict.setter
    def nested_opts_dict(self, opts_dict):
        if not opts_dict:
            # skip processing
            self._nested_opts_dict = None
        else:
            # nest everything that comes from the commandline under this key
            cmd_line = '__cmd_line'
            d = {}
            # create the key for command line options
            d[cmd_line] = {}
            
            # process all the keys in opts_dict
            for key in opts_dict:
                # ignore keys if they in the ignore lists AND are False/None 
                if (key in self.ignore_none or key in self.ignore_false) and not opts_dict[key]:
                    logger.debug(f'ignoring key: {key}')
                    # do not include these keys in the nested dictionary
                    continue
                # match those that are in the format [[SectionName]]__[[OptionName]]
                match = re.match('^(\w+)__(\w+)$', key)
                if match:
                    # unpack into {sectionName: {OptionName: Value}}
                    section = match.group(1)
                    option = match.group(2)
                    if not section in d:
                        # add the section if needed
                        d[section] = {}
                    d[section][option] = opts_dict[key]
                else:
                    # if not in `section__option format`, do not unpack add to dictionary
                    # under `cmd_line` key
                    d[cmd_line][key] = opts_dict[key]
            
            self._nested_opts_dict = d
            

    
    def add_argument(self, *args, **kwargs):
        '''add arguments to the parser.argparse.ArgumentParser object 
        
            use the standard *args and **kwargs for argparse
            
            arguments added using the kwarg `dest=section__option_name`
             --note the format: [[section_name]]__[[option_name]]
            will be nested in the `opts_dict` property in the format:
            {'section': 
                        {'option_name': 'value'
                         'option_two': 'value'}}
                         
            the `nested_opts_dict` property can then be merged with a ConfigFile 
            `config_dict` property using the merge_dicts() function:
            merge_dicts(obj:`ConfigFile.config_dict`, obj:`Options.nested_opts_dict`) 
            to override the options set in the configuration file(s) with
            commandline arguments
            
            Example:
                CmdArgs.add_argument('-m', '--menu', ignore_none=True, 
                          metavar='["item one", "item two", "item three"]', 
                          type=list,
                          dest='main__menu', 
                          help='list of menu items')
        
        Args:
            ignore_none(`bool`): ignore this option if set to `None` when building configuration dictionary
            ignore_false(`bool`): ignore this option if set to `False` when building configuation dictionary
            *args, **kwargs'''
        # pop out these keys from the dictionary  to avoid sending to the dictionary; if not found
        # set to `False`

        # this can probably be fixed by using the following:
        # parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
        
        ignore_none = kwargs.pop('ignore_none', False)
        ignore_false = kwargs.pop('ignore_false', False)

        if 'dest' in kwargs:
            dest = kwargs['dest']
        elif len(args) == 2:
            dest = args[1]
        else:
            #FIXME need to strip out `--` and turn `-` to `_`
            dest = args[0]
        
        dest = dest.strip('-').replace('-', '_')
        
        if ignore_none:
            self.ignore_none.append(dest)
        if ignore_false:
            self.ignore_none.append(dest)
        
        try:
            self.parser.add_argument(*args, **kwargs)
        except argparse.ArgumentError as e:
            logger.warning(f'failed adding conflicting option: {e}')


