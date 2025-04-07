def getDBMS(file_path="/home/table_column_list.txt"):
    db_dict = {}
    current_table = None
    columns = []

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            for line in lines:
                line = line.strip()
                
                # 检查表�?
                if line.startswith("Table:"):
                    if current_table:
                        db_dict[current_table] = {'columns': columns, 'constraints': []}
                    current_table = line.split(":")[1].strip()
                    columns = []
                
                # 检查列�?
                elif line.startswith("Column:"):
                    column_name = line.split(":")[1].strip()
                    columns.append(column_name)
            
            # 处理最后一�?�?
            if current_table:
                db_dict[current_table] = {'columns': columns, 'constraints': []}
    
    except FileNotFoundError:
        # 如果文件不存�?，返回空字典
        # print("FileNotFound")
        return {}
    # print(db_dict)
    return db_dict
if __name__ == "__main__":
    # 娴�??�?鍑芥�?
    file_path = 'test.txt'  # 杩欓噷鏇挎崲鎴愪綘鐨�?枃浠惰矾寰�
    db_dict = getDBMS(file_path)

    # 鎵撳嵃缁撴灉
    # print(db_dict)

