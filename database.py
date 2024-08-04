import sqlite3
import pandas as pd
import csv

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

conn.execute('''CREATE TABLE IF NOT EXISTS text(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    before TEXT NOT NULL,
    after TEXT NOT NULL)
    ''')

conn.commit()
conn.close()