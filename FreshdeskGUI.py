from PySide6 import QtWidgets, QtCore
import sys

from MainWindow import Ui_HelloWorldUI
from GetAllTickets import GetAllTickets


class MainWindow(QtWidgets.QMainWindow, Ui_HelloWorldUI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Create a model
        self.model = QtCore.QStringListModel()

        # Setup ticket list on startup
        self.updateTicketList()

        # Connecting update button
        self.pushButton_UpdateTickets.clicked.connect(self.updateTicketList)

    def updateTicketList(self):
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
                ticketItems.append(f"ID: {ticket.get("id")}, Sender: {email}")

        return ticketItems


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()