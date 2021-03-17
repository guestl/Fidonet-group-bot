# -*- coding: utf-8 -*-

# helper for work with database
import sqlite3

import config

import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(config.LOGGER_LEVEL)


os.chdir(os.path.dirname(os.path.abspath(__file__)))


class fidonetbot_db_helper:
    """class helper for work with SQLite3 database

    methods:
        __init__ -- setup db setting
        add_currency_rates_data -- insert parsed data into rates table
    """

    def __init__(self, dbname=config.dbname):
        self.dbname = dbname

        logger.debug(dbname)
        try:
            self.connection = sqlite3.connect(dbname, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logger.error(dbname)
            logger.error(e)
            raise e
        self.tg_userId_list = self.get_list_of_tg_userid()
        logger.info(self.tg_userId_list)

    # I got this piece of code from
    #    http://stackoverflow.com/questions/5266430/how-to-see-the-real-sql-query-in-python-cursor-execute"
    # it doesn't work pretty good,
    #   but I can see a sql text and it's enough for me
    def check_sql_string(self, sql_text, values):
        unique = "%PARAMETER%"
        sql_text = sql_text.replace("?", unique)
        for v in values:
            sql_text = sql_text.replace(unique, repr(v), 1)
        return sql_text

# search is case insensitive
    def get_fidodata_by_text(self, tg_data):
        result = ''

        try:
            sql_text = 'SELECT fido_addr, fido_name, tg_username, tg_name \
                FROM fidonetlist\
                WHERE fido_addr LIKE "%{data}" \
                order by fido_addr LIMIT 1\
                COLLATE NOCASE'.format(data=tg_data)

#            logger.info(sql_text)
            self.cursor.execute(sql_text)
        except Exception as e:
            logger.error(e)
            logger.error(self.check_sql_string(sql_text))

        if self.cursor:
            for row in self.cursor:
                data = row[0] + ", " + row[1]
                if (row[2] is not None):
                    data = data + (", @" + row[2])
                result = data

        return result

    def get_list_of_tg_userid(self):
        try:
            sql_text = 'SELECT user_id \
                FROM fidonetlist\
                WHERE user_id is not Null\
                group by user_id'

            self.cursor.execute(sql_text)
        except Exception as e:
            logger.error(e)
            logger.error(self.check_sql_string(sql_text, ''))

        result = list()
        if self.cursor:
            for row in self.cursor:
                result.append(row[0])
        return result

    def update_by_somename(self, user_id, tg_name, tg_username=None):
        if user_id in self.tg_userId_list:
            return

        update_by_somename_Query = ("update fidonetlist"
                                    " set user_id = ?"
                                    " where tg_name = ?")
        where_idx = tg_name

        if tg_name:
            update_by_somename_Query = ("update fidonetlist"
                                        " set user_id = ?"
                                        " where tg_username = ?")
            where_idx = tg_username

        try:
            self.cursor.execute(update_by_somename_Query, (user_id, where_idx, ))
            self.connection.commit()
        except Exception as e:
            logger.error(e)
            logger.error(self.check_sql_string(update_by_somename_Query,
                                               (user_id, tg_username, )))

        self.tg_userId_list = self.get_list_of_tg_userid()
        logger.info(self.tg_userId_list)
        return self.cursor.rowcount
