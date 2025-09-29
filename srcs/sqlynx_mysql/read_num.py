# -*- coding: utf-8 -*-


def read_integer_from_file(filename="/home/Squirrel/srcs/sqlynx_mysql/num.txt"):
    try:
        with open(filename, "r") as file:
            return int(file.read().strip())  # 
    except FileNotFoundError:
        # print(f"{filename} 
        return None
    except ValueError:
        # print(f"{filename} 
        return None

def write_integer_to_file(integer, filename="/home/Squirrel/srcs/sqlynx_mysql/num.txt"):
    try:
        with open(filename, "w") as file:
            file.write(str(integer))  # 灏嗘暣鏁拌浆涓哄瓧绗︿�?�骞跺啓鍏ユ枃浠�?
    except Exception as e:
        pass
        # print(f": {e}")
if __name__ == "__main__":
    write_integer_to_file(12)
    # print(read_integer_from_file())