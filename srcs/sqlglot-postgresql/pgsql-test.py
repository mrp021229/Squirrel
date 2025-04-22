import time
import psycopg2
from psycopg2 import OperationalError


# 杩炴帴鍒癙ostgreSQL鏁版嵁搴�
def create_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",  # 鏁版嵁搴撲富鏈�
            user="postgres",  # 鏁版嵁搴撶敤鎴峰悕
            password="root",  # 鏁版嵁搴撳瘑鐮�
            database="postgres"  # 鏁版嵁搴撳悕绉�
        )
        print("Successfully connected to the database")
        return connection
    except OperationalError as e:
        print(f"Error: {e}")
        return None


# 鎵ц�孲QL鏂囦欢涓�鐨勮��鍙ワ紙閫愭潯鎻愪氦锛�
def execute_sql_from_file(connection, file_path):
    success_sql = []
    fail_sql = []
    cursor = None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            sql_statements = file.read().split(";")  # 鍒嗗壊鎴愬崟鏉�SQL璇�鍙�

        successful_count = 0
        cursor = connection.cursor()

        for sql in sql_statements:
            sql = sql.strip()  # 鍘绘帀棣栧熬绌虹櫧瀛楃��
            if sql:  # 纭�淇漇QL璇�鍙ラ潪绌�
                try:
                    cursor.execute(sql)
                    connection.commit()  # **姣忔墽琛屼竴鏉� SQL 璇�鍙ュ悗鎻愪氦**
                    successful_count += 1
                    success_sql.append(sql)
                except Exception as e:
                    print(f"Error executing SQL: {e}. SQL: {sql}")
                    fail_sql.append(sql)
                    connection.rollback()  # 浠呭洖婊氬け璐ョ殑 SQL 璇�鍙�
                    continue

        print(f"Total successful SQL statements executed: {successful_count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()

    return success_sql, fail_sql


# 涓荤▼搴�
if __name__ == "__main__":
    start_time = time.time()
    connection = create_connection()

    if connection:
        success_sql, fail_sql = execute_sql_from_file(connection, "E:\your PhD\姣曡�綷sqlglot\sqlglot-pgsql\\filledSQL.txt")
        connection.close()

        print("\nSUCCESS SQL:")
        for a in success_sql:
            print(a)

        print("\nFAIL SQL:")
        for b in fail_sql:
            print(b)

        print("\n鎴愬姛鎵ц�岀殑SQL鏁伴噺:", len(success_sql))
        print("澶辫触鐨凷QL鏁伴噺:", len(fail_sql))

    end_time = time.time()
    print("杩愯�屾椂闂�:", end_time - start_time, "绉�")

# 686 572
# 657    431