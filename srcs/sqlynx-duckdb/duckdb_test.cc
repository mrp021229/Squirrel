#include <iostream>
#include <fstream>
#include <string>
#include <duckdb.hpp>

int dump_schema_to_file(duckdb::Connection &conn, const std::string &path) {
    std::ofstream out(path);
    if (!out.is_open()) {
        perror("fopen");
        return -1;
    }

    auto result = conn.Query(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' AND table_type='BASE TABLE' "
        "ORDER BY table_name;");

    if (result->HasError()) {
        std::cerr << "[dump] failed to get table list: " << result->GetError() << "\n";
        return -2;
    }

    for (size_t i = 0; i < result->RowCount(); ++i) {
        std::string tname = result->GetValue(0, i).ToString();
        out << "Table: " << tname << "\n";

        auto col_result = conn.Query("PRAGMA table_info(" + tname + ");");
        if (col_result->HasError()) {
            std::cerr << "[dump] failed to get columns for " << tname << ": "
                      << col_result->GetError() << "\n";
            continue;
        }

        for (size_t j = 0; j < col_result->RowCount(); ++j) {
            std::string cname = col_result->GetValue(1, j).ToString();
            out << "  Column: " << cname << "\n";
        }

        out << "\n";
    }

    out.close();
    return 0;
}

int main() {
    duckdb::DuckDB db("/home/src/test.duckdb");
    duckdb::Connection conn(db);

    conn.Query("CREATE TABLE v258479(v258480 INT, v258481 TEXT);");
    conn.Query("CREATE TABLE v258485(v258486 TEXT, v258487 INT);");

    if (dump_schema_to_file(conn, "/home/table.txt") == 0) {
        std::cout << "Schema dumped to table.txt\n";
    }

    return 0;
}
// LD_LIBRARY_PATH=/home/bld/src ./duckdb_test