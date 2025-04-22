# -*- coding: utf-8 -*-

import random
import sqlglot_mysql
import sqlglot
def init(seed):
    pass

def deinit():
    pass

# def deinit():  # optional for Python
#     passs
def queue_new_entry(filename_new_queue, filename_orig_queue):
    return False
def fuzz_count(buf):
    return 2

def fuzz(buf, add_buf, max_size):
    buf = buf.decode('utf-8')
    sql_statements = buf.split(';')
    
    
    mutated_sql_statements = []
    

    for sql in sql_statements:

        if sql.strip():  
            num = 0
            mutated_out = None
            
            while num <= 10 and mutated_out is None:
                try:
                    mutated_out = sqlglot_mysql.mutation(sql.strip())

                except Exception as e:
                    mutated_out = None

                else:
                    pass
                num = num + 1
            if mutated_out is not None:
                mutated_sql_statements.append(mutated_out)  
                # # 
                # with open("/home/mutated_sql.txt", "a") as file:
                #     file.write("sql: " + sql + "\n")
                #     file.write("new_sql: " + mutated_out + "\n")
            else:
                mutated_sql_statements.append(sql)  
        else:
            mutated_sql_statements.append(sql)  
    
    print(mutated_sql_statements)
    mutated_sql = '; '.join(mutated_sql_statements)
    # mutated_sql = mutated_sql.replace('\ufffd', '[INV]')
    mutated_sql = mutated_sql.encode('utf-8', errors='ignore')
    buf = mutated_sql
    buf = bytearray(buf)
    return buf
# def strToBytearray(sql):
#     byte = sql.encode('utf-8')
#     byteArray = bytearray(byte)
#     return byteArray

if __name__ == "__main__":
    print("@#@#")
    sql = "select a from b where c = 3;select c from a;"
    tmp=strToBytearray(sql)
    print(fuzz(tmp,None,None))