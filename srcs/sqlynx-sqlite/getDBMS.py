# -*- coding: utf-8 -*-


def getDBMS(file_path="/home/table_column_list.txt"):
    db_dict = {}
    current_table = None
    columns = []

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            for line in lines:
                line = line.strip()
                
                # 
                if line.startswith("Table:"):
                    if current_table:
                        db_dict[current_table] = {'columns': columns, 'constraints': []}
                    current_table = line.split(":")[1].strip()
                    columns = []
                
                # 
                elif line.startswith("Column:"):
                    column_name = line.split(":")[1].strip()
                    columns.append(column_name)
            
            # 
            if current_table:
                db_dict[current_table] = {'columns': columns, 'constraints': []}
    
    except FileNotFoundError:
        # 
        # print("FileNotFound")
        return {}
    # print(db_dict)
    return db_dict
if __name__ == "__main__":
    # 
    file_path = 'test.txt'  # 
    db_dict = getDBMS(file_path)

    # 
    # print(db_dict)

