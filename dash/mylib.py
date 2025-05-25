import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime


def db_to_df_random(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute("SELECT count(*) FROM " + table_name)
    cnt = query.fetchall()[0][0]
    rid = str(np.random.randint(0,cnt,1)[0])
    query = "SELECT * From " + table_name + " where rowid=" + rid
    out = cur.execute( query )    
    cols = [column[0] for column in out.description]
    result = pd.DataFrame.from_records(data=out.fetchall(), columns=cols)
    con.close()
    return result



def drop_table(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute( "DROP TABLE " + table_name)    
    con.close()

def db_to_df(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute( "SELECT * From " + table_name  )    
    cols = [column[0] for column in query.description]
    result = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    con.close()
    return result


def db_to_df_rescent(db_name, table_name, time_col, period):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute( "SELECT * From " + table_name + " where " + time_col + " <= '" +  str(pd.to_datetime(datetime.now())) + "' AND "+time_col+" >= '" + str(pd.to_datetime(datetime.now()) - pd.to_timedelta(period)) + "'"  )
    cols = [column[0] for column in query.description]
    result = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    con.close()
    return result




def df_to_db(df_name, db_name, table_name):
    con = sqlite3.connect(db_name)
    df_name.to_sql(table_name, con,  if_exists='append', index=False)    
    con.close()

    

def df_to_db_col_only(df_name, db_name, table_name ):
    con = sqlite3.connect(db_name)
    df_name[:0].to_sql(table_name, con,  if_exists='append', index=False)
    con.close() 


def db_last_row_to_df(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute( "SELECT * FROM " + table_name + " ORDER BY rowid DESC LIMIT 1")
    cols = [column[0] for column in query.description]
    result = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    con.close()
    return result    

