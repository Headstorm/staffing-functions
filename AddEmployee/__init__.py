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
        conn = psycopg2.connect(
            "dbname='{}' user='HSadmin@hs-azure-sql-staff-app' host='hs-azure-sql-staff-app.postgres.database.azure.com' password='{}' port='5432'".format(
                dbname, pwd
            )
        )
        cur = conn.cursor()
        print("POST Employee")

        message = req.get_body()
        json_body = json.loads(message)
        logging.info(json_body)

        sql_command = "INSERT INTO employee (full_name, email, title) VALUES (%s,%s,%s) RETURNING id, full_name, email, title, is_active;"

        cur.execute(
            sql_command,
            (json_body["full_name"], json_body["email"], json_body["title"]),
        )
        result = cur.fetchone()
        # logging.info(result)
        df = pd.DataFrame([result], columns=["id", "full_name", "email", "title", "is_active"])
        conn.commit()
        cur.close()
        conn.close()

        return func.HttpResponse(df.to_json(orient="records"), mimetype="application/json", status_code=200)

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        logging.warning(str(e))
        return func.HttpResponse(json.dumps(e, default=str), status_code=500)
