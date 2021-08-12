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
        id = req.route_params.get('id')
        # logging.info("id : {}".format(id))
        con_string = os.environ["dbManagementConnectionString"]
        conn = psycopg2.connect(
            con_string
        )
        cur = conn.cursor()
        logging.info("GET Employee")

        sql_command = "SELECT * FROM employee WHERE id = %s"

        cur.execute(sql_command, (id, ))
        result = cur.fetchall()
        df = pd.DataFrame(result, columns=["id", "full_name", "email", "title", "is_active"])
        return func.HttpResponse(df.to_json(orient="records"), mimetype="application/json", status_code=200)
    except Exception as e:
        logging.warning(str(e))
        return func.HttpResponse(str(e), status_code=500)
    finally:
        if cur is not None:
            cur.close()
            conn.close()
