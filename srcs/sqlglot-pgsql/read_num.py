def read_integer_from_file(filename="/houm/Squirrel/srcs/sqlglot-pgsql/num.txt"):
    try:
        with open(filename, "r") as file:
            return int(file.read().strip())  # 读取整数并去掉两�?空白字�??
    except FileNotFoundError:
        print(f"{filename} 文件不存在�?")
        return None
    except ValueError:
        print(f"{filename} 文件内�?�不�?有效的整数�?")
        return None

def write_integer_to_file(integer, filename="/houm/Squirrel/srcs/sqlglot-pgsql/num.txt"):
    try:
        with open(filename, "w") as file:
            file.write(str(integer))  # 将整数转为字符串并写入文�?
    except Exception as e:
        print(f"写入文件时发生错�?: {e}")
if __name__ == "__main__":
    write_integer_to_file(12)
    print(read_integer_from_file())