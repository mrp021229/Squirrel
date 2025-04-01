def getDBMS(file_path):
    db_dict = {}
    current_table = None
    columns = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            
            # 判断表名
            if line.startswith("Table:"):
                if current_table:
                    db_dict[current_table] = {'columns': columns, 'constraints': []}
                current_table = line.split(":")[1].strip()
                columns = []
            
            # 判断列名
            elif line.startswith("Column:"):
                column_name = line.split(":")[1].strip()
                columns.append(column_name)
        
        # 处理最后一个表
        if current_table:
            db_dict[current_table] = {'columns': columns, 'constraints': []}
    
    return db_dict
if __name__ == "__main__":
    # 测试函数
    file_path = 'test.txt'  # 这里替换成你的文件路径
    db_dict = getDBMS(file_path)

    # 打印结果
    print(db_dict)

