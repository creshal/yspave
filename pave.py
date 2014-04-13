import os.path,xdg.BaseDirectory

appname = "yspave"
appvers = "0.0.1"
default_dir = xdg.BaseDirectory.save_config_path(appname)
default_db_filename = os.path.join (default_dir, "default.db")
default_config_filename = os.path.join (default_dir, "config.json")

database_version = 1
database_encoding = 'utf8'
database_key_fields = [
	'Title',
	'Password',
	'Details'
]

# scrypt maxtime for db files
database_complexity = 1.0

# scrypt maxtime for title/details
metadate_complexity = 0.01

#scrypt maxtime for passwords
password_complexity = 2.0

