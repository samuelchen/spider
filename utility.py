#!/usr/bin/python
#-*- coding=UTF-8 -*-
'''
Created on Mar 23, 2011

@author: Sam
'''

import sys
import sqlite3
import logging
import time

class DatabaseUtility(object):
    _database = ''
    _connection = None
    AUTO_COMMIT = False
    _log = None
    
    def __init__(self):
        self._log = logging.getLogger('DB')
        self._log.debug('DatabaseUtilify initialized.')
        return
    
    __cls_connections = {}
    @classmethod
    def _connect(cls, db, usr=None, pwd=None):
        if db in cls.__cls_connections:
            cls.__cls_connections[db][0] += 1
            return cls.__cls_connections[db][1]
        conn = sqlite3.connect(db)
        cls.__cls_connections[db] = [1, conn]
        return conn
        
    
    @classmethod
    def _disconnect(cls, db):
        if db in cls.__cls_connections:
            cls.__cls_connections[db][0] -= 1
            if cls.__cls_connections[db][0] == 0:
                cls.__cls_connections[db][1].close()
                del cls.__cls_connections[db]
                return
        
            
    @property
    def connection(self):
        return self._connection
    
    @connection.setter
    def connection(self, conn):
        self._connection = conn

    def open(self, db, usr=None, pwd=None):
        
        if self._connection:
            return False
        
        rc = False
        try:
            self._database = db
            #self._connection = sqlite3.connect(database)
            self._connection = DatabaseUtility._connect(db)
            self.set_row_type(sqlite3.Row) # data ctor() for each row
            self._log.info('Database "%s" is connected.' % self._database)
            rc = True
        except:
            self._log.error('Database "%s" is NOT connected.' % self._database)
            err = sys.exc_info()[0]
            err_msg = sys.exc_info()[1]                 
            self._log.debug('%s, %s' % (err, err_msg))
            
        
        return rc
    
    def close(self):
        rc = False
        try:
#            if self._connection:
#                self._connection.close()
            DatabaseUtility._disconnect(self._database)
            self._connection = None
            self._log.info('Database "%s" is disconnected.' % self._database)
            self._database = None
            rc = True        
        except:
            err = sys.exc_info()[0]
            err_msg = sys.exc_info()[1]                 
            self._log.error('Exception occurs while closing database "%s".' % self._database)
            self._log.debug('%s, %s' % (err, err_msg))        
        return rc
    
    def commit(self):
        if not self._connection:
            return False
                
        rc = False
        try:
            self._connection.commit()
            self._log.info('Database "%s" is committed.' % self._database)
            rc = True
        except:
            err = sys.exc_info()[0]
            err_msg = sys.exc_info()[1]                 
            self._log.error('Database "%s" is NOT committed.' % self._database)
            self._log.debug('%s, %s' % (err, err_msg))        
        return rc
    
    def set_row_type(self, row_type=sqlite3.Row):
        '''
            Change the row factory of the connection.
            Default is tuple. You may use tuple, sqlite3.Row or etc.
            row_factory : class constructor.
        '''
        self._connection.row_factory = row_type
        
    def cursor(self):
        return self._connection.cursor()
        
    def execute(self, sql, parameters=None, succeed_msg=None, failure_msg=None):
        if not self._connection:
            return False, None, 0
        
        rc = False
        cur = self._connection.cursor()
        duration = time.clock()
        try:
            if parameters:
                cur.execute(sql, parameters)
            else:
                cur.execute(sql)
            duration = time.clock() - duration
            if self.AUTO_COMMIT:
                self.commit()
            rc = True
            if succeed_msg:
                self._log.info(succeed_msg)
        except KeyboardInterrupt:
            raise KeyboardInterrupt                
        except:
            duration = time.clock() - duration
            if failure_msg:
                self._log.warning(failure_msg)
            else:
                self._log.warning("Fail to execute Query:\r\n%s\r\n" % sql)
                self._log.warning("Parameters: {0}".format(parameters)) 
            err = sys.exc_info()[0]
            err_msg = sys.exc_info()[1]
            self._log.debug('%s, %s' % (err, err_msg))
        return rc, cur, duration
    
    def execute_none_query(self, sql, parameters=None, succeed_msg=None, failure_msg=None):
        if not self._connection:
            return False, None, 0
        
        rc = False
        val = None
        cur = self._connection.cursor()
        duration = time.clock()
        try:
            if parameters:
                cur.execute(sql, parameters)
            else:
                cur.execute(sql)
            duration = time.clock() - duration
            if self.AUTO_COMMIT:
                self.commit()
            row = cur.fetchone()
            if row:
                val = row[0]
            if succeed_msg:
                self._log.info(succeed_msg)
            rc = True
        except KeyboardInterrupt:
            raise KeyboardInterrupt        
        except:
            duration = time.clock() - duration
            if failure_msg:
                self._log.warning(failure_msg)
            else:
                self._log.warning("Fail to execute Query:\r\n%s\r\n" % sql)
                self._log.warning("Query parameters: {0}".format(parameters)) 
            err = sys.exc_info()[0]
            err_msg = sys.exc_info()[1]
            self._log.debug('%s, %s' % (err, err_msg))
        return rc, val, duration
    
    def execute_script(self, script, succeed_msg=None, failure_msg=None):
        if not self._connection:
            return False, None, 0
        
        rc = False
        duration = time.clock()
        try:
            self._connection.executescript(script)
            duration = time.clock() - duration
            if self.AUTO_COMMIT:
                self.commit()
            if succeed_msg:
                self._log.info(succeed_msg)
            rc = True
        except KeyboardInterrupt:
            raise KeyboardInterrupt            
        except:
            duration = time.clock() - duration
            if failure_msg:
                self._log.warning(failure_msg)
            else:
                self._log.warning("Fail to execute script:\r\n%s\r\n" % script)
            err = sys.exc_info()[0]
            err_msg = sys.exc_info()[1]
            self._log.debug('%s, %s' % (err, err_msg))
        return rc, duration
    
def main():
    dbutil = DatabaseUtility()
    dbutil.open('../../yule.sqlite3')
    succeed, cur, dur = dbutil.execute('select * from actor')
    if succeed:
        for row in cur:
            for item in row:
                print '"%s"' % item,
            print
        print 'Query uses %f ms' % dur
    else:
        sys.stderr.writelines('failed')
    dbutil.close()

def none_query():
    dbutil = DatabaseUtility()
    dbutil.open('../../../db/movie.db')
    succeed, cnt, dur = dbutil.execute_none_query('select count(id) from actor')
#    for row in cnt:
#        print type(row)
#        for item in row:
#            print type(item)
#            print '"%s"' % item,
#        print
    print cnt, type(cnt)
    print 'Query uses %f ms' % dur
    dbutil.close()
    
if __name__ == '__main__':
    from sam.logging import init_log
    init_log(lvl=10)
    none_query()
    #main()
