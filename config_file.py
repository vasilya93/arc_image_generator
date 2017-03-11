#!/usr/bin/python
import ConfigParser
import io

def writeConfigFile(fileName, dictionary):
    configFile = open(fileName, 'w')
    config = ConfigParser.ConfigParser()
    for key in dictionary:
        config.add_section(key)
        for subKey in dictionary[key]:
            config.set(key, subKey, dictionary[key][subKey])
    config.write(configFile)
    configFile.close()

def readConfigFile(fileName):
    with open(fileName) as f:
        configContent = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(configContent))

    dictionary = {}
    for section in config.sections():
        print section
        options = {}
        for option in config.options(section):
            option_value = config.get(section, option)
            options[option] = option_value
        dictionary[section] = options
    return dictionary
