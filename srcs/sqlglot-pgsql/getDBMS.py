def getDBMS(file_path):
    db_dict = {}
    current_table = None
    columns = []

     try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            for line in lines:
                line = line.strip()
                
                # 检查表名
                if line.startswith("Table:"):
                    if current_table:
                        db_dict[current_table] = {'columns': columns, 'constraints': []}
                    current_table = line.split(":")[1].strip()
                    columns = []
                
                # 检查列名
                elif line.startswith("Column:"):
                    column_name = line.split(":")[1].strip()
                    columns.append(column_name)
            
            # 处理最后一个表
            if current_table:
                db_dict[current_table] = {'columns': columns, 'constraints': []}
    
    except FileNotFoundError:
        # 如果文件不存在，返回空字典
        return {}
    return db_dict
if __name__ == "__main__":
    # 娴嬭瘯鍑芥暟
    file_path = 'test.txt'  # 杩欓噷鏇挎崲鎴愪綘鐨勬枃浠惰矾寰�
    db_dict = getDBMS(file_path)

    # 鎵撳嵃缁撴灉
    print(db_dict)

