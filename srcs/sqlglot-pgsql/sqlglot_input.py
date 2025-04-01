import os
import glob
import chardet
import sqlglot
def strip_semantics(sql,read='postgres'):
    # 瑙ｆ瀽 SQL 璇�鍙ヤ负璇�娉曟爲
    try:
        tree = sqlglot.parse_one(sql,read=read)
    except sqlglot.errors.ParseError as e:
        return None

    # print(tree)
    # 鏇挎崲鍒楀悕銆佽〃鍚嶃€佸瓧绗︿覆銆佹暟瀛椾负鍗犱綅绗�
    def replace_node(node):
        # print(node)
        if node is None:
            return
        if isinstance(node, sqlglot.exp.Identifier):  # 琛ㄥ悕鎴栧垪鍚�
            node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Literal):  # 瀛楃�︿覆鎴栨暟瀛�
        #     node.set("this", "x")
        elif isinstance(node, sqlglot.exp.Table):  # 琛ㄥ紩鐢�
            node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Star): # *涓嶅�勭悊
        #     node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Column):
        #     node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Null):  # NULL 鐨勫�勭悊 #null涓嶅�勭悊
        #     node.set("this", "x")
        # 澶勭悊澶栭敭绾︽潫绛�
        elif isinstance(node, sqlglot.exp.ForeignKey):  # 澶栭敭绾︽潫
            for child in node.args.values():
                replace_node(child)

        elif isinstance(node, sqlglot.exp.Check):  # CHECK绾︽潫
            for child in node.args.values():
                replace_node(child)

        # 纭�淇濆瓙鑺傜偣鏄� Expression 鎴� list锛岃€屼笉鏄� string
        if hasattr(node, 'args'):
            for child in node.args.values():
                if isinstance(child, list):
                    for c in child:
                        replace_node(c)
                elif isinstance(child, sqlglot.Expression):
                    replace_node(child)

    def replace_x(tree):
        for node in tree.walk():
            if isinstance(node, sqlglot.exp.TableAlias):
                node.set('columns', None)
            if isinstance(node, sqlglot.exp.Identifier):  # 琛ㄥ悕鎴栧垪鍚�
                node.set("this", "x")
            # elif isinstance(node, sqlglot.exp.Literal):  # 瀛楃�︿覆鎴栨暟瀛�
            #     node.set("this", "x")
            elif isinstance(node, sqlglot.exp.Table):  # 琛ㄥ紩鐢�
                node.set("this", "x")

    replace_x(tree)
    # replace_node(tree)

    # 杩斿洖鍓ョ�诲悗鐨� SQL
    return tree.sql()
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        return encoding if confidence > 0.5 else None

def parse_sql(sql):
    """
    灏濊瘯鐢� sqlglot 瑙ｆ瀽 SQL 璇�鍙ワ紝瑙ｆ瀽鎴愬姛杩斿洖璇�鍙ワ紝澶辫触杩斿洖 None銆�
    """
    try:

        parsed_sql = strip_semantics(sql,read='postgres')
        print("sdfsdf")
        print(sql)

        return parsed_sql  # 杩斿洖鍘熷�� SQL锛堝�傛灉闇€瑕佽繘涓€姝ュ�勭悊鍙�浠ヤ慨鏀癸級
    except Exception:
        return None
def extract_sql_statements(test_dir, output_file):
    # 鏌ユ壘 test_dir 鐩�褰曚笅鐨勬墍鏈� .sql 鏂囦欢
    sql_files = glob.glob(os.path.join(test_dir, '**', '*.sql'), recursive=True)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for sql_file in sql_files:
            encoding = detect_encoding(sql_file)
            if encoding is None:
                print(f"鏃犳硶妫€娴嬫枃浠� {sql_file} 鐨勭紪鐮佹牸寮忥紝宸茶烦杩囥€�")
                continue


            with open(sql_file, 'r', encoding='utf-8', errors='replace') as infile:
                sql_content = infile.read()
                # 灏嗘枃浠跺唴瀹逛腑鐨勬瘡涓� SQL 璇�鍙ュ悎骞朵负涓€琛�
                sql_statements = sql_content.split(';')



                for statement in sql_statements:
                    statement = statement.strip()
                    statement = parse_sql(statement)
                    if statement:
                        outfile.write(statement.replace('\n', ' ') + ';\n')


if __name__ == "__main__":
    test_directory = 'E:\your PhD\姣曡�綷sqlglot\postgres\src\\test'  # 璇峰皢姝よ矾寰勬浛鎹�涓� PostgreSQL 婧愮爜涓� test 鐩�褰曠殑瀹為檯璺�寰�
    output_filename = 'pgsql_seed.txt'
    extract_sql_statements(test_directory, output_filename)
    print(f"SQL 璇�鍙ュ凡鎻愬彇骞朵繚瀛樺埌 {output_filename}")
