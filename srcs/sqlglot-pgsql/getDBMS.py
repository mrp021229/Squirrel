def getDBMS(file_path):
    db_dict = {}
    current_table = None
    columns = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            
            # 鍒ゆ柇琛ㄥ悕
            if line.startswith("Table:"):
                if current_table:
                    db_dict[current_table] = {'columns': columns, 'constraints': []}
                current_table = line.split(":")[1].strip()
                columns = []
            
            # 鍒ゆ柇鍒楀悕
            elif line.startswith("Column:"):
                column_name = line.split(":")[1].strip()
                columns.append(column_name)
        
        # 澶勭悊鏈€鍚庝竴涓�琛�
        if current_table:
            db_dict[current_table] = {'columns': columns, 'constraints': []}
    
    return db_dict
if __name__ == "__main__":
    # 娴嬭瘯鍑芥暟
    file_path = 'test.txt'  # 杩欓噷鏇挎崲鎴愪綘鐨勬枃浠惰矾寰�
    db_dict = getDBMS(file_path)

    # 鎵撳嵃缁撴灉
    print(db_dict)

