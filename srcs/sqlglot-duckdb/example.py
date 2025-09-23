# -*- coding: utf-8 -*-
import os
import subprocess
import random
import signal
import sqlglot
import sqlglot_mutation
import sqlglot_fill
from sqlglot_manager import ExpressionSetManager
expression_manager = None

def init(seed):
    global expression_manager
    expression_manager = ExpressionSetManager()
    expression_manager.load_from_file("/home/Squirrel/srcs/sqlglot-duckdb/duckdb_seed.pkl")  # 替换为实际路径
    sqlglot_mutation.set_expression_manager(expression_manager)  # 注入给子模块
    sqlglot_fill.set_expression_manager(expression_manager)
    # with open("/home/memtest.txt", "a") as f:
    #     f.write(f"Main module expression_manager id: {id(expression_manager)}\n")
    # try:
    #     with open("/home/database.txt", "w") as f:
    #         f.write("1")
    #     print("[mutator] init: wrote 1 to /home/database.txt")
    # except Exception as e:
    #     print(f"[mutator] init: failed to write to file - {e}")
    # return 0


def deinit():
    pass


# def deinit():  # optional for Python
#     passs
def queue_new_entry(filename_new_queue, filename_orig_queue):
    return False


def fuzz_count(buf):
    return 2


def mutation(sql):
    mutated_sql = sqlglot_mutation.get_mutated_sql(sql)
    filled_sql = sqlglot_fill.fill_sql(mutated_sql)
    return filled_sql
    


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("fuzz() execution timed out")

signal.signal(signal.SIGALRM, timeout_handler)

def fuzz(buf, add_buf, max_size):
    try:
        signal.alarm(15)  # 
        try:
            buf = buf.decode('utf-8')
            sql_statements = buf.split(';')

            mutated_sql_statements = []

            for sql in sql_statements:
                if sql.strip():
                    mutated_out = None
                    new_sql = None
                    # try :

                    #     new_sql = sqlglot.parse_one(sql,dialect='duckdb')
                    #     new_sql = expression_manager.get_new_sql(new_sql)
                    #     new_sql = new_sql.sql()
                    # except Exception:
                    #     new_sql = None
                    # if random.random()>0.2:
                    try:
                        mutated_out = mutation(sql.strip())
                    except Exception:
                        mutated_out = None

                    if mutated_out is not None:
                        mutated_sql_statements.append(mutated_out)
                    else:
                        if new_sql is not None:
                            try:
                                mutated_out = mutation(new_sql)
                            except Exception:
                                mutated_out = None
                            if mutated_out is not None:
                                mutated_sql_statements.append(mutated_out)
                    # else:
                    #     if new_sql is not None:
                    #         try:
                    #             mutated_out = mutation(new_sql)
                    #         except Exception:
                    #             mutated_out = None
                    #         if mutated_out is not None:
                    #             mutated_sql_statements.append(mutated_out)
                        

            mutated_sql = '; '.join(mutated_sql_statements)
            mutated_sql = mutated_sql.replace('\ufffd', '[INV]')
            mutated_sql = mutated_sql.encode('utf-8', errors='ignore')
            buf = bytearray(mutated_sql)

            if len(buf) == 0:
                buf = bytearray(b'0')

        finally:
            try:
                with open("/home/check.txt", "r+") as f:
                    f.seek(0)
                    f.write("2\n")
                    f.truncate()
            except Exception:
                pass

    except TimeoutException:
        buf = bytearray(b'0')  # 
        with open("/home/timelog.txt","a") as f:
            f.write("!")
    finally:
        signal.alarm(0)  # 

    return buf



def test(n):
    buf = 0
    try:
        signal.alarm(5)  # 
        sleep(n)

    except TimeoutException:
        buf = 1
    finally:
        signal.alarm(0)  # 

    return buf


if __name__ == "__main__":
    for i in range(10):
        print(test)