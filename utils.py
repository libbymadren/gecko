import logging
import logging.config
import json

def get_logger(name, configFile):
  logConfig = get_config(configFile)
  logConfig['handlers']['file']['filename'] = f"logs/{name}.log"
  logging.config.dictConfig(logConfig)
  logger = logging.getLogger()
  logger.debug(f"Logger Intialized - Config loaded from: {configFile}")
  return logger

def get_config(configPath):
  with open(configPath) as f:
    config = json.load(f)
  return config