import time
import psycopg2
from psycopg2 import OperationalError


# 连接到PostgreSQL数据库
def create_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",  # 数据库主机
            user="postgres",  # 数据库用户名
            password="root",  # 数据库密码
            database="postgres"  # 数据库名称
        )
        print("Successfully connected to the database")
        return connection
    except OperationalError as e:
        print(f"Error: {e}")
        return None


# 执行SQL文件中的语句（逐条提交）
def execute_sql_from_file(connection, file_path):
    success_sql = []
    fail_sql = []
    cursor = None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            sql_statements = file.read().split(";")  # 分割成单条SQL语句

        successful_count = 0
        cursor = connection.cursor()

        for sql in sql_statements:
            sql = sql.strip()  # 去掉首尾空白字符
            if sql:  # 确保SQL语句非空
                try:
                    cursor.execute(sql)
                    connection.commit()  # **每执行一条 SQL 语句后提交**
                    successful_count += 1
                    success_sql.append(sql)
                except Exception as e:
                    print(f"Error executing SQL: {e}. SQL: {sql}")
                    fail_sql.append(sql)
                    connection.rollback()  # 仅回滚失败的 SQL 语句
                    continue

        print(f"Total successful SQL statements executed: {successful_count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()

    return success_sql, fail_sql


# 主程序
if __name__ == "__main__":
    start_time = time.time()
    connection = create_connection()

    if connection:
        success_sql, fail_sql = execute_sql_from_file(connection, "E:\your PhD\毕设\sqlglot\sqlglot-pgsql\\filledSQL.txt")
        connection.close()

        print("\nSUCCESS SQL:")
        for a in success_sql:
            print(a)

        print("\nFAIL SQL:")
        for b in fail_sql:
            print(b)

        print("\n成功执行的SQL数量:", len(success_sql))
        print("失败的SQL数量:", len(fail_sql))

    end_time = time.time()
    print("运行时间:", end_time - start_time, "秒")

# 686 572
# 657    431