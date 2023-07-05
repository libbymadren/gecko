import sqlite3

DATABASE_PATH = "./database.db"

def initialize_server(data):
  db = sqlite3.connect(DATABASE_PATH)
  cursor = db.cursor()
  cursor.execute('INSERT INTO keys_data VALUES(?, ?)', data)
  db.commit()
  cursor.close()
  db.close()

def get_guild_id(guild_id):
  db = sqlite3.connect(DATABASE_PATH)
  cursor = db.cursor()
  try:
    cursor.execute('SELECT guild_id FROM keys_data WHERE guild_id = ?', guild_id)
    result = cursor.fetchone()
    db.commit()
    cursor.close()
    db.close()
    return result
  except sqlite3.Error as er:
    print(er)
    return None

def add_keys_channel(data):
  db = sqlite3.connect(DATABASE_PATH)
  cursor = db.cursor()
  cursor.execute('INSERT INTO keys_channels VALUES(?, ?)', data)
  db.commit()
  cursor.close()
  db.close()

def get_keys_channels(guild_id):
  db = sqlite3.connect(DATABASE_PATH)
  cursor = db.cursor()
  try:
    cursor.execute('SELECT channel_id FROM keys_channels WHERE guild_id = ?', guild_id)
    result = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return result
  except sqlite3.Error as er:
    print(er)
    return None 

def add_mythic_plus_ping(data):
  db = sqlite3.connect(DATABASE_PATH)
  cursor = db.cursor()
  cursor.execute('INSERT OR REPLACE INTO keys_data VALUES(?, ?)', data)
  db.commit()
  cursor.close()
  db.close()

def get_mythic_plus_ping(guild_id):
  db = sqlite3.connect(DATABASE_PATH)
  cursor = db.cursor()
  try:
    cursor.execute('SELECT ping_role FROM keys_data WHERE guild_id = ?', guild_id)
    result = cursor.fetchone()
    db.commit()
    cursor.close()
    db.close()
    return result
  except sqlite3.Error as er:
    return None 

def remove_mythic_plus_ping(guild_id):
  db = sqlite3.connect(DATABASE_PATH)
  cursor = db.cursor()
  cursor.execute('DELETE FROM mythic_plus_pings WHERE guild_id = ?', guild_id)
  db.commit()
  cursor.close()
  db.close()



