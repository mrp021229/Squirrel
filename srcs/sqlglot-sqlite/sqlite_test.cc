// test_sqlite_schema_dump.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sqlite3.h>

static int exec_sql(sqlite3 *db, const char *sql) {
    char *err = NULL;
    int rc = sqlite3_exec(db, sql, NULL, NULL, &err);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "[exec_sql] error: %s\n", err ? err : "(unknown)");
        sqlite3_free(err);
    }
    return rc;
}

int dump_schema_to_file(sqlite3 *db, const char *path) {
    FILE *fp = fopen(path, "w");
    if (!fp) {
        perror("fopen");
        return -1;
    }

    const char *q_tables =
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name;";

    sqlite3_stmt *stmt_tables = NULL;
    if (sqlite3_prepare_v2(db, q_tables, -1, &stmt_tables, NULL) != SQLITE_OK) {
        fprintf(stderr, "prepare tables failed: %s\n", sqlite3_errmsg(db));
        fclose(fp);
        return -2;
    }

    while (sqlite3_step(stmt_tables) == SQLITE_ROW) {
        const unsigned char *tname_uc = sqlite3_column_text(stmt_tables, 0);
        const char *tname = (const char*)tname_uc;

        fprintf(fp, "Table: %s\n", tname);

        char pragma_sql[512];
        snprintf(pragma_sql, sizeof(pragma_sql), "PRAGMA table_info(%s);", tname);

        sqlite3_stmt *stmt_cols = NULL;
        if (sqlite3_prepare_v2(db, pragma_sql, -1, &stmt_cols, NULL) != SQLITE_OK) {
            fprintf(stderr, "prepare pragma failed for %s: %s\n",
                    tname, sqlite3_errmsg(db));
            continue;
        }

        while (sqlite3_step(stmt_cols) == SQLITE_ROW) {
            const unsigned char *cname_uc = sqlite3_column_text(stmt_cols, 1);
            const char *cname = (const char*)cname_uc;
            fprintf(fp, "  Column: %s\n", cname);
        }
        sqlite3_finalize(stmt_cols);

        fprintf(fp, "\n"); // 表之间空一行
    }

    sqlite3_finalize(stmt_tables);
    fclose(fp);
    return 0;
}

int main(void) {
     sqlite3 *db = NULL;
    if (sqlite3_open(":memory:", &db) != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
        return 1;
    }

    // 示例建表
    sqlite3_exec(db, "CREATE TABLE v258478(v258479 INT, v258480 TEXT);", 0, 0, 0);
    sqlite3_exec(db, "CREATE TABLE v258484(v258485 TEXT, v258486 INT);", 0, 0, 0);

    // 调用导出函数
    if (dump_schema_to_file(db, "/home/src/table.txt") == 0) {
        printf("Schema dumped to table.txt\n");
    }

    sqlite3_close(db);
    
    return 0;
}
