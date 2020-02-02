#!/usr/bin/env python

import eventlet

eventlet.monkey_patch()

from eventlet import sleep
from itertools import islice
import os
import pyodbc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from toolz.curried import concat
import urllib


conn_str_mssql = "DRIVER={{{}}};SERVER={};DATABASE={};UID={};PWD={}".format(
    os.environ["MSSQL_DRIVER"],
    os.environ["MSSQL_HOST"],
    os.environ["MSSQL_CATALOG"],
    os.environ["MSSQL_USER"],
    os.environ["MSSQL_PASS"],
)
cstr = "mssql+pyodbc:///?odbc_connect={}".format(
    urllib.parse.quote_plus(conn_str_mssql)
)

cstr_psql = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    urllib.parse.quote_plus(os.environ["PSQL_USER"]),
    urllib.parse.quote_plus(os.environ["PSQL_PASS"]),
    urllib.parse.quote_plus(os.environ["PSQL_HOST"]),
    urllib.parse.quote_plus(os.environ["PSQL_PORT"]),
    urllib.parse.quote_plus(os.environ["PSQL_SCHEMA"]),
)

db_engine_mssql = create_engine(cstr)
db_engine_postgresql = create_engine(cstr_psql)
db_sessionmaker_mssql = sessionmaker(bind=db_engine_mssql)
db_sessionmaker_postgresql = sessionmaker(bind=db_engine_postgresql)


def _fetchall_with_sleep(result_proxy):
    while True:
        # recs = result_proxy.fetchmany(size=1000)
        recs = result_proxy.fetchmany(1000)
        if not recs:
            break
        yield recs
        sleep()


def fetchall_with_sleep(result_proxy):
    for x in concat(_fetchall_with_sleep(result_proxy)):
        yield x
        sleep()


sql_mssql = """
           WITH x AS (SELECT n FROM (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) v(n))
           SELECT ones.n + 10*tens.n + 100*hundreds.n + 1000*thousands.n + 10000*tenthous.n + 100000*hunthous.n + 1000000*mil.n n
           FROM x ones,     x tens,      x hundreds,       x thousands, x tenthous, x hunthous, x mil
           ORDER BY 1"""


def mssql_sqlalchemy(i, *args, **kwargs):
    sess_mssql = None
    try:
        print("pre busy mssql")
        sess_mssql = db_sessionmaker_mssql()
        recs = sess_mssql.execute(sql_mssql)
        print(", ".join(str(x[0]) for x in islice(fetchall_with_sleep(recs), 10)))
        print("post busy mssql")
        return f"{i}: mssql done"
    finally:
        if sess_mssql:
            sess_mssql.close()


def mssql_pyodbc(i, *args, **kwargs):
    cnxn = None
    try:
        print("pre busy mssql")
        cnxn = pyodbc.connect(conn_str_mssql)
        cursor = cnxn.cursor()
        cursor.execute(sql_mssql)
        print(", ".join(str(x[0]) for x in islice(fetchall_with_sleep(cursor), 10)))
        print("post busy mssql")
        return f"{i}: mssql done"
    finally:
        if cnxn:
            cnxn.close()


def psql_sqlalchemy(i, *args, **kwargs):
    sess_psql = None
    try:
        print("pre busy postgresql")
        sess_psql = db_sessionmaker_postgresql()
        recs = sess_psql.execute("SELECT * FROM generate_series(1,1000000)")
        print(", ".join(str(x[0]) for x in islice(fetchall_with_sleep(recs), 10)))
        print("post busy postgresql")
        return f"{i}: psql done"
    finally:
        if sess_psql:
            sess_psql.close()


if __name__ == "__main__":
    pool = eventlet.GreenPool()
    for data in pool.imap(mssql_pyodbc, range(1, 16)):
        print(data)
