__author__ = 'mustafa salih oguz'
from Tkinter import *
from xlrd import *
import tkFileDialog, anydbm, ttk, tkMessageBox, os

class GUI(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.data = {}  # keeps all of the curriculum data
        self.Semester = "Semester I"  # chosen semester
        self.UI()

    def UI(self):
        """GUI elements and two events which are for display button and combobox"""

        def chooseSemester(event):
            """event that runs when user choose an option from COMBOBOX and converts it into roman numerals to use in excel exploration"""
            self.previousSemester = self.Semester
            self.Semester = choice.get()
            if "1" in self.Semester:
                self.Semester = "Semester I"
            elif "2" in self.Semester:
                self.Semester = "Semester II"
            elif "3" in self.Semester:
                self.Semester = "Semester III"
            elif "4" in self.Semester:
                self.Semester = "Semester IV"
            elif "5" in self.Semester:
                self.Semester = "Semester V"
            elif "6" in self.Semester:
                self.Semester = "Semester VI"
            elif "7" in self.Semester:
                self.Semester = "Semester VII"
            elif "8" in self.Semester:
                self.Semester = "Semester VIII"

        def courseView(event):
            """Event that happens when DISPLAY button is clicked.
             Headers and the course data will be extracted and displayed"""
            # if no excel file chosen it checks if there is a db or not. If not gives error, if there is a db, uses it to extract data. If excel file chosen data is ready already
            if self.filePath == "":
                if os.path.exists("curriculum.db") == False:
                    tkMessageBox.showinfo("Excel File Could Not Found",
                                          "A curriculum file should be selected first by clicking on the Browse button")
                    return
                else:
                    self.useDatabase()

            header1.grid(row=6, column=0)
            header2.grid(row=6, column=1)
            header3.grid(row=6, column=2)

            try:
                for i in range(len(self.data[self.previousSemester][0])):  # it uses previousSemester because previous and current semesters might have different number of courses
                    CourseCodes[i].grid_forget()
                    CourseCredits[i].grid_forget()
                    CourseTitles[i].grid_forget()
            except:
                pass

            # showing labels on the screen
            for i in range(len(self.data[self.Semester][0])):
                CourseCodes[i].config(text=self.data[self.Semester][0][i])
                CourseCodes[i].grid(row=i + 7, column=0)

                CourseTitles[i].config(text=self.data[self.Semester][1][i])
                CourseTitles[i].grid(row=i + 7, column=1)

                CourseCredits[i].config(text=self.data[self.Semester][2][i])
                CourseCredits[i].grid(row=i + 7, column=2)

        self.grid()
        self.filePath = ""  # Path of chosen excel file
        self.previousSemester = ""  # Semester chosen before current one. For cleaning additional old labels

        head = Label(self, text="Curriculum Viewer v1.0", bg="orange", fg="white", font="-weight bold", height=3)
        head.grid(row=0, column=0, sticky=EW, columnspan=3)

        lab1 = Label(self, text="Please select curriculum excel file:")
        lab1.grid(row=2, column=1, sticky=E, pady=10)

        lab2 = Label(self, text="Please select semester that you want to print:")
        lab2.grid(row=3, column=1, sticky=E)

        browse = Button(self, text='Browse', command=self.browseButton)
        browse.grid(row=2, column=2, sticky=W)

        display = Button(self, text="Display")
        display.grid(row=4, column=2, sticky=W)

        options = (
            'Semester 1', 'Semester 2', "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8")
        choice = StringVar()
        comboBox = ttk.Combobox(self, textvariable=choice, values=options, state='readonly')
        comboBox.current(0)
        comboBox.grid(row=3, column=2, sticky=W)

        header1 = Label(self, text="Course Code", font="-weight bold")
        header2 = Label(self, text="Course Title", font="-weight bold")
        header3 = Label(self, text="Credit", font="-weight bold")

        # Course Codes
        cc1 = Label(self, fg="maroon")
        cc2 = Label(self, fg="maroon")
        cc3 = Label(self, fg="maroon")
        cc4 = Label(self, fg="maroon")
        cc5 = Label(self, fg="maroon")
        cc6 = Label(self, fg="maroon")
        cc7 = Label(self, fg="maroon")
        cc8 = Label(self, fg="maroon")

        # Course Titles
        ct1 = Label(self, fg="maroon")
        ct2 = Label(self, fg="maroon")
        ct3 = Label(self, fg="maroon")
        ct4 = Label(self, fg="maroon")
        ct5 = Label(self, fg="maroon")
        ct6 = Label(self, fg="maroon")
        ct7 = Label(self, fg="maroon")
        ct8 = Label(self, fg="maroon")

        # Course redits
        cr1 = Label(self, fg="maroon")
        cr2 = Label(self, fg="maroon")
        cr3 = Label(self, fg="maroon")
        cr4 = Label(self, fg="maroon")
        cr5 = Label(self, fg="maroon")
        cr6 = Label(self, fg="maroon")
        cr7 = Label(self, fg="maroon")
        cr8 = Label(self, fg="maroon")

        # lists for using labels easily when changing text, deleting and displaying
        CourseCodes = [cc1, cc2, cc3, cc4, cc5, cc6, cc7, cc8]
        CourseTitles = [ct1, ct2, ct3, ct4, ct5, ct6, ct7, ct8]
        CourseCredits = [cr1, cr2, cr3, cr4, cr5, cr6, cr7, cr8]

        comboBox.bind("<<ComboboxSelected>>", chooseSemester)
        display.bind("<Button-1>", courseView)

    def browseButton(self):
        """Takes the path of chosen excel file and calls readExcel"""
        self.filePath = tkFileDialog.askopenfilename(filetypes=[('Excel Files', '.xlsx'), ('Excel Files', 'xls')],
                                                     title="Select the Excel File Contains Cirriculum")
        #if self.filePath != "":  # if an excel file chosen
        try:
            self.readExcel()  # going to read Excel file from given path
        except:
            pass

    def readExcel(self):
        """Reads data from Excel file and fills the data list which includes all curriculum data and calls fillDatabase"""
        book = open_workbook(self.filePath)  # opening chosen excel file to read

        sheet = book.sheet_by_index(0)  # choosing the first sheet of the spreadsheet

        # cleaning the data for newly chosen excel file. Format -> {"Semester I":[(Courses),(Titles),(Credits)]}
        self.data = {"Semester I": [(), (), ()], "Semester II": [(), (), ()], "Semester III": [(), (), ()],
                     "Semester IV": [(), (), ()], "Semester V": [(), (), ()], "Semester VI": [(), (), ()],
                     "Semester VII": [(), (), ()], "Semester VIII": [(), (), ()]}

        Totrow = sheet.nrows
        Totcol = sheet.ncols

        for i in self.data.keys():  # for loop that fills the data list
            # First Part: getting the cell name of the semester's title in (5,0) format which is row and column numbers.
            semesterCell = ()
            for row_index in range(Totrow):
                for col_index in range(Totcol):
                    cell = sheet.cell(row_index, col_index).value
                    if type(cell) is not float:  # encode doesn't work with floats
                        if i.encode('utf-8') in (cell).encode('utf-8'):  # Can't use str() because of Turkish characters
                            semesterCell = (row_index, col_index)  # If value of the cell equals to the wanted semester takes the row and column data.
                            break
                if semesterCell == (row_index, col_index):
                    break

            # Second Part: taking the data from excel file according to the semester's row and column number
            emptyCode = 0  # for checking if there are two empty rows back to back. When reached 2 it means semester data ended and breaks the loop"
            for row_index in range(semesterCell[0] + 2, Totrow):  # used + 2 for not checking title lines like "Semester I" or "Code"
                for col_index in range(semesterCell[1], Totcol):
                    cell = sheet.cell(row_index, col_index).value

                    # ending conditions for breaking the inner for loop
                    if cell == "" and col_index != semesterCell[1] + 5:  # If cell is empty and it is not credits column. Empty in credits column means non-credit
                        if cell == "" and col_index == semesterCell[1]:  # if code column cell is empty increase emptyCode by 1
                            emptyCode += 1
                            continue
                        else:
                            continue
                    elif type(cell) is not float:  # If the semester ended
                        if "Semester" in cell and "Total" not in cell or emptyCode == 2:
                            break

                    # filling the data list
                    if col_index == semesterCell[1]:  # Code column. Same column with the "Semester X" title
                        self.data[i][0] += cell.encode("utf-8"),  # using encode to get rid of "'u" at the start
                    elif col_index == semesterCell[1] + 1 and "Total" in cell:  # Title column 1 line after code column. Checking if it is a title or "Total Semester" line
                        break
                    elif col_index == semesterCell[1] + 1:
                        self.data[i][1] += cell.encode("utf-8"),
                    elif col_index == semesterCell[1] + 5:  # Credits column. 5 column after the code column
                        if cell == "":  # if line is empty it means non-credit course
                            self.data[i][2] += "(non-credit)",
                            break
                        else:
                            self.data[i][2] += int(cell),
                            break

                # ending conditions for breaking the outer for loop
                if type(cell) is not float:
                    if "Semester" in cell and "Total" not in cell or emptyCode == 2:
                        break

        self.fillDatabase()

    def fillDatabase(self):
        """fills the database with the data list"""
        db = anydbm.open("curriculum.db", "c")
        for i in self.data.keys():
            db["%s - Courses" % i] = str(self.data[i][0])[1:-1]  # [1:-1] for eliminating the parenthesis of the tuple
            db["%s - Titles" % i] = str(self.data[i][1])[1:-1]
            db["%s - Credits" % i] = str(self.data[i][2])[1:-1]
        db.close()

    def useDatabase(self):
        """uses the database to fill the data list"""
        db = anydbm.open("curriculum.db", "r")
        courses = (db["%s - Courses" % self.Semester])[1:-1].split("', '")  # [1:-1].split("', '") for eliminating ' characters
        titles = (db["%s - Titles" % self.Semester])[1:-1].split("', '")
        credits = (db["%s - Credits" % self.Semester]).split(", ")
        for i in range(len(courses)):
            self.data[self.Semester] = [tuple(courses), tuple(titles), tuple(credits)]
        db.close()

def main():
    root = Tk()
    root.title("Mustafa Salih Oguz - Ergun Demiro")
    root.resizable(width=FALSE, height=FALSE)
    app = GUI(root)
    root.mainloop()

main()