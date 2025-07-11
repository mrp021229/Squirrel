# -*- coding: utf-8 -*-
"""
Run a fuzzing instance.
"""
import os
import fire
import uuid
from pathlib import Path

DBMS = ["sqlite", "mysql", "mariadb", "postgresql", "percona", "afl_percona"]
ROOTPATH = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent


def get_mutator_so_path(database):
  if database == "mariadb":
    database = "mysql"
  return f"{ROOTPATH}/build/lib{database}_mutator.so"
def get_mutator_py_path(database):
  if database == "mariadb":
    database = "mysql"
  if database == "percona":
    database = "mysql"
  if database == "postgresql":
    database = "pgsql"
  return f"{ROOTPATH}/srcs/sqlglot-{database}"

def get_config_path(database):
  return f"{ROOTPATH}/data/config_{database}.yml"


def set_env(database):
  if database == "afl_percona":
    database = "percona"
  else :
    os.environ["AFL_CUSTOM_MUTATOR_ONLY"] = "1"
    os.environ["PYTHONPATH"] = get_mutator_py_path(database)
    os.environ["AFL_PYTHON_MODULE"] = "example"
  os.environ["AFL_DISABLE_TRIM"] = "1"
  os.environ["AFL_FAST_CAL"] = "1"
  # os.environ["AFL_CUSTOM_MUTATOR_LIBRARY"] = get_mutator_so_path(database)
  os.environ["SQUIRREL_CONFIG"] = get_config_path(database)


def run(database, input_dir, output_dir=None, config_file=None, fuzzer=None):
  # Precondition checks
  if database not in DBMS:
    print(f"Unsupported database. The supported ones are {DBMS}")
    return

  if not output_dir:
    output_dir = "/home/output"

  if not config_file:
    config_file = get_config_path(database)
  if not fuzzer:
    fuzzer = f"{ROOTPATH}/AFLplusplus/afl-fuzz"
  if not os.path.exists(config_file):
    print("Invalid path for config file")
  if not os.path.exists(fuzzer):
    print("Invalid path for afl-fuzz")

  set_env(database)

  output_id = str(uuid.uuid4())[:10]
  if database == "sqlite":
    cmd = f"{fuzzer} -i {input_dir} -o {output_dir} -M {output_id} -V 450000 -- /home/ossfuzz @@"
  else:
    cmd = f"{fuzzer} -i {input_dir} -o {output_dir} -M {output_id} -t 60000 -V 450000 -- {ROOTPATH}/build/db_driver"

  os.system(cmd)


if __name__ == "__main__":
  fire.Fire(run)
