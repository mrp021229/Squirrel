def read_integer_from_file(filename="/home/Squirrel/srcs/sqlglot-pgsql/num.txt"):
    try:
        with open(filename, "r") as file:
            return int(file.read().strip())  # 璇诲彇鏁存暟骞跺幓鎺変袱绔�绌虹櫧瀛楃��
    except FileNotFoundError:
        print(f"{filename} 鏂囦欢涓嶅瓨鍦ㄣ€�")
        return None
    except ValueError:
        print(f"{filename} 鏂囦欢鍐呭�逛笉鏄�鏈夋晥鐨勬暣鏁般€�")
        return None

def write_integer_to_file(integer, filename="/home/Squirrel/srcs/sqlglot-pgsql/num.txt"):
    try:
        with open(filename, "w") as file:
            file.write(str(integer))  # 灏嗘暣鏁拌浆涓哄瓧绗︿覆骞跺啓鍏ユ枃浠�
    except Exception as e:
        print(f"鍐欏叆鏂囦欢鏃跺彂鐢熼敊璇�: {e}")
if __name__ == "__main__":
    write_integer_to_file(12)
    print(read_integer_from_file())