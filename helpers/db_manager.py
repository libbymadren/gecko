import sqlite3

DATABASE_PATH = "./database.db"

def add_mythic_plus_ping(ping):
  db = sqlite3.connect(DATABASE_PATH)
  cursor = db.cursor()
  cursor.execute('INSERT OR REPLACE INTO mythic_plus_pings VALUES(?, ?)', ping)
  db.commit()
  cursor.close()
  db.close()

def get_mythic_plus_ping(guild_id):
  db = sqlite3.connect('database.db')
  cursor = db.cursor()
  cursor.execute('SELECT ping_role FROM mythic_plus_pings WHERE guild_id = ?', guild_id)
  result = cursor.fetchone()
  db.commit()
  cursor.close()
  db.close()
  return result

def remove_mythic_plus_ping(guild_id):
  db = sqlite3.connect('database.db')
  cursor = db.cursor()
  cursor.execute('DELETE FROM mythic_plus_pings WHERE guild_id = ?', guild_id)
  db.commit()
  cursor.close()
  db.close()

