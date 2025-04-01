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
    
    buf = buf.decode('utf-8')
    # 将多个SQL语句按照分号分隔
    sql_statements = buf.split(';')
    
    # 用来存储变异后的SQL语句
    mutated_sql_statements = []
    

    for sql in sql_statements:
        if sql.strip():  # 只处理非空的SQL语句
            num = 0
            mutated_out = None
            # 尝试变异10次
            while num <= 10 and mutated_out is None:
                mutated_out = sqlglot_pgsql.mutation(sql.strip())  # 对每个SQL语句进行变异
                num = num + 1
            if mutated_out is not None:
                mutated_sql_statements.append(mutated_out)  # 添加变异后的SQL语句
                # 将原始SQL和变异后的SQL写入文件
                with open("/home/mutated_sql.txt", "a") as file:
                    file.write("sql: " + sql + "\n")
                    file.write("new_sql: " + mutated_out + "\n")
            else:
                mutated_sql_statements.append(sql)  # 如果没有变异成功，则保持原SQL语句
        else:
            mutated_sql_statements.append(sql)  # 对于空字符串（例如分号后的空白），直接保留原值
    
    # 将变异后的SQL语句按分号拼接起来
    mutated_sql = '; '.join(mutated_sql_statements)
    return mutated_sql.encode('utf-8')

if __name__ == "__main__":
    print("@#@#")
    print(fuzz("create table v0(v1 INT, v2 INT);",None,None))