DATABASE_CONFIG = {
    "host": "your_host",  # insert your localhost to your_host
    "user": "your_user",  # inser your user to your_user
    "password": "your_password",  # insert your password to your_password
    # (change @ to %40 if the last character of your password is @)
    "database": "your_database",  # insert your database to your_database
}

DATABASE_URI = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
