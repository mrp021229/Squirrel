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

    # �����SQL��䰴�շֺŷָ�
    sql_statements = buf.split(';')
    
    # �����洢������SQL���
    mutated_sql_statements = []
    

    for sql in sql_statements:
        if sql.strip():  # ֻ����ǿյ�SQL���
            num = 0
            mutated_out = None
            # ���Ա���10��
            while num <= 10 and mutated_out is None:
                mutated_out = sqlglot_pgsql.mutation(sql.strip())  # ��ÿ��SQL�����б���
                num = num + 1
            if mutated_out is not None:
                mutated_sql_statements.append(mutated_out)  # ��ӱ�����SQL���
                # ��ԭʼSQL�ͱ�����SQLд���ļ�
                with open("/home/mutated_sql.txt", "a") as file:
                    file.write("sql: " + sql + "\n")
                    file.write("new_sql: " + mutated_out + "\n")
            else:
                mutated_sql_statements.append(sql)  # ���û�б���ɹ����򱣳�ԭSQL���
        else:
            mutated_sql_statements.append(sql)  # ���ڿ��ַ���������ֺź�Ŀհף���ֱ�ӱ���ԭֵ
    
    # ��������SQL��䰴�ֺ�ƴ������
    return '; '.join(mutated_sql_statements)

if __name__ == "__main__":
    print("@#@#")
    print(fuzz("create table v0(v1 INT, v2 INT);",None,None))