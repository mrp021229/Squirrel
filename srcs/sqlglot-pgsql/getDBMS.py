import psycopg2

def getDBMS():
    db_dict = {}
    connection = psycopg2.connect(
        host='localhost',  # 数据库主机
        user='dobigthing',  # 数据库用户名
        password='',  # 数据库密码
        dbname='postgres'  # 数据库名称
    )

    try:
        cursor = connection.cursor()

        # 查询所有表名
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()

        if tables:
            for table in tables:
                table_name = table[0]

                # 查询表的列信息
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
                columns = cursor.fetchall()

                column_list = [column[0] for column in columns]
                db_dict[table_name] = {'columns': column_list}

    finally:
        # 关闭连接
        cursor.close()
        connection.close()

    return db_dict


if __name__ == "__main__":
    print(getDBMS())
    table_dict = {
        'table1': {'columns': ['id', 'name', 'age', 'email'], 'constraints': []},
        'table2': {'columns': ['a', 'b', 'c'], 'constraints': []},
        'table3': {'columns': ['d', 'e'], 'constraints': []}
    }
    print(table_dict)
