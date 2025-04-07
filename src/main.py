import psycopg2
import os
from cuid2 import Cuid

def fetchCurrentSprints(cursor):
    sql = '''SELECT "currentSprintId" FROM "Team" WHERE "currentSprintId" IS NOT NULL'''
    cursor.execute(sql)
    return cursor.fetchall()

def fetchSprintTickets(cursor, sprint_id):
    sql = '''SELECT "status", count(*) FROM "Ticket" WHERE "sprintId"=%s GROUP BY "status"'''
    cursor.execute(sql, sprint_id)
    return cursor.fetchall()

def insertSprintDailyProgress(cursor, progress):
    sql = '''INSERT INTO "SprintDailyProgress"("id", "sprintId", "completed", "blocked", "remaining") VALUES(%s, %s, %s, %s, %s)'''
    cursor.execute(sql, progress)

def main(request, context):
    # using sqlite we connect to our database, grab all teams from the "teams" table
    try:
        CUID_GENERATOR: Cuid = Cuid(length=25)
        # connect to the database using environment variables
        user=os.getenv('DB_USER', default="postgres")
        password=os.getenv('DB_PASSWORD')
        host=os.getenv('DB_HOST', default="localhost")
        port=os.getenv('DB_PORT', default="5432")
        db_name=os.getenv('DB_NAME')

        # check if all environment variables are set
        if not all([user, password, host, port, db_name]):
            raise ValueError("Missing one or more database connection parameters.")

        conn_string = f"postgres://{user}:{password}@{host}:{port}/{db_name}"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        sprint_ids = fetchCurrentSprints(cursor)

        for sprint_id in sprint_ids:
            open_count = 0
            blocked_count = 0
            closed_count = 0
            try:
                status_counts = fetchSprintTickets(cursor, sprint_id)
                # grab all tickets in the sprint and insert a row based on status
                for status in status_counts:
                    status_title, count = status
                    if status_title in ["OPEN", "IN PROGRESS"]:
                        open_count += count
                    elif status_title == "BLOCKED":
                        blocked_count += count
                    elif status_title == "CLOSED":
                        closed_count += count
            except Exception as err:
                print(err)
            progress = (CUID_GENERATOR.generate(), sprint_id[0], closed_count, blocked_count, open_count)
            insertSprintDailyProgress(cursor, progress)
            conn.commit()
    except Exception as err:
        print(err)
    finally:
        conn.close()
