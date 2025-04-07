import random
import sqlglot_pgsql
def init(seed):
    pass

def deinit():
    pass

# def deinit():  # optional for Python
#     passs
def queue_new_entry(filename_new_queue, filename_orig_queue):
    return False

def fuzz_count(buf):
    return 10



def fuzz(buf, add_buf, max_size):
    print(buf)
    buf = buf.decode('utf-8')
    print(buf)
    # 将�?�个SQL�?句按照分号分�?
    sql_statements = buf.split(';')
    
    # 用来存储变异后的SQL�?�?
    mutated_sql_statements = []
    

    for sql in sql_statements:
        if sql.strip():  # �?处理非空的SQL�?�?
            num = 0
            mutated_out = None
            # 尝试变异10�?
            while num <= 10 and mutated_out is None:
                mutated_out = sqlglot_pgsql.mutation(sql.strip())  # 对每个SQL�?句进行变�?
                num = num + 1
            if mutated_out is not None:
                mutated_sql_statements.append(mutated_out)  # 添加变异后的SQL�?�?
                # 将原始SQL和变异后的SQL写入文件
                with open("/home/mutated_sql.txt", "a") as file:
                    file.write("sql: " + sql + "\n")
                    file.write("new_sql: " + mutated_out + "\n")
            else:
                mutated_sql_statements.append(sql)  # 如果没有变异成功，则保持原SQL�?�?
        else:
            mutated_sql_statements.append(sql)  # 对于空字符串（例如分号后的空白），直接保留原�?
    
    # 将变异后的SQL�?句按分号拼接起来
    mutated_sql = '; '.join(mutated_sql_statements)
    print(mutated_sql)
    return mutated_sql.encode('utf-8')

if __name__ == "__main__":
    print("@#@#")
    print(fuzz("create table v0(v1 INT, v2 INT);",None,None))