from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QMessageBox # respond imports
import sys
import re
from html import unescape

from MainWindow import Ui_HelloWorldUI

from GetAllTickets import GetAllTickets
from GetSingleTicket import GetSingleTicket
from GetTicketTimes import GetTicketTimes
from SendOutEmail import SendOutEmail
from SendReply import SendReply

class ReplyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reply to Ticket")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        

        self.send_button = QPushButton("Send")
        self.cancel_btn = QPushButton("Cancel")
        self.send_button.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.send_button)
        layout.addWidget(self.cancel_btn)

        self.setLayout(layout)

    def get_text(self):
        return self.text_edit.toPlainText()

class MainWindow(QtWidgets.QMainWindow, Ui_HelloWorldUI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Create a model
        self.model = QtCore.QStringListModel()

        # Setup ticket list on startup
        self.updateTicketList()

        # Disable buttons until pressed
        self.pushButton_RespondTicket.setEnabled(False)

        self.pushButton_ReadTicket.setEnabled(False)

        self.pushButton_CloseTicket.setEnabled(False)

        # Connecting buttons
        self.pushButton_UpdateTickets.clicked.connect(self.updateTicketList)

        self.pushButton_ReadTicket.clicked.connect(self.readSelectedTicket)

        self.pushButton_RespondTicket.clicked.connect(self.sendResponse)

        # Connecting listview
        self.listView_TicketList.selectionModel().selectionChanged.connect(self.onSelectionChanged)

    def updateTicketList(self):
        # disable buttons again
        self.pushButton_RespondTicket.setEnabled(False)
        self.pushButton_ReadTicket.setEnabled(False)

        self.model.setStringList(self.getTicketList())

        self.listView_TicketList.setModel(self.model)

    def getTicketList(self):
        gat = GetAllTickets()
        ticketItems = []
    
        #set to false as not getting install times
        if self.comboBox_TicketState.currentText() == "Open":
            openClosed = False
        else:
            openClosed = True

        tickets = gat.getOpenTickets(openClosed)

        #if no tickets do nothing
        if not tickets:
            ticketItems.append("No tickets currently in the inbox")
        else:
        #for each ticket extract information
            for ticket in tickets:
                email = (ticket.get("requester", {}).get("email"))
                ticketItems.append(f"ID: {ticket.get("id")}, Sender: {email}, Subject: {ticket.get("subject")}")

        return ticketItems

    def readSelectedTicket(self):
        self.model.setStringList(self.getSingleTicket())

        self.listView_TicketList.setModel(self.model)

    def getSingleTicket(self):
        gst = GetSingleTicket()

        selectedTicket = (self.listView_TicketList.currentIndex()).data()

        if selectedTicket is None or not selectedTicket[:2] == "ID":
            outputList = ["No ticket selected to be read, please try again"]
            return(outputList)
        else:
            ticketID = selectedTicket.split(",")[0].split(":")[1].strip()
            ticket = gst.getTicket(ticketID)
            outputList = [selectedTicket]
            outputList.append(ticket.get('description_text', '').strip())
            
            # Conversation logic
            convs = ticket.get("conversations") or []

            outputList.append("--- Conversation Thread ---")

            # if no convo do nothing
            if not convs:
                outputList.append("No conversations found.")
            else:
                for i, c in enumerate(convs, start=1):
                    who = "Incoming (customer)" if c.get("incoming") else "Outgoing (agent)"
                    body = self.clean_freshdesk_body(c)

                    MAX = 1000
                    if len(body) > MAX:
                        body = body[:MAX] + "…"

                    outputList.append(f"[{i}] {who}\n{body}")

            return(outputList)
    
    def clean_freshdesk_body(self, conversation):
        body = conversation.get("body") or conversation.get("body_text") or ""
        if not body:
            return ""

        # Remove Freshdesk quoted reply block completely
        body = re.sub(
            r'<div class="freshdesk_quote".*?</div>\s*</blockquote>\s*</div>',
            '',
            body,
            flags=re.IGNORECASE | re.DOTALL
        )

        # Remove blockquotes if any remain
        body = re.sub(
            r'<blockquote.*?>.*?</blockquote>',
            '',
            body,
            flags=re.IGNORECASE | re.DOTALL
        )

        # Convert common HTML line break tags to real newlines
        body = re.sub(r'(?i)<br\s*/?>', '\n', body)
        body = re.sub(r'(?i)</p>', '\n', body)
        body = re.sub(r'(?i)</div>', '\n', body)
        body = re.sub(r'(?i)</li>', '\n', body)

        # Remove all remaining HTML tags
        body = re.sub(r'<[^>]+>', '', body)

        # Decode HTML entities
        body = unescape(body)

        # Remove invisible characters
        body = body.replace('\u200b', '').replace('\ufeff', '').replace('\xa0', ' ')

        # Clean up lines while keeping real line breaks
        lines = [line.strip() for line in body.splitlines()]
        lines = [line for line in lines if line]

        return '\n'.join(lines).strip()

    def sendResponse(self):
        sr = SendReply()
        dialog = ReplyDialog()

        if dialog.exec():
            message = dialog.get_text().strip()
            if not message:
                QMessageBox.warning(self, "Empty", "Message cannot be empty")
                return
            if message:
                selectedTicket = (self.listView_TicketList.currentIndex()).data()

                if selectedTicket is None or not selectedTicket[:2] == "ID":
                    outputList = ["No ticket selected to be read, please try again"]
                    return(outputList)
                else:
                    ticketID = selectedTicket.split(",")[0].split(":")[1].strip()
                    result = sr.reply_to_ticket(ticketID, message)

                    if result:
                        QMessageBox.information(self, "Success", "Reply sent!")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to send reply")

    def onSelectionChanged(self):
        indexes = self.listView_TicketList.selectedIndexes()

        if not indexes:
            self.pushButton_RespondTicket.setEnabled(False)
            return

        # Get selected item's text
        selected_text = indexes[0].data()

        # Enable only if it starts with "ID"
        if selected_text.startswith("ID"):
            self.pushButton_RespondTicket.setEnabled(True)
            self.pushButton_ReadTicket.setEnabled(True)
            self.pushButton_CloseTicket.setEnabled(True)
        else:
            self.pushButton_RespondTicket.setEnabled(False)
            self.pushButton_ReadTicket.setEnabled(False)
            self.pushButton_CloseTicket.setEnabled(False)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()