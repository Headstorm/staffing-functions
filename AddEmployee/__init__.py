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
        con_string = os.environ["dbManagementConnectionString"]
        conn = psycopg2.connect(
            con_string
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
        return func.HttpResponse(df.to_json(orient="records"), mimetype="application/json", status_code=200)

    except Exception as e:
        if conn is not None:
            conn.rollback()
        logging.warning(str(e))
        return func.HttpResponse(str(e), status_code=500)
    finally:
        if cur is not None:
            cur.close()
            conn.close()
