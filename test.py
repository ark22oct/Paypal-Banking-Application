import mysql.connector
import pandas as pd
def users():
    curs.execute("""Select login.user_id, user_info.first_name, login.user_name, login.password , account_type.account_type
From user_info, login, account_type
WHERE login.user_id = account_type.user_id AND login.user_id = user_info.user_id;""")
    pull = (curs.fetchall())
    userdf = pd.DataFrame(pull, columns = ['UserID', 'Name','Username','Password','Type'])
    
    return (userdf)

def transactions():
    vid = 20
    curs.execute(f"""
Select t.transaction_id, t.status, t.amount, t.description, t.date
From user_info as ui, transaction_beneficiaries as tb, transaction as t
Where ui.user_id = {vid}
And (tb.sender_id = {vid} or tb.receiver_id = {vid})
And t.transaction_id = tb.transaction_id""")
    pull = (curs.fetchall())
    trandf = pd.DataFrame(pull, columns = ['Transaction ID', 'Send / Received','Amount','Description','Date'])
    
    return (trandf)

db = mysql.connector.connect(
    host="72.39.74.52",
    user="pyuser",
    passwd="T3st1nG@714",
    database="Banking",autocommit=True
)

curs = db.cursor(buffered=True)
sid = 1
amount = 120
desc = "crate of prime"
timenow = "03:12:41"
d3 = "2021-11-11"
newinitial = 150
curs.execute(f"""INSERT INTO user_balance (balance) VALUES ({newinitial});""")

curs.close()



