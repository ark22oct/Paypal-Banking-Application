from asyncore import file_dispatcher
import pandas as pd
import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
from datetime import datetime
from datetime import date
import mysql.connector
from mysql.connector import errorcode


db = mysql.connector.connect(
    host="72.39.74.52",
    user="pyuser",
    passwd="T3st1nG@714",
    database="Banking",autocommit=False
)
db.autocommit = False

def users():
    curs = db.cursor()
    curs.execute("""Select login.user_id, user_info.first_name, login.user_name, login.password , account_type.account_type
From user_info, login, account_type
WHERE login.user_id = account_type.user_id AND login.user_id = user_info.user_id;""")
    pull = (curs.fetchall())
    userdf = pd.DataFrame(pull, columns = ['UserID', 'Name','Username','Password','Type'])
    print(userdf)
    curs.close()
    return (userdf)

def send_transactions(usname):
    curs = db.cursor()
    vid = usern2id[usname]
    curs.execute(f"""
Select t.transaction_id, t.amount, t.description, t.date
From user_info as ui, transaction_beneficiaries as tb, transaction as t
Where ui.user_id = {vid}
And tb.sender_id = {vid}
And t.transaction_id = tb.transaction_id""")
    pull = (curs.fetchall())
    trandf = pd.DataFrame(pull, columns = ['Transaction ID','Amount','Description','Date'])
    curs.close()
    return (trandf)

def sendbal(sid, rid, amount,desc):
    
        curs = db.cursor()
        now = datetime.now()
        timenow= now.strftime("%H:%M:%S")
        today = date.today()
        d3 = today.strftime("%y-%m-%d")

        curs.execute("INSERT INTO transaction (user_id, amount , description , time , date) VALUES( %s, %s, %s, %s,%s);",(sid,amount,desc,timenow,d3))

        curs.execute(f"""INSERT INTO transaction_beneficiaries(sender_id, receiver_id)
    VALUES({sid}, {rid});""")
    
        curs.execute(f"""Select balance
    From user_balance
    Where user_id = {sid};""")

        spull = (curs.fetchone())
        sbal = spull[0] - amount

        curs.execute(f"""Select balance
    From user_balance
    Where user_id = {rid};""")

        rpull = (curs.fetchone())
        rbal = rpull[0] + amount

        curs.execute(f"""UPDATE user_balance SET balance = {sbal} WHERE (user_id = {sid});""")
    
        curs.execute(f"""UPDATE user_balance SET balance = {rbal} WHERE (user_id = {rid});""")
        curs.close()
        db.commit()
        return(0)

def adduser(newUser ,newPassword ,newfname ,newmname ,newlname,newage,newgender,newemail,newphone,newcountry,newprovince,newcity,newstreet,newstrnum,newpostal,newinitial):
    try:
        curs = db.cursor ()
        curs.execute("INSERT INTO address (country, province, city, street, street_number, postal_code) VALUES (%s, %s, %s, %s, %s, %s);",(newcountry,newprovince,newcity,newstreet,newstrnum,newpostal))
        curs.execute("INSERT INTO user_info(first_name, middle_name, last_name, age,gender, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s);",(newfname ,newmname ,newlname,newage,newgender,newemail,newphone))
        curs.execute("INSERT INTO login (user_name, password) VALUES (%s, %s);",(newUser ,newPassword))
        curs.execute("INSERT INTO account_type (account_type) VALUES ('R');")
        curs.execute(f"""INSERT INTO user_balance (balance) VALUES ({newinitial});""")
        curs.close()
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        return(1)
    return(0)

def deluser(userToDelete):
    
        curs = db.cursor ()
        userlist = users();
        usernames = userlist["Username"].tolist()
        idlist= userlist["UserID"].tolist()
        usern2id = dict(zip(usernames, idlist))
        pid = usern2id[userToDelete]
        curs.execute(f"""DELETE FROM login WHERE (user_id = {pid});""")
        curs.execute(f"""DELETE FROM account_type WHERE (user_id = {pid});""")
        curs.execute(f"""DELETE FROM address WHERE (address_id = {pid});""")
        curs.execute(f"""DELETE FROM user_info WHERE (user_id = {pid});""")
        curs.execute(f"""DELETE FROM user_balance WHERE (user_id = {pid});""")
        curs.close()
        db.commit()

def rec_transactions(usname):
    curs = db.cursor ()
    vid = usern2id[usname]
    curs.execute(f"""
Select t.transaction_id, t.amount, t.description, t.date
From transaction_beneficiaries as tb, transaction as t
where t.transaction_id = tb.transaction_id
And tb.receiver_id = {vid}""")
    pull = (curs.fetchall())
    trandf = pd.DataFrame(pull, columns = ['Transaction ID','Amount','Description','Date'])
    curs.close()
    return (trandf)

def emails():
    curs = db.cursor ()
    curs.execute(f"""select email
from user_info;""")
    pull = (curs.fetchall())
    edf = pd.DataFrame(pull, columns = ['Emails'])
    curs.close()
    return (edf)

def balances(usname):
    curs = db.cursor ()
    vid = usern2id[usname]
    curs.execute(f"""Select balance
From user_balance
Where user_id = {vid};""")
    pull = (curs.fetchone())
    sendback = pull[0]
    curs.close()
    return (sendback)



userlist = users();



#USER AUTHENTICATION
usernames = userlist["Username"].tolist()
names= userlist["Name"].tolist()
idlist= userlist["UserID"].tolist()
passwordlist = userlist["Password"].tolist()
typlist = userlist["Type"].tolist()
imgc1, imgc2 = st.columns(2)
with imgc1:
    st.image('./preview.png', width=150)
usern2type = dict(zip(usernames, typlist))
usern2id = dict(zip(usernames, idlist))

hashed_passwords = stauth.Hasher(passwordlist).generate()

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
'dashboard', 'abc', cookie_expiry_days=30)

names, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status != True:
    st.subheader("Frequently Asked Questions")
    with st.expander("How do I login to my account?"):
        st.write("On the login page, enter your username and password. Then click the “Login” button below to access your account. If you do not have an account, please contact the admin")
    with st.expander("How do I change my password? "):
        st.write("You need to contact an admin, and they will send you a link to change your password. Click on the link, enter your new password, and enter it again to confirm it. ")
    with st.expander("How do I access my account history? "):
        st.write("When you make a transaction, your history will show your most recent transactions. You can also check your recent transactions by clicking on the “My Transactions” tab.")
    with st.expander("How do I send an e transfer?"):
        st.write("To send an e-transfer, on the e-transfer screen you need to enter the email address of the person you would like to send the transaction to. Then hit “Send”, and confirm that you would like to transfer the specified amount of money to the specified email.")

if authentication_status and usern2type[username] == "A":
    # SIDEBAR
    authenticator.logout("Logout Admin", "sidebar")
    st.sidebar.title(f"Welcome {names}")
    heading1, heading2, heading3 = st.columns(3)

    with heading1:
        """
        # Paypal Banking
        Welcome to your banking dashboard.
        """
    
    with heading3:
        bal = balances(username)
        heading3.metric(label ='Current balance',value = f"${bal:,}")
    with st.expander("Transfer Menu"):
        with st.form("send_form"):
            send_email = st.text_input("Email address", placeholder="Enter receipent's email")
            amount = st.number_input('Amount ($CAD) to send')
            descript = st.text_area('Description', placeholder='Enter transaction description.')
            if st.form_submit_button("Send money"):
                emaillist = emails()
                emailing = emaillist["Emails"].tolist()
                email2id = dict(zip(emailing, idlist))
                if (send_email in emailing and balances(username)>amount and usern2id[username] != email2id[send_email]):
                    if(sendbal(usern2id[username],email2id[send_email], amount,descript) == 0):
                        st.success(f"${amount} was successfully transfered!")
                        st.experimental_rerun()
                    else:
                        st.warning("Sorry, Please Check Values")
                else:
                    st.warning("Sorry, Transaction could not be processed")
        


    st.subheader("Sent Transfers")
    df = send_transactions(username)
    st.dataframe(df, use_container_width=True)

    st.subheader("Received Transfers")
    df2 = rec_transactions(username)
    st.dataframe(df2, use_container_width=True)

    with st.expander("Admin Dashboard"):
        st.title("Admin Dashboard")
        st.write("Here you can modify new/existing users of the application.")
    
        h1, h2 = st.tabs(["Create user", "Delete User"])

        with h1:
            with st.form("add_user"):
                st.subheader("Add User")
                newUser = st.text_input("Username", placeholder="Create a username for the new user")
                newPassword = st.text_input("Password", type="password",placeholder="Enter the password for the new user")
                newfname = st.text_input("First Name")
                newmname = st.text_input("Middle Name")
                newlname= st.text_input("Last Name")
                newage= st.text_input("Age")
                newgender= st.text_input("Gender")
                newemail= st.text_input("Email")
                newphone= st.text_input("Phone Number")
                
                newcountry= st.text_input("Country")
                newprovince= st.text_input("Province")
                newcity= st.text_input("City")
                newstreet= st.text_input("Street")
                newstrnum= st.text_input("Street Number")
                newpostal= st.text_input("Postal Code")

                newinitial = st.number_input("Initial Balance")

                if st.form_submit_button("Add user") and newUser != "":
                    if(adduser(newUser ,newPassword ,newfname ,newmname ,newlname,newage,newgender,newemail,newphone,newcountry,newprovince,newcity,newstreet,newstrnum,newpostal,newinitial)==0):
                        st.success(f"User: '{newUser}' was successfully created!")
                    else:
                        st.warning("Improper input data")
                else:
                    st.warning("User was not created")
        with h2:
            with st.form("delete_user"):
                st.subheader("Delete User")
                userToDelete = st.text_input("Username", placeholder="Input the username to delete")
                if st.form_submit_button("Delete user") and userToDelete != "":
                    if(deluser(userToDelete) == 0):
                        st.success(f"User: '{userToDelete}' was successfully deleted!")
                    else:
                        st.warning("User not Deleted")

    


elif authentication_status:

    # SIDEBAR
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {names}")

    heading1, heading2, heading3 = st.columns(3)

    with heading1:
        """
        # Paypal Banking
        Welcome to your banking dashboard.
        """
    
    with heading3:
        bal = balances(username)
        heading3.metric(label ='Current balance',value = f"${bal:,}")
    with st.expander("Transfer Menu"):
        with st.form("send_form"):
            send_email = st.text_input("Email address", placeholder="Enter receipent's email")
            amount = st.number_input('Amount ($CAD) to send')
            descript = st.text_area('Description', placeholder='Enter transaction description.')
            if st.form_submit_button("Send money"):
                emaillist = emails()
                emailing = emaillist["Emails"].tolist()
                email2id = dict(zip(emailing, idlist))
                if (send_email in emailing and balances(username)>amount and usern2id[username] != email2id[send_email]):
                    if(sendbal(usern2id[username],email2id[send_email], amount,descript) == 0):
                        st.success(f"${amount} was successfully transfered!")
                        st.experimental_rerun()
                    else:
                        st.warning("Sorry, Please Check Values")
                else:
                    st.warning("Sorry, Transaction could not be processed")

            


            
        


    st.subheader("Sent Transfers")
    df = send_transactions(username)
    st.dataframe(df.round(2), use_container_width=True)

    st.subheader("Received Transfers")
    df2 = rec_transactions(username)
    st.dataframe(df2.round(2), use_container_width=True)
    
