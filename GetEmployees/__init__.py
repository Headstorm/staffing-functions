import json
import logging
import os
import pathlib

import azure.functions as func
import pandas as pd
import psycopg2


def get_ssl_cert():
    current_path = pathlib.Path(__file__).parent.parent
    return str(current_path / "BaltimoreCyberTrustRoot.crt.pem")


def main(req: func.HttpRequest) -> func.HttpResponse:
    cur = None
    try:
        dbname = os.environ["DB_NAME"]
        pwd = os.environ["PW"]
        conn = psycopg2.connect(
            "dbname='{}' user='HSadmin@hs-azure-sql-staff-app' host='hs-azure-sql-staff-app.postgres.database.azure.com' password='{}' port='5432'".format(
                dbname, pwd
            )
        )
        cur = conn.cursor()
        logging.info("GET Employees")

        sql_command = "SELECT * FROM employee"

        cur.execute(sql_command)
        result = cur.fetchall()
        df = pd.DataFrame(result, columns=["id", "full_name", "email", "title", "is_active"])
        return func.HttpResponse(df.to_json(orient="records"), mimetype="application/json", status_code=200)
    except Exception as e:
        if cur is not None:
            cur.rollback()
        logging.warning(str(e))
        return func.HttpResponse(str(e), status_code=500)
    finally:
        if cur is not None:
            cur.close()
            conn.close()
