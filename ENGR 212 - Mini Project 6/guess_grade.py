__author__ = "mustafa salih oguz"

from Tkinter import *
from xlrd import *
from selenium import webdriver
import docclass, tkFileDialog, time

class GUI(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.filePath=""
        self.UI()

    def UI(self):
        def browse(event):
            """Takes the path of chosen excel file and calls readExcel then readUrl"""
            self.filePath = tkFileDialog.askopenfilename(filetypes=[('Excel Files', '.xlsx'), ('Excel Files', 'xls')], title="Select the Excel File Contains Cirriculum")
            if self.filePath != "":  # if an excel file chosen
                self.readExcel()  # going to read Excel file from given path and form trainer - guess dictionaries
                self.readUrl()

        def predict(event):
            """predicts results by training classifier then calls printOut function"""
            cl = docclass.naivebayes(docclass.getwords)

            # training classifier
            for i in self.trainer:
                if self.trainer[i][0] !="" and self.trainer[i][1] !="":
                    cl.train(self.trainer[i][0], self.trainer[i][1])

            # predicting grades for other courses
            for i in self.guess:
                if self.guess[i][0] !="":
                    self.guess[i][1] = cl.classify(self.guess[i][0], default="unknown")

            # printing predicted results to text widget
            self.printOut()

        self.grid()
        frame1 = Frame(self)
        frame1.grid(row=0, column=0, sticky=EW)
        Label(frame1, text="Guess My Grade! v1.0", fg="white", bg="black", height=3, font="-weight bold").grid(row=0, column=0, columnspan=5, sticky=EW)
        Label(frame1, text="Please upload your curriculum file with the grades:", fg="blue", font="-weight bold").grid(row=1, column=0, pady=10, sticky=W, padx=5)

        buttonBrowse = Button(frame1, text="Browse", fg="white", bg="maroon", width=20, font="-weight bold")
        buttonBrowse.grid(row=1, column=1,padx=20, sticky=W)

        Label(frame1, text='-'*200).grid(row=2, column=0, columnspan=5,sticky=EW)
        Label(frame1, text="Enter urls for course descriptions").grid(row=3, column=0, sticky=W, padx=5)

        self.textUrl = Text(frame1, width=80, height=6)
        self.textUrl.grid(row=4, column=0, sticky=W, padx=5)
        self.textUrl.insert(END, "http://www.sehir.edu.tr/en/Pages/Academic/Bolum.aspx?BID=12\n"
                                      "http://www.sehir.edu.tr/en/Pages/Academic/Bolum.aspx?BID=13\n"
                                      "http://www.sehir.edu.tr/en/Pages/Academic/Bolum.aspx?BID=14\n"
                                      "http://www.sehir.edu.tr/en/Pages/Academic/Bolum.aspx?BID=32")
        Label(frame1, text="Key:", font="-weight bold").grid(row=5, column=0, sticky=W, padx=5)

        frame2 = Frame(self)
        frame2.grid(row=1, column=0, sticky=EW)
        Label(frame2, text="A", fg="white", bg="dark green", width=10, font="-weight bold").grid(row=0, column=0, sticky=W, padx=5)
        Label(frame2, text="B", fg="white", bg="light green", width=10, font="-weight bold").grid(row=0, column=1, sticky=W, padx=5)
        Label(frame2, text="C", fg="white", bg="orange", width=10, font="-weight bold").grid(row=0, column=2, sticky=W, padx=5)
        Label(frame2, text="D", fg="white", bg="red", width=10, font="-weight bold").grid(row=0, column=3, sticky=W, padx=5)
        Label(frame2, text="F", fg="white", bg="black", width=10, font="-weight bold").grid(row=0, column=4, sticky=W, padx=5)

        buttonPredict = Button(frame2, text="Predict Grades", fg="white", bg="maroon", width=20, font="-weight bold")
        buttonPredict.grid(row=0, column=5,padx=25, sticky=W)

        Label(frame2, text='-'*200).grid(row=1, column=0, columnspan=6, sticky=EW)
        Label(frame2, text="Predicted Grades", font="-weight bold").grid(row=2, column=0, columnspan=2, sticky=W, padx=5)

        scrollText= Scrollbar(frame2)
        self.textPredict = Text(frame2, height=15, yscrollcommand=scrollText.set)
        self.textPredict.grid(row=3, column=0, columnspan=6, sticky=EW)
        scrollText.grid(row=3, column=7, sticky=W+NS, rowspan=2)
        scrollText.config(command=self.textPredict.yview)

        buttonBrowse.bind("<Button-1>", browse)
        buttonPredict.bind("<Button-1>", predict)

    def readExcel(self):
        """Reads data from Excel file and form trainer - guess dictionaries"""
        book = open_workbook(self.filePath)  # opening chosen excel file to read

        sheet = book.sheet_by_index(0)  # choosing the first sheet of the spreadsheet

        self.trainer = {}  # {Course:[Description, Grade], Course2:[Description, Grade]}
        self.guess = {}  # {Course:[Description, Grade, Semester], Course2:[Description, Grade, Semester]}

        semesters=["Semester I", "Semester II", "Semester III", "Semester IV", "Semester V", "Semester VI", "Semester VII", "Semester VIII"]

        Totrow = sheet.nrows
        Totcol = sheet.ncols

        for i in semesters:  # for loop that fills the data list
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
            col_index=semesterCell[1]
            # Second Part: taking the data from excel file according to the semester's row and column number
            emptyCode = 0  # for checking if there are two empty rows back to back. When reached 2 it means semester data ended and breaks the loop"
            for row_index in range(semesterCell[0] + 2, Totrow):  # used + 2 for not checking title lines like "Semester I" or "Code"

                    cell = sheet.cell(row_index, col_index).value.encode("utf-8")  # course code
                    grade = sheet.cell(row_index, col_index+6).value.encode("utf-8")  # grade of the course

                    # ending conditions for breaking the inner for loop
                    if cell == "" :  # If cell is empty
                        emptyCode += 1
                        continue
                    elif type(cell) is not float:  # If the semester ended
                        if "Semester" in cell and "Total" not in cell or emptyCode == 2:
                            break

                    # filling the data list
                    if grade != "":
                        self.trainer[cell]=["", grade[0]]
                    else:
                        if "xxx" in cell:
                            continue
                        elif "UNI" in cell:
                            self.guess[cell]=["", "", "UNI Courses"]
                        else:
                            self.guess[cell]=["","",i]

    def readUrl(self):
        """call functions that are going to extract data from given urls"""
        urls = self.textUrl.get("1.0", END).encode("utf-8").split("\n")
        if "cs.xlsx" in self.filePath:
            self.get_courses(urls[0])
        if "ee.xlsx" in self.filePath:
            self.get_courses(urls[1])
        if "ie.xlsx" in self.filePath:
            self.get_courses(urls[2])
        self.get_uni_courses(urls[3])

    def get_uni_courses(self, url):
        """Get uni course code and descriptions from given url"""
        #opening the page
        driver = webdriver.Firefox()
        driver.get(url)
        driver.close()
        isDescription = 0
        courseCode=[]
        # taking data from the text in the body
        for i in driver.find_element_by_tag_name("body").text.split("\n"):
            if isDescription > 0:  # taking description
                if isDescription == 1:
                    isDescription += 1
                    continue

                for j in courseCode:
                    if j in self.trainer:
                        self.trainer[j][0] = i
                    elif j in self.guess:
                        self.guess[j][0] = i
                    else:
                        self.guess[j] = [i, "", "UNI Courses"]
                isDescription=0

            if "ECTS" in i:  # taking course codes
                isDescription = 1
                courseCode=[]
                if i.count("UNI")>1:
                    courseCode.append("UNI %s" % (i.split()[1]))
                    courseCode.append("UNI %s" % (i.split()[4]))
                else:
                    if "TURKISH FOR INTERNATIONAL STUDENTS" in i:
                        for j in range(1,12, 2):
                            courseCode.append("UNI %s" % (i.split()[j]))
                    else:
                        courseCode.append(" ".join(i.split()[0:2]))

    def get_courses(self, url):
        """Get course code and description data from given urls"""
        # clicking the Course Descriptions text
        driver = webdriver.Firefox()
        driver.get(url)
        line = driver.find_element_by_link_text("Course Descriptions")
        line.click()
        time.sleep(5)
        driver.close()

        # getting course descriptions
        isDescription = False
        courseCode=""
        for i in driver.find_element_by_tag_name("body").text.split("\n"):
            if isDescription == True:  # taking description
                isDescription = False
                if courseCode in self.trainer:
                    self.trainer[courseCode][0] = i
                elif courseCode in self.guess:
                    self.guess[courseCode][0] = i
                else:
                    self.guess[courseCode] = [i, "", "Departmental Electives"]

            if "ECTS" in i:  # taking course code
                isDescription = True
                courseCode= " ".join(i.split()[0:2])

    def printOut(self):
        """printing calculated data to text widget"""
        # separating results to semesters
        toPrint = {"Semester III":{}, "Semester IV":{}, "Semester V":{}, "Semester VI":{}, "Semester VII":{}, "Semester VIII":{}, "UNI Courses":{}, "Departmental Electives":{}}
        for i in self.guess:
            toPrint[self.guess[i][2]][i]=self.guess[i][1]
        semesters=["Semester III", "Semester IV", "Semester V", "Semester VI", "Semester VII", "Semester VIII", "UNI Courses", "Departmental Electives"]  # for ordering

        # tags for different circumstances
        self.textPredict.tag_config("title", underline=1, font="Helvetica 15")
        self.textPredict.tag_config("A", background="dark green", font="Helvetica 15")
        self.textPredict.tag_config("B", background="light green", font="Helvetica 15")
        self.textPredict.tag_config("C", background="orange", font="Helvetica 15")
        self.textPredict.tag_config("D", background="red", foreground="white", font="Helvetica 15")
        self.textPredict.tag_config("F", background="black", foreground="white", font="Helvetica 15")

        # adding data to text widget with wanted style
        self.textPredict.delete("1.0", END)
        for i in semesters:
            if toPrint[i] == {}:
                continue
            self.textPredict.insert(END, i+"\n\n", "title")
            for j in toPrint[i]:
                if toPrint[i][j] == "":
                    continue
                self.textPredict.insert(END, "%s --> %s\n" % (j, toPrint[i][j]), "%s" %(toPrint[i][j]))
            self.textPredict.insert(END, "\n")

if __name__ == "__main__":
    root = Tk()
    root.title("Guess My Grade")
    root.resizable(width=FALSE, height=FALSE)
    app = GUI(root)
    root.mainloop()