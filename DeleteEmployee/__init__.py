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
    conn = None
    try:
        id = req.route_params.get("id")
        # logging.info("id : {}".format(id))
        dbname = os.environ["DB_NAME"]
        pwd = os.environ["PW"]
        conn = psycopg2.connect(
            "dbname='{}' user='HSadmin@hs-azure-sql-staff-app' host='hs-azure-sql-staff-app.postgres.database.azure.com' password='{}' port='5432'".format(
                dbname, pwd
            )
        )
        cur = conn.cursor()
        logging.info("DELETE Employee")

        sql_command = "UPDATE employee SET is_active = false WHERE id = %s RETURNING id, full_name, email, title, is_active;"
        cur.execute(sql_command, (id,))
        result = cur.fetchone()
        df = pd.DataFrame(
            [result], columns=["id", "full_name", "email", "title", "is_active"]
        )
        conn.commit()
        return func.HttpResponse(
            df.to_json(orient="records"), mimetype="application/json", status_code=200
        )
    except Exception as e:
        if conn is not None:
            conn.rollback()
        logging.warning(str(e))
        return func.HttpResponse(str(e), status_code=500)
    finally:
        if cur is not None:
            cur.close()
            conn.close()
