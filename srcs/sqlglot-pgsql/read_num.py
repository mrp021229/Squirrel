# -*- coding: utf-8 -*-


def read_integer_from_file(filename="/home/Squirrel/srcs/sqlglot-pgsql/num.txt"):
    try:
        with open(filename, "r") as file:
            return int(file.read().strip())  # 璇�?�彇鏁存暟骞跺幓鎺�?�袱绔�绌虹櫧瀛�?���?
    except FileNotFoundError:
        # print(f"{filename} 鏂囦欢涓嶅瓨鍦ㄣ�?�?")
        return None
    except ValueError:
        # print(f"{filename} 鏂囦欢鍐�?�逛笉鏄�鏈�?�晥鐨勬暣鏁�?�?�?")
        return None

def write_integer_to_file(integer, filename="/home/Squirrel/srcs/sqlglot-pgsql/num.txt"):
    try:
        with open(filename, "w") as file:
            file.write(str(integer))  # 灏嗘暣鏁拌浆涓哄瓧绗︿�?�骞跺啓鍏ユ枃浠�?
    except Exception as e:
        pass
        # print(f"鍐欏叆鏂囦�?�鏃跺彂鐢熼敊璇�?: {e}")
if __name__ == "__main__":
    write_integer_to_file(12)
    # print(read_integer_from_file())