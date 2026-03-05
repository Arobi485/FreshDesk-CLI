# pyright: reportPrivateImportUsage=false

from GetAllTickets import GetAllTickets
from GetSingleTicket import GetSingleTicket
from GetTicketTimes import GetTicketTimes
from SendOutEmail import SendOutEmail

import time
import sys
import csv
import os
import json
from dotenv import set_key, find_dotenv, load_dotenv

from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy import prompt

#Read all tickets in the inbox (ONLY GETS THE SUBJECT)
def readAllTickets():
    gat = GetAllTickets()
    
    #set to false as not getting install times
    tickets = gat.getOpenTickets(False)

    #if no tickets do nothing
    if not tickets:
        print ("No tickets currently in the inbox")
        time.sleep(1)
        return

    #for each ticket extract information
    for ticket in tickets:
        email = (ticket.get("requester", {}).get("email"))
        print (f"ID: {ticket.get("id")}, Sender: {email}, Created At: {ticket.get("created_at")}, Last Updated: {ticket.get("updated_at")}, Subject: {ticket.get("subject")}")

    #print how many tickets there are in total
    print (f"\nTotal Tickets: {len(tickets)}\n")

    time.sleep(3)

    return

#Read only the details of the ticket provided (ALSO GETS FULL CONVO)
def readSpecificTicket():
    gst = GetSingleTicket()

    #setup pyinq question for ticket ID to search
    questions = [
        {
            "type": "input",
            "name": "ticketID",
            "message": "Please enter the ID of the ticket to search:",
            "default": "",
        }
    ]

    #get pyinq response
    response = prompt(questions)

    #try to get the ticket, if you can't do nothing
    try:
        ticket = gst.getTicket(str(response["ticketID"]).strip())
    except:
        print("\nNo ticket with this ID exists")
        time.sleep(1)
        return

    #extract data from the ticket and get the conversation
    email = (ticket.get("requester", {}).get("email"))
    print (f"ID: {ticket.get("id")}, Sender: {email}, Created At: {ticket.get("created_at")}, Last Updated: {ticket.get("updated_at")}, Subject: {ticket.get("subject")},")
    print (f"Content:\n\n {ticket.get('description_text', '').strip()}")
    
    #Conversation logic
    convs = ticket.get("conversations") or []
    print("\n--- Conversation Thread ---")
    #if no convo do nothing
    if not convs:
        print("No conversations found.")
    #otherwise go through the conversation, format it to be readable and print out
    else:
        for i, c in enumerate(convs, start=1):
            who = "Incoming (customer)" if c.get("incoming") else "Outgoing (agent)"
            body = c.get("body_text") or c.get("body") or ""
            body = " ".join(body.split())
            MAX = 1000
            if len(body) > MAX:
                body = body[:MAX] + "…"

            print(f"\n[{i}] {who}")
            print(body)

    time.sleep(3)
    print("\n")

#Get the most recently responded to ticket
def readMostRecentTicket():
    #This function is the same as the above one but instead of asking for a ticketID it just gets the most recent one
    #getOpenTickets() sorts by most recent so can just get item[0] in the list
    gat = GetAllTickets()
    gst = GetSingleTicket()
    
    tickets = gat.getOpenTickets(False)

    if not tickets:
        print ("No tickets currently in the inbox\n")
        time.sleep(1)
        return
    
    ticketID = tickets[0].get("id")

    ticket = gst.getTicket(ticketID)

    email = (ticket.get("requester", {}).get("email"))
    print (f"ID: {ticket.get("id")}, Sender: {email}, Created At: {ticket.get("created_at")}, Last Updated: {ticket.get("updated_at")}, Subject: {ticket.get("subject")},")
    print (f"Content:\n\n {ticket.get('description_text', '').strip()}")

    convs = ticket.get("conversations") or []
    print("\n--- Conversation Thread ---")
    if not convs:
        print("No conversations found.")
    else:
        for i, c in enumerate(convs, start=1):
            who = "Incoming (customer)" if c.get("incoming") else "Outgoing (agent)"
            body = c.get("body_text") or c.get("body") or ""
            body = " ".join(body.split())
            MAX = 1000
            if len(body) > MAX:
                body = body[:MAX] + "…"

            print(f"\n[{i}] {who}")
            print(body)

    print("\n")

    time.sleep(3)

#Get the installation times and how many to get
def getInstalls(amount):
    gat = GetAllTickets()
    gtt = GetTicketTimes()

    tickets = []

    tickets = gat.getOpenTickets(True)

    if not tickets:
        print ("No tickets currently in the inbox\n")
        time.sleep(1)
        return
    
    installTickets = []

    for i in range(amount):
        installTickets.append(gtt.getTime(tickets[i].get("id")))

    for ticket in installTickets:
        print (f"ID: {ticket.get("id")}")

#Send single email to client     
def sendSingleEmail(pointer, emailConfigID):
    se = SendOutEmail()

    #loads up the html file that we will use to edit
    with open("MailingLists/EmailTemplate.html", encoding="utf-8") as f:
        html = f.read()

    #gathers data for the email
    questions = [
        {
            "type": "input",
            "name": "destination",
            "message": "Enter destination email:",
            "default": "",
        },
        {
            "type": "input",
            "name": "ccEmails",
            "message": "Enter CC emails:",
            "multiline": True, #mult line allows you to add multiple emails
            "default": "",
        },
        {
            "type": "input",
            "name": "subject",
            "message": "Enter the email subject:",
            "default": "VARS Technical Support - ", #pre filled
        },
        {
            "type": "input",
            "name": "greeting",
            "message": "Enter the email greeting:",
            "default": "Hi Site,", #pre filled
        },
        {
            "type": "input",
            "name": "body",
            "message": "Enter the email body (will open your editor):",
            "multiline": True, #mult line allows you to press enter like you would in an email to seperate points
            "default": "",
        },
        {
            "type": "input",
            "name": "signoff",
            "message": "Enter the email signoff:",
            "default": "Yours Sincerely,", #pre filled 
        },
        {
            "type": "input",
            "name": "name",
            "message": "Enter the sender's name:",
            "default": "",
        },
    ]

    #get pyinq response
    answers = prompt(questions)

    #split the main body as in mult line it uses \n, html needs <br/>
    answers["body"] = str(answers["body"]).replace("\n","<br/>")

    html = html.replace("{greeting}", str(answers["greeting"]).strip())
    html = html.replace("{mainBody}", str(answers["body"]).strip())
    html = html.replace("{signoff}", str(answers["signoff"]).strip())
    html = html.replace("{name}", str(answers["name"]).strip())

    #same as main body but split into "," so the .split function can be called to turn it into a list
    ccEmails = str(answers["ccEmails"]).replace("\n",",")

    ccEmailsList = []

    #listifying the ccEmails
    if ccEmails:
        ccEmailsTemp = ccEmails.split(",")
        for email in ccEmailsTemp:
            if not email == "":
                ccEmailsList.append(email)
    else:
        ccEmailsList = None

    #make the user confirm that they want to send an email to the destination
    print(f"\nConfirm? Send email to {str(answers["destination"]).strip()}")

    choice = inquirer.select(
            message="Send email?:",
            choices=[
                "Yes",
                "No"
            ],
            pointer=pointer,
            qmark="",
            instruction="Use ↑↓ arrow keys to move and ⏎ to select choice",
            cycle=True,
        ).execute()

    #send the email
    if choice == "Yes":
        se.sendEmail(
            to_email=str(answers["destination"]).strip(),
            subject=str(answers["subject"]).strip(),
            body_html=html,
            email_config_id=emailConfigID,
            cc_emails=ccEmailsList,
            bcc_emails=None,
            status=5, #(closed)
            priority=1, #default
            tags=["FreshdeskCLI"], #tag so that it can be identified in freshdesk
        )

        print(f"\nEmail sent succesfully to: {str(answers["destination"]).strip()}\n")
    else:
        print(f"\nEmail send cancelled, returning to menu\n")

    time.sleep(1)

#Gets a list of the mailing lists and allows you to look inside them 2
def getMailingList(pointer):
    #get the list from the files
    mailing_lists = [
        f for f in os.listdir("MailingLists")
        if f.lower().endswith(".csv")
    ]
    
    #setup pyinq choices
    choices = [
        "0) Go back a menu",
        Separator(),
    ]

    # add each mailing list file as a selectable option to choices
    for idx, filename in enumerate(mailing_lists, start=1):
        choices.append(f"{idx}) {filename}")

    choices.append(Separator())

    #loop to select mailing list
    while True:
        choice = inquirer.select(
            message="Mailing List Menu:",
            choices=choices,
            pointer=pointer,
            qmark="",
            instruction="Use ↑↓ arrow keys to move and ⏎ to select choice"
        ).execute()

        print("\n")

        #if the choice is 0 then go back
        match choice[0]:
            case "0":
                time.sleep(1)
                return

        #if choice not 0 work out what they chose and then open that mailing list
        path = "MailingLists/" + choice.split(") ", 1)[1]

        print(f"Reading: {path}\n")
        time.sleep(1)

        #csv reader time... yay
        with open(path, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                #print out in a basic format as i dislike csvs
                print(row)
                time.sleep(0.02)

        print("\n")

#Creates a new BCC mailing list
def createMailingList():
    #setup for pyinq
    questions = [
        {
            "type": "input",
            "name": "destination",
            "message": "Enter mailing list name:",
            "default": "",
        },
        {
            "type": "input",
            "name": "emails",
            "message": "Enter destination emails:",
            "multiline": True,   
            "default": "",
        },
    ]

    #get pyinq response
    answers = prompt(questions)

    #name of the csv file
    listName = str(answers["destination"])

    #get a list of the lists in the current mailing lists directory
    listList = os.listdir("MailingLists")

    #if the list was already created then error out
    for item in listList:
        if item[:-3] == listName:
            print("\nMailing list with this name already exists\n")
            return

    #else: do this
    filename = "MailingLists/" + listName + ".csv"
    
    #split the emails into a list
    emails = str(answers["emails"]).split("\n")

    #write to the csv verified from before
    with open (filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows([[e] for e in emails])

    print(f"\nSuccesfull saved to {filename}\n")

#Send an email to a mailing list
def sendToMailingList(pointer, emailConfigID, bccEmail):
    se = SendOutEmail()

    #get the mailing lists
    mailing_lists = [
        f for f in os.listdir("MailingLists")
        if f.lower().endswith(".csv")
    ]
    
    #add to choices
    choices = [
        "0) Go back a menu",
        Separator(),
    ]

    # add each mailing list file as a selectable option
    for idx, filename in enumerate(mailing_lists, start=1):
        choices.append(f"{idx}) {filename}")

    choices.append(Separator())

    #present mailing list
    choice = inquirer.select(
        message="Mailing List Menu:",
        choices=choices,
        pointer=pointer,
        qmark="",
        instruction="Use ↑↓ arrow keys to move and ⏎ to select choice"
    ).execute()

    print("\n")

    #return if 0
    match choice[0]:
        case "0":
            time.sleep(1)
            return

    #otherwise user selects the mailing list
    path = "MailingLists/" + choice.split(") ", 1)[1]
    
    emailList = []

    #opens the mailing list and gets the BCC list
    with open(path, "r", newline='') as f:
        reader = csv.reader(f)
        emailList = list(reader)

    singleEmailList: list[str] = []

    #strip of anything but email
    for item in emailList:
        singleEmailList.append(item[0].strip())

    #same as send single email
    with open("MailingLists/EmailTemplate.html", encoding="utf-8") as f:
        html = f.read()

    questions = [
        {
            "type": "input",
            "name": "subject",
            "message": "Enter the email subject:",
            "default": "VARS Technical Support - ",
        },
        {
            "type": "input",
            "name": "greeting",
            "message": "Enter the email greeting:",
            "default": "",
        },
        {
            "type": "input",
            "name": "body",
            "message": "Enter the email body (will open your editor):",
            "multiline": True,   
            "default": "",
        },
        {
            "type": "input",
            "name": "signoff",
            "message": "Enter the email signoff:",
            "default": "",
        },
        {
            "type": "input",
            "name": "name",
            "message": "Enter the sender's name:",
            "default": "",
        },
    ]

    answers = prompt(questions)

    answers["body"] = str(answers["body"]).replace("\n","<br/>")

    # Safely coerce to string for strip (silences Pylance & avoids None issues)
    html = html.replace("{greeting}", str(answers["greeting"]).strip())
    html = html.replace("{mainBody}", str(answers["body"]).strip())
    html = html.replace("{signoff}", str(answers["signoff"]).strip())
    html = html.replace("{name}", str(answers["name"]).strip())

    print(f"\nConfirm? Send email to {len(singleEmailList)} clients?")

    choice = inquirer.select(
            message="Send emails?:",
            choices=[
                "Yes",
                "No"
            ],
            pointer=pointer,
            qmark="",
            instruction="Use ↑↓ arrow keys to move and ⏎ to select choice",
            cycle=True,
        ).execute()

    if choice == "Yes":
        result = se.sendEmail(
            to_email=bccEmail,
            subject=(str(answers["subject"]).strip() + " - NO REPLY") , # added - NO REPLY onto the end as you can't reply to Freshdesk BCC emails
            body_html=html,
            email_config_id=emailConfigID,
            cc_emails=None,
            bcc_emails=singleEmailList, # this is where the BCC emails are added
            status=5,
            priority=1,
            tags=["FreshdeskCLI"],
        )

        print(f"\nSent email to {len(singleEmailList)} clients\n")

    else:
        print(f"\nEmail send cancelled, returning to menu\n")

    time.sleep(1)

#Install time loop 2
def getInstallationTimes(pointer):
    #setup pyinq questions
    while True:
        choice = inquirer.select(
            message="Installs Menu:",
            choices=[
                "0) Go back a menu",
                Separator(),
                "1) Get most recent install",
                "2) Get past 10 installs",
                "3) Get all possible installs",
                Separator(),
            ],
            pointer=pointer,
            qmark="",
            instruction="Use ↑↓ arrow keys to move and ⏎ to select choice"
        ).execute()#get response

        print("\n")

        #depending on what the user chooses get that many installs, 0 is all
        match choice[0]:
            case "0":
                time.sleep(1)
                return
            case "1":
                getInstalls(1)
            case "2":
                getInstalls(10)
            case "3":
                getInstalls(0)

#Set the new pointer
def setPointer():
    #setup pyinq
    questions = [
        {
            "type": "input",
            "name": "newPointer",
            "message": "Please enter the new pointer:",
            "default": "",
        }
    ]

    #get response, open json, set point, save json

    response = prompt(questions)

    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    settings["pointer"] = str(response["newPointer"])

    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

    print("New pointer set, will take effect at next restart\n")

#Toggle startup animation
def toggleStartup():

    #open json, toggle the startup, save json

    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    settings["startup"] = not settings["startup"]

    temp = settings["startup"]

    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

    print(f"Startup animation toggle changed to {temp}\n")

#Change the environment variables so that you can actually use the system
def changeEnv():
    load_dotenv()

    #get the .env api key and domain
    api_key = os.getenv("FRESHDESK_API_KEY")
    domain = os.getenv("FRESHDESK_DOMAIN")

    #setup pyinq with the defaults as what it currently is set to
    questions = [
        {
            "type": "input",
            "name": "newAPIKey",
            "message": "Please enter the new FRESHDESK_API_KEY:",
            "default": api_key,
        },
        {
            "type": "input",
            "name": "newDomain",
            "message": "Please enter the new FRESHDESK_DOMAIN:",
            "default": domain,
        }
    ]

    response = prompt(questions)

    env_path = find_dotenv(usecwd=True)
    if not env_path:
        env_path = ".env"
        open(env_path, "a").close()

    #set the gathered keys
    set_key(env_path, "FRESHDESK_API_KEY", str(response["newAPIKey"]).strip())
    set_key(env_path, "FRESHDESK_DOMAIN", str(response["newDomain"]).strip())

    print("\nEnvironment variables updated, no restart required\n")

#Change the email config ID
def changeEmailConfigID():
    questions = [
        {
            "type": "input",
            "name": "newEmailID",
            "message": "Please enter the new email ID (Or type 0 to automatically find the email config, will only work if .env api+domain set):",
            "default": "",
        }
    ]

    response = prompt(questions)

    #if the user sets a manual email id then just save that
    if str(response["newEmailID"]) != "0":
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)

        settings["emailConfigID"] = str(response["newEmailID"])

        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    #if they choose 0, then get the email id from the api data from a ticket
    else:
        gat = GetAllTickets()

        tickets = gat.getOpenTickets(False)

        if tickets:
            emailConfigID = tickets[0].get("emailConfigID")

            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)

            settings["emailConfigID"] = emailConfigID

            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
        else:
            print("\nNo tickets currently in your inbox, please send one and retry\n")
            return

    print("New email ID set, will take effect at next restart\n")

#Change the target BCC email
def changeBccEmail():
    #setup pyinq
    questions = [
        {
            "type": "input",
            "name": "newBccEmail",
            "message": "Please enter the new email ID:",
            "default": "",
        }
    ]

    response = prompt(questions)

    # set the mailing list BCC email

    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    settings["bccEmail"] = str(response["newBccEmail"])

    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

    print("New BCC email set, will take effect at next restart\n")

#Ticket menu loop 1
def ticketMenu(pointer):
    while True:
        choice = inquirer.select(
            message="Ticket Menu:",
            choices=[
                "0) Go back a menu",
                Separator(),
                "1) Read all tickets",
                "2) Read ticket by ID number",
                "3) Read the most recent ticket",
                "4) Get installation times",
                Separator(),
            ],
            pointer=pointer,
            qmark="",
            instruction="Use ↑↓ arrow keys to move and ⏎ to select choice"
        ).execute()

        print("\n")

        match choice[0]:
            case "0":
                time.sleep(1)
                return
            case "1":
                readAllTickets()
            case "2":
                readSpecificTicket()
            case "3":
                readMostRecentTicket()
            case "4":
                getInstallationTimes(pointer)

#Email menu loop 1
def emailMenu(pointer, emailConfigID, bccEmail):
    while True:
        choice = inquirer.select(
            message="Email Menu:",
            choices=[
                "0) Go back a menu",
                Separator(),
                "1) Send single email",
                "2) Access mailing list",
                "3) Create mailing list",
                "4) Send email to mailing list",
                Separator(),
            ],
            pointer=pointer,
            qmark="",
            instruction="Use ↑↓ arrow keys to move and ⏎ to select choice"
        ).execute()

        print("\n")

        match choice[0]:
            case "0":
                time.sleep(1)
                return
            case "1":
                time.sleep(1)
                sendSingleEmail(pointer, emailConfigID)
            case "2":
                time.sleep(1)
                getMailingList(pointer)
            case "3":
                time.sleep(1)
                createMailingList()
            case "4":
                time.sleep(1)
                sendToMailingList(pointer, emailConfigID, bccEmail)

#Settings menu loop 1
def settingsMenu(pointer):
    while True:
        choice = inquirer.select(
            message="Settings Menu:",
            choices=[
                "0) Go back a menu",
                Separator(),
                "1) Change menu pointer",
                "2) Startup animation toggle",
                "3) .env file editting",
                "4) Change email config ID",
                "5) Change inbox to send mailing list BCC to",
                Separator(),
            ],
            pointer=pointer,
            qmark="",
            instruction="Use ↑↓ arrow keys to move and ⏎ to select choice"
        ).execute()

        print("\n")

        match choice[0]:
            case "0":
                time.sleep(1)
                return
            case "1":
                time.sleep(1)
                setPointer()
            case "2":
                time.sleep(1)
                toggleStartup()
            case "3":
                time.sleep(1)
                changeEnv()
            case "4":
                time.sleep(1)
                changeEmailConfigID()
            case "5":
                time.sleep(1)
                changeBccEmail()

#Main Entry 0
def main():
    #epic banner
    BANNER = """
    ███████╗██████╗ ███████╗███████╗██╗  ██╗██████╗ ███████╗███████╗██╗  ██╗
    ██╔════╝██╔══██╗██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝██╔════╝██║ ██╔╝
    █████╗  ██████╔╝█████╗  ███████╗███████║██║  ██║█████╗  ███████╗█████╔╝ 
    ██╔══╝  ██╔══██╗██╔══╝  ╚════██║██╔══██║██║  ██║██╔══╝  ╚════██║██╔═██╗ 
    ██║     ██║  ██║███████╗███████║██║  ██║██████╔╝███████╗███████║██║  ██╗
    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

         ██████╗██╗     ██╗     By Adam Robinson
        ██╔════╝██║     ██║     
        ██║     ██║     ██║
        ██║     ██║     ██║
        ╚██████╗███████╗██║
         ╚═════╝╚══════╝╚═╝
    """

    #CHECK FOR NO SETTINGS FILE
    if not os.path.exists("settings.json"):
        json.dump({"pointer": " ➤ ", "startup": True, "emailConfigID":"", "bccEmail":""},
                open("settings.json", "w"),
                indent=4)

    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    #open the settings.json and get the settings for the app
    pointer = (settings["pointer"])
    startupEnabled = (settings["startup"])
    emailConfigID = (settings["emailConfigID"])
    bccEmail = (settings["bccEmail"])

    #Entry
    os.system('cls' if os.name == 'nt' else 'clear')

    #if the banner scroll animation is activated scroll it across the screen
    #this uses the cursor, writes the banner in current position, then flushes and does it again slightly to the left
    if startupEnabled:
        lines = BANNER.split("\n")
        width = 60
        max_len = max(len(l) for l in lines)

        for offset in range(max_len + width):
            # move cursor to top-left
            sys.stdout.write("\x1b[H")

            for line in lines:
                # clear entire current line
                sys.stdout.write("\x1b[2K")

                x = width - offset
                sys.stdout.write((" " * max(0, x)) + line + "\n")

            sys.stdout.flush()
            time.sleep(0.02)

    #if startup is false just print the banner
    else:
        print(BANNER)
        time.sleep(3)

    #checks so that if the emailconfigs and bccemail aren't set
    if(emailConfigID == ""):
        print("EMAIL CONFIG NOT SET, PLEASE NAVIGATE TO SETTINGS TO SET THIS\n")

    if(bccEmail == ""):
        print("BCC EMAIL FOR SENDING TO MAILING LIST NOT SET, PLEASE NAVIGATE TO SETTINGS TO SET THIS\n")

    #Main Menu Loop
    while True:
        choice = inquirer.select(
            message="Main Menu:",
            choices=[
                "0) Quit",
                Separator(),
                "1) Ticket reading",
                "2) Email sending",
                "3) Contact management",
                Separator(),
                "4) Settings",
            ],
            pointer=pointer,
            qmark="",
            instruction="Use ↑↓ arrow keys to move and ⏎ to select choice",
            cycle=True,
        ).execute()

        print("\n")

        match choice[0]:
            case "0":
                time.sleep(1)
                exit()
            case "1":
                time.sleep(1)
                ticketMenu(pointer)
            case "2":
                time.sleep(1)
                emailMenu(pointer, emailConfigID, bccEmail) # pass in the email config details
            case "3":
                print("Not yet implemented\n")
                time.sleep(1)
            case "4":            
                time.sleep(1)
                settingsMenu(pointer)

if __name__ == "__main__":
    main()