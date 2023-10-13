import xlsxwriter
import sys
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QPushButton
import mysql.connector
import pandas as pd
import csv

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # window size 
        self.resize(1250, 850)
        self.ui()
        self.sub_window = None
        self.data = None
        self.ids = ""
        self.current_page=0
        self.operation=""
        self.query =""
        self.fileNames=[]
        self.offset=0
        self.page_size = 1000
        self.columns=["ID", "None2", "Email", "Phone", "Religon", "Birthdate",
             "FirstName", "SecondName","Gender", "ProfileLink",
             "None11", "UserName", "FullName", "BIO", "WorksIn",
             "WorksAs","CityFrom", "LivesIn", "WentToSchool",
             "FacebookMail", "None21 0", "None22 0", "None23 0",
             "None24 Date", "None25 Date", "RelationshipState" ]
        
    #ui
    def ui(self):
        # Create a table widget and populate it with some data
        self.tableWidget = QtWidgets.QTableWidget()
        self.progress = QtWidgets.QProgressBar()
        self.tableWidget.setRowCount(0) # initialize with 0 rows
        self.tableWidget.setColumnCount(26)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "None2", "Email", "Phone", "Religon", "Birthdate",
             "FirstName", "SecondName","Gender", "ProfileLink",
             "None11", "UserName", "FullName", "BIO", "WorksIn",
             "WorksAs","CityFrom", "LivesIn", "WentToSchool",
             "FacebookMail", "None21 0", "None22 0", "None23 0",
             "None24 Date", "None25 Date", "RelationshipState" ])
        # Allow multiple cell selection
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # Create a "Copy" action in the Edit menu
        copyAction = QtGui.QAction("Copy", self)
        copyAction.setShortcut(QtGui.QKeySequence.Copy)
        copyAction.triggered.connect(self.copySelection)
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(copyAction)

    # Create two buttons on the left side
        self.read_data = QtWidgets.QPushButton('read data', self)
        self.button1 = QtWidgets.QPushButton('search ids', self)
        self.button = QtWidgets.QPushButton("Advanced search",self)
        self.clear_button = QtWidgets.QPushButton('clear', self)
        self.load_button = QtWidgets.QPushButton('load more', self)
  
        self.read_data.clicked.connect(self.visualize_data)
        self.button.clicked.connect(self.open_window2)
        self.button1.clicked.connect(self.search_ids)
        self.clear_button.clicked.connect(self.clear)
        self.load_button.clicked.connect(self.load_more)


        # Create a horizontal layout for the buttons
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.addWidget(self.read_data)
        self.buttonLayout.addWidget(self.button1)
        self.buttonLayout.addWidget(self.button)

        self.buttonLayout.addWidget(self.load_button)
        self.buttonLayout.addWidget(self.clear_button)
 
        # Create the dropdown list and add options
        self.combo_box = QtWidgets.QComboBox(self)
        self.buttonLayout.addWidget(self.combo_box)
  
        # Add the options to the combo box
        self.combo_box.addItem('Select Export Type', None)
        self.combo_box.addItem('CSV', 'csv')
        self.combo_box.addItem('Excel', 'xlsx')
        self.combo_box.addItem('Text', 'txt')

        # Connect the dropdown list to the function handler
        self.combo_box.currentIndexChanged.connect(self.export_data)

        # Create a vertical layout for the table and add it to the main layout
        tableLayout = QtWidgets.QVBoxLayout()
        tableLayout.addWidget(self.tableWidget)
        tableLayout.addWidget(self.progress)

        # Create a horizontal layout to hold the button layout and table layout
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(self.buttonLayout)
        mainLayout.addLayout(tableLayout)

        # Create a central widget and set the main layout
        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    # functions
    def visualize_data(self):
            if not self.fileNames:
                # If the file hasn't been selected, prompt the user to select a file
                options = QtWidgets.QFileDialog.Options()
                fileNames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Files", "", "Text Files (*.txt);;All Files (*)", options=options)
                if fileNames:
                    self.fileNames.append(fileNames[0])
                    self.operation = "visualize"
                    self.query = "yes"
             
                    # Read the next chunk of data
                    data = pd.read_csv(self.fileNames[0], header=None, quotechar=",", names=self.columns, encoding="utf-8", usecols=range(0, 26), skiprows=self.offset, nrows= self.page_size)
                    print("sasa1")
                    rows = data.values.tolist()
                
                    self.current_page += 1
                    # insert into the table the fetched rows
                    for row in rows:
                        table_row = self.tableWidget.rowCount()
                        self.tableWidget.insertRow(table_row)
                        for col, item in enumerate(row):
                            table_item = QtWidgets.QTableWidgetItem(str(item))
                            self.tableWidget.setItem(table_row, col, table_item)
                            
                    # Update the progress bar value
                    self.progress.setValue(self.tableWidget.rowCount())

                    # Update the page label
                    page = (self.offset // self.page_size) + 1
                    page_label = QtWidgets.QLabel(f'Page {page}')
                    page_label.setAlignment(QtCore.Qt.AlignCenter)
                    self.tableWidget.setCellWidget(50, 0, page_label)

                    # Update the progress bar format
                    self.progress.setFormat(f'Fetching data ({self.offset+1}-{self.offset+len(rows)}) page {page}')

    def clear(self):
        self.sub_window = None
        self.data = None
        self.ids = ""
        self.current_page=0
        self.operation=""
        self.query =""
        self.fileNames=[]
        self.offset=0
        self.page_size = 10000
        self.tableWidget.setRowCount(0) # initialize with 0 rows

    def search_ids(self):
        self.operation = "ids"

        # Get the list of files from the user.
        try:
            options = QtWidgets.QFileDialog.Options()
            fileNames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Files", "", "Text Files (*.txt);;All Files (*)", options=options)
        except Exception:
            QtWidgets.QMessageBox.information(self, "invalid file", "invalid file structure")
            
        # If no files were selected, return.
        if not fileNames:
            return

        # Read the ids from the files.
        ids = []
        for fileName in fileNames:
            with open(fileName, 'r', encoding='utf-8') as f:
                ids.extend([f"'{line.strip()}'" for line in f])

        # Connect to the database.
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='zbady')
        cursor = cnx.cursor()

        # Construct the SQL query.
        query = "SELECT * FROM zabadytable WHERE ID IN (%s)" % ','.join(ids)

        # Execute the query.
        cursor.execute(query)
        rows = cursor.fetchall()
        # print(type(rows))
        len(rows)
        rows= self.filter(rows)
        # Calculate the total number of pages.
        total_count = cursor.rowcount

        # Set the progress bar properties.
        self.progress.setMaximum(total_count)
        self.progress.setValue(0)
        self.progress.setFormat(f"Page {self.current_page} ({self.offset+1}-{self.offset+len(rows)} of {total_count} rows)")

        # Insert the rows into the table.
        self.tableWidget.setRowCount(0)
        for row in rows:
            table_row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(table_row)
            for col, item in enumerate(row):
                table_item = QtWidgets.QTableWidgetItem(str(item.replace('"',"")))
                self.tableWidget.setItem(table_row, col, table_item)

            # Update the progress bar value.
            self.progress.setValue(table_row + 1)

        # Close the cursor and the connection.
        if len(rows) == 0:
            # Display a message to the user indicating that no rows were found.
            QtWidgets.QMessageBox.information(self, "No Rows Found", "No rows were found matching the specified criteria.")
         
        cursor.close()
        cnx.close()
    def copySelection(self):
        selectedCells = self.tableWidget.selectedItems()

        # Sort the cells by row and column
        selectedCells.sort(key=lambda item: (item.row(), item.column()))

        # Concatenate the cell values into a tab-separated string
        copiedText = ""
        currentRow = -1
        for cell in selectedCells:
            if cell.row() != currentRow:
                currentRow = cell.row()
                copiedText += "\n" if len(copiedText) > 0 else ""
            else:
                copiedText += "\t"
            copiedText += cell.text()

        # Copy the text to the clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(copiedText)
    
    def open_window2(self):
        self.sub_window = AnotherWindow()
        self.sub_window.data_ready.connect(self.handle_data)
        self.sub_window.show()
        
    def handle_data(self, data):
        self.operation="Advanced Search"
        # Define the page size and offset

        self.query = data
        if self.query != "no data available":
            # Construct the SQL query with LIMIT and OFFSET
            cnx = mysql.connector.connect(user='root', password='', host='localhost', database='zbady')
            cursor = cnx.cursor()
            query = self.query
            cursor.execute(query + f" LIMIT {self.page_size} OFFSET {self.offset}")
            rows = cursor.fetchall()

            # Calculate the total number of pages
            total_count = cursor.rowcount
            
            # Set the progress bar properties
            self.progress.setMaximum(total_count)
            self.progress.setValue(0)
            self.progress.setFormat(f"Page {self.current_page} ({self.offset+1}-{self.offset+len(rows)} of {total_count} rows)")

            # insert into the table the fetched rows
            self.tableWidget.setRowCount(0)
            for row in rows:
                table_row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(table_row)
                for col, item in enumerate(row):
                    table_item = QtWidgets.QTableWidgetItem(str(item))
                    self.tableWidget.setItem(table_row, col, table_item)

                # Update the progress bar value
                self.progress.setValue(table_row + 1)

            cursor.close()
            cnx.close()
            self.sub_window.close()
        else:
            QtWidgets.QMessageBox.information(self, "No Rows Found", "No rows were found matching the specified criteria.")
         
    

    def export_data(self, index):
        # Create a database connection
        cnx = mysql.connector.connect(host='localhost', user='root', password='', database='zbady')

        selected_option = self.combo_box.itemData(index, Qt.UserRole)
        query = 'SELECT * FROM zabadytable'

        # Read the data from the database
        df = pd.read_sql_query(query, con=cnx)

        # Close the database connection
        cnx.close()

        if selected_option == None:
            return

        # Get the file name and file type from the user
        file_types = {
            'csv': 'CSV (*.csv)',
            'xlsx': 'Excel (*.xlsx)',
            'txt': 'Text (*.txt)'
        }
        file_type = file_types[selected_option]
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(filter=file_type)

        if file_name:
            if selected_option == 'csv':
                # Save the filtered data to a CSV file
                df.to_csv(file_name, index=False, header=False, quoting=csv.QUOTE_NONE, escapechar=' ')
            elif selected_option == 'xlsx':
                # Save the filtered data to an Excel file
                workbook = xlsxwriter.Workbook(file_name)
                worksheet = workbook.add_worksheet()
                headers = list(df.columns.values)
                for i, header in enumerate(headers):
                    worksheet.write(0, i, header)
                for row_num, row_data in df.iterrows():
                    for col_num, cell_value in enumerate(row_data):
                        worksheet.write(row_num + 1, col_num, cell_value)
                workbook.close()
            elif selected_option == 'txt':
                # Save the filtered data to a text file
                df.to_csv(file_name, sep=' ', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar=' ')
        
    def load_more(self):
        if self.query:
            
            if self.operation == "ids":
                cnx = mysql.connector.connect(user='root', password='', host='localhost', database='zbady')
                cursor = cnx.cursor()

                self.offset = self.tableWidget.rowCount() - 1

                # Construct the SQL query with LIMIT and OFFSET
                query = f"SELECT * FROM zabadytable WHERE ID IN ({self.ids}) LIMIT {self.page_size} OFFSET {self.offset}"
                cursor.execute(query)
                rows = cursor.fetchall()

                
                cursor.close()
                cnx.close()
            elif self.operation == "Advanced Search":
                cnx = mysql.connector.connect(user='root', password='', host='localhost', database='zbady')
                cursor = cnx.cursor()
                # Define the page size and offset

                self.offset = self.tableWidget.rowCount() - 1
                # Construct the SQL query with LIMIT and OFFSET
                query = self.query
                cursor.execute(query + f" LIMIT {self.page_size} OFFSET {self.offset}")
                rows = cursor.fetchall()
                cursor.close()
                cnx.close()
            elif self.operation == "visualize":
                # Read the next chunk of data
                self.offset = self.current_page *  self.page_size 
                
                data = pd.read_csv(self.fileNames[0], header=None, quotechar=",", names=self.columns, encoding="utf-8", usecols=range(0, 26), skiprows=self.offset, nrows=  self.page_size)
                print("sasa2")
                rows=data.itertuples(index=False)
                print("sasa3")
            for row in rows:
                table_row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(table_row)
                for col, item in enumerate(row):
                    table_item = QtWidgets.QTableWidgetItem(str(item))
                    self.tableWidget.setItem(table_row, col, table_item)
            print("sasa4")

            self.current_page += 1

            # Update the progress bar value
            self.progress.setValue(self.tableWidget.rowCount())

            # Update the page label
            page = (self.offset // self.page_size) + 1
            page_label = QtWidgets.QLabel(f'Page {page}')
            page_label.setAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setCellWidget(50, 0, page_label)

            # Update the progress bar format
            self.progress.setFormat(f'Fetching data ({self.offset+1}-{self.offset+len(data)}) page {page}')
            # Set the number of rows and columns in the model
            
            # Check if the query fetched zero rows.
           
    def filter(self,query):
      
        # Read the data into a Pandas DataFrame
       # Convert the list to a DataFrame
        df = pd.DataFrame(query, columns=self.columns)


        # Filter the DataFrame based on unique values of the phone column
        unique_phones = df['Phone'].unique()
        filtered_df = df[df['Phone'].isin(unique_phones)]
        # Print the filtered DataFrame
        print(len(filtered_df))
        return filtered_df 

                  
class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    data_ready = QtCore.Signal(str)
    def __init__(self):
        super().__init__()
        # window size 
        self.resize(1200, 800)
        self.ui()
    def ui(self):
        #22 labels and input fields
        self.label_1 = QtWidgets.QLabel('ID')
        self.lineedit_1 = QtWidgets.QLineEdit()
        self.label_2 = QtWidgets.QLabel('Email')
        self.lineedit_2 = QtWidgets.QLineEdit()
        self.label_3 = QtWidgets.QLabel('Phone')
        self.lineedit_3 = QtWidgets.QLineEdit()
        self.label_4 = QtWidgets.QLabel('Religon')
        self.lineedit_4 = QtWidgets.QLineEdit()
        self.label_5 = QtWidgets.QLabel('Birthdate')
        self.lineedit_5 = QtWidgets.QLineEdit()
        self.label_6 = QtWidgets.QLabel('FirstName')
        self.lineedit_6 = QtWidgets.QLineEdit()
        self.label_7 = QtWidgets.QLabel('SecondName')
        self.lineedit_7 = QtWidgets.QLineEdit()
        self.label_8 = QtWidgets.QLabel('Gender')
        self.lineedit_8 = QtWidgets.QLineEdit()
        self.label_9 = QtWidgets.QLabel('ProfileLink')
        self.lineedit_9 = QtWidgets.QLineEdit()
        self.label_10 = QtWidgets.QLabel('UserName')
        self.lineedit_10 = QtWidgets.QLineEdit()
        self.label_11 = QtWidgets.QLabel('FullName')
        self.lineedit_11 = QtWidgets.QLineEdit()
        self.label_12 = QtWidgets.QLabel('BIO')
        self.lineedit_12 = QtWidgets.QLineEdit()
        self.label_13 = QtWidgets.QLabel('WorksIn')
        self.lineedit_13 = QtWidgets.QLineEdit()
        self.label_14 = QtWidgets.QLabel('WorksAs')
        self.lineedit_14 = QtWidgets.QLineEdit()
        self.label_15 = QtWidgets.QLabel('CityFrom')
        self.lineedit_15 = QtWidgets.QLineEdit()
        self.label_16 = QtWidgets.QLabel('LivesIn')
        self.lineedit_16 = QtWidgets.QLineEdit()
        self.label_17 = QtWidgets.QLabel('WentToSchool')
        self.lineedit_17 = QtWidgets.QLineEdit()
        self.label_18 = QtWidgets.QLabel('FacebookMail')
        self.lineedit_18 = QtWidgets.QLineEdit()
        self.label_19 = QtWidgets.QLabel('RelationshipState')
        self.lineedit_19 = QtWidgets.QLineEdit()
        self.label_20 = QtWidgets.QLabel('Label 20')
        self.lineedit_20 = QtWidgets.QLineEdit()
        self.label_21 = QtWidgets.QLabel('Label 21')
        self.lineedit_21 = QtWidgets.QLineEdit()
        self.label_22 = QtWidgets.QLabel('Label 22')
        self.lineedit_22 = QtWidgets.QLineEdit()

        #buttons
        self.button = QPushButton("Save Data",self)
        self.button.clicked.connect(self.search_records)

        # Create a grid layout with two columns
        layout = QtWidgets.QGridLayout()

        
        # Add the labels and input fields to the layout
        layout.addWidget(self.label_1, 0, 0)
        layout.addWidget(self.lineedit_1, 0, 1)
        layout.addWidget(self.label_2, 1, 0)
        layout.addWidget(self.lineedit_2, 1, 1)
        layout.addWidget(self.label_3, 2, 0)
        layout.addWidget(self.lineedit_3, 2, 1)
        layout.addWidget(self.label_4, 3, 0)
        layout.addWidget(self.lineedit_4, 3, 1)
        layout.addWidget(self.label_5, 4, 0)
        layout.addWidget(self.lineedit_5, 4, 1)
        layout.addWidget(self.label_6, 5, 0)
        layout.addWidget(self.lineedit_6, 5, 1)
        layout.addWidget(self.label_7, 6, 0)
        layout.addWidget(self.lineedit_7, 6, 1)
        layout.addWidget(self.label_8, 7, 0)
        layout.addWidget(self.lineedit_8, 7, 1)
        layout.addWidget(self.label_9, 8, 0)
        layout.addWidget(self.lineedit_9, 8, 1)
        layout.addWidget(self.label_10, 9, 0)
        layout.addWidget(self.lineedit_10, 9, 1)
        layout.addWidget(self.label_11, 10, 0)
        layout.addWidget(self.lineedit_11, 10, 1)
        layout.addWidget(self.label_12, 0, 2)
        layout.addWidget(self.lineedit_12, 0, 3)
        layout.addWidget(self.label_13, 1, 2)
        layout.addWidget(self.lineedit_13, 1, 3)
        layout.addWidget(self.label_14, 2, 2)
        layout.addWidget(self.lineedit_14, 2, 3)
        layout.addWidget(self.label_15, 3, 2)
        layout.addWidget(self.lineedit_15, 3, 3)
        layout.addWidget(self.label_16, 4, 2)
        layout.addWidget(self.lineedit_16, 4, 3)
        layout.addWidget(self.label_17, 5, 2)
        layout.addWidget(self.lineedit_17, 5, 3)
        layout.addWidget(self.label_18, 6, 2)
        layout.addWidget(self.lineedit_18, 6, 3)
        layout.addWidget(self.label_19, 7, 2)
        layout.addWidget(self.lineedit_19, 7, 3)
        layout.addWidget(self.label_20, 8, 2)
        layout.addWidget(self.lineedit_20, 8, 3)
        layout.addWidget(self.label_21, 9, 2)
        layout.addWidget(self.lineedit_21, 9, 3)
        layout.addWidget(self.label_22, 10, 2)
        layout.addWidget(self.lineedit_22, 10, 3)
        layout.addWidget(self.button, 11, 2)

        # Set the layout for the main window
        self.setLayout(layout)

        # Set the fixed width for the window
        self.setFixedWidth(800)

    def search_records(self):
        # Define the labels and input fields as label_lineedit_pairs
        dic = {
            "lineedit_1": "ID", "lineedit_2": "Email", "lineedit_3": "Phone", "lineedit_4": "Religon",
            "lineedit_5": "Birthdate", "lineedit_6": "FirstName", "lineedit_7": "SecondName", "lineedit_8": "Gender",
            "lineedit_9": "ProfileLink", "lineedit_10": "UserName", "lineedit_11": "FullName", "lineedit_12": "BIO",
            "lineedit_13": "WorksIn", "lineedit_14": "WorksAs", "lineedit_15": "CityFrom", "lineedit_16": "LivesIn",
            "lineedit_17": "WentToSchool", "lineedit_18": "FacebookMail", "lineedit_19": "RelationshipState", "lineedit_20": "Label 20",
            "lineedit_21": "Label 21", "lineedit_22": "Label 22",
        }
        column_names = []
        values = []
        for i in range(1, 23):
            text = getattr(self, f"lineedit_{i}").text()
            if text:
                column_names.append(dic[f"lineedit_{i}"])
                # params.append("?")
                s=f'"{text}"'
                values.append(f"'{s}'")
        if len(column_names)==0 and len(values)==0:
            
            self.data_ready.emit("no data available")
        else:
            # Create the SQL query using the column names and parameter placeholders
            query = f"SELECT * FROM zabadytable  WHERE {' AND '.join([f' {column_names[i]} = {values[i]}' for i in range(len(column_names))])}"
        
            self.data_ready.emit(query)

   
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window1 = MainWindow()
    window1.show()
    app.exec()
