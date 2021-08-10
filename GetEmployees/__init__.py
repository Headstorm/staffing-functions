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
    try:
        dbname = os.environ["DB_NAME"]
        pwd = os.environ["PW"]
        logging.info(dbname, pwd)
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

        cur.close()
        conn.close()

        return func.HttpResponse(df.to_json(orient="records"), mimetype="application/json", status_code=200)
    except Exception as e:
        cur.close()
        conn.close()
        logging.warning(str(e))
        return func.HttpResponse(json.dumps(e, default=str), status_code=500)
