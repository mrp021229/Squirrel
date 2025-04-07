import sqlglot
import sqlglot_manager
import sqlglot_mutation
import sqlglot_fill
import sys

def mutation(sql):
    mutated_sql = sqlglot_mutation.get_mutated_sql(sql)
    print("mutation")
    print(mutated_sql)
    filled_sql = sqlglot_fill.fill_sql(mutated_sql)
    print("fill")
    return filled_sql

if __name__ == "__main__":

    
    print(sqlglot_fill.fill_sql("INSERT INTO x (x, x) VALUES ('______`___________', '_CA01__')"))