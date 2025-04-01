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
    num=0
    mutated_out = None
    # try 10 times and get mutated 
    while(num<=10 and mutated_out is None):
        mutated_out = sqlglot_pgsql.mutation(buf)
        num = num+1
    if mutated_out is not None:
        with open("/home/mutated_sql.txt", "a") as file:
            file.write("sql: "+buf + "\n")
            file.write("new_sql: "+mutated_out + "\n")  # 每次变异结果后加上换行符
    return mutated_out

if __name__ == "__main__":
    print("@#@#")
    print(fuzz("create table v0(v1 INT, v2 INT);",None,None))