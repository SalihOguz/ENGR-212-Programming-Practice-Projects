__author__ = "mustafa salih oguz"
from Tkinter import *
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
import ttk, io, urllib2
from urllib2 import urlopen

class GUI(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.url=""
        self.UI()

    def UI(self):
        def get_html(event):
            """extracting html file from given url, populates comboboxes with the data taken from the page"""
            # getting html
            response = urllib2.urlopen(url.get())
            self.html = response.read()
            self.soup = BeautifulSoup(self.html, 'html.parser')

            # populating comboboxes
            years.config(values=self.comboYear())
            years.current(0)

            principal.config(values=self.comboPrincipal())
            principal.current(0)

            funding.config(values=self.comboFunding())
            funding.current(0)

        def listFill(event):
            """filters all the projects based on combobox choices and add project titles to listbox"""
            data=[]
            for i in self.soup.find_all(class_ ="list-group-item"):  # adding project title and year to data list
                yearString = i.find_next('p').string
                data.append([i.find_next('a').get("id").encode("utf-8"), yearString.encode("utf-8").split()[2]+"-"+yearString.encode("utf-8").split()[6],"",""])

            investigatorList=[]
            for i in self.soup.find_all(class_  = "list-group-item"):  # getting principal investigators
                principalStr = i.find_all("p")
                for j in principalStr[2].find_all("a"):
                        investigatorList.append(j.encode("utf-8").strip().split()[2]+" "+j.encode("utf-8").strip().split()[3])

            fundingList=[]
            for i in self.soup.find_all(class_  = "list-group-item"):  # getting funding institutions
                institutionsStr = i.find_all("p")
                for j in institutionsStr[1]:
                    if "<" not in j.encode("utf-8").strip() and "" != j.encode("utf-8").strip() and j.encode("utf-8").strip():
                        fundingList.append(j.encode("utf-8").strip())

            for i in range(len(investigatorList)):  # adding investigators and institutions to data list
                data[i][2]= investigatorList[i]
                data[i][3]= fundingList[i]

            # getting combobox choices
            year = yearChoice.get()
            investigator = principalChoice.get()
            fundings = fundingChoice.get()

            print data

            # filtering and adding to the listbox
            listProject.delete(0, END)
            for i in range(len(data)):
                if year != "All Years" and (int(year) < int(data[i][1].split("-")[0]) or int(year) > int(data[i][1].split("-")[1])):
                    continue
                if investigator != "All Investigators" and investigator.encode("utf-8") != data[i][2]:
                    continue
                if fundings != "All Institutions" and fundings.encode("utf-8") !=  data[i][3]:
                    continue
                listProject.insert(END, data[i][0])

        def showDescpription(event):
            """prints the description of projects on listbox and displays picture of the project on canvas"""
            # adding text to the Text widget
            text=[]
            for i in self.soup.find_all(class_ ="list-group-item"):
                if i.find_next(id=listProject.get(listProject.curselection())) != None:
                    text.append(i.find_next(class_="gap").string)
            try:
                textBox.delete("1.0", END)
            except:
                pass
            textBox.insert(END, text[-1])

            # displaying picture
            image_url="http://cs.sehir.edu.tr"
            urls=[]
            for i in self.soup.find_all(class_ ="list-group-item"):
                if i.find_next(id=listProject.get(listProject.curselection())) != None:
                    urls.append(i.find_next(class_="img-responsive img-thumbnail small-gap").get("src"))
            image_url += urls[-1]

            image_bytes = urlopen(image_url).read()
            data_stream = io.BytesIO(image_bytes)
            pil_image = Image.open(data_stream)
            pil_image=pil_image.resize((650,300),Image.BICUBIC)
            self.tk_image = ImageTk.PhotoImage(pil_image)

            canvas.create_image(10, 10, image=self.tk_image, anchor=NW)

        self.grid()
        frame1 = Frame(self)
        frame1.grid(row=0,column=0)
        Label(frame1, text="SEHIR Research Projects Analyzer - CS Edition",  bg="blue", fg="white", font="-weight bold").grid(columnspan=5, row=0, column=0, sticky=EW)
        Label(frame1, text="Please provide a url:").grid(row=1, column=0, sticky=E)
        url = Entry(frame1, bg="yellow", width=40)
        url.grid(sticky=E, row=2,column=0, pady=10, padx=10)
        url.insert(END, "http://cs.sehir.edu.tr/en/research/")
        Label(frame1, text="'"*400).grid(row=3,column=0, columnspan=5)

        fetch = Button(frame1, text="Fetch Research Projects")
        fetch.grid(row=2, column=2, pady=10)

        frame2 = Frame(self)
        frame2.grid(row=1, column=0)
        Label(frame2, text="Filter Research Projects By:").grid(row=0, column=1)
        Label(frame2, text="Pick a Project:").grid(row=0,column=3)
        Label(frame2, text="Year:", fg="blue").grid(row=1, column=1)
        Label(frame2, text="Principal Investigator:", fg="blue").grid(row=2, column=1)
        Label(frame2, text="Funding Instution:", fg="blue").grid(row=3, column=1)

        yearChoice = StringVar()
        years = ttk.Combobox(frame2, text="All Years", textvariable=yearChoice)
        years.grid(row=1, column=2, padx=20)

        principalChoice = StringVar()
        principal = ttk.Combobox(frame2, text="All Investigators", textvariable=principalChoice)
        principal.grid(row=2, column=2, padx=20)

        fundingChoice = StringVar()
        funding = ttk.Combobox(frame2, text="All Institutions", textvariable=fundingChoice,)
        funding.grid(row=3, column=2, padx=20)

        scrollProject = Scrollbar(frame2)
        scrollProject.grid(row=1, column=4, sticky=W+NS, rowspan=3)
        listProject = Listbox(frame2, yscrollcommand=scrollProject.set, height=6, width=80)
        listProject.grid(row=1, column=3, rowspan=3, sticky=E)
        scrollProject.config(command=listProject .yview)

        displayTitle = Button(frame2, text="Display Project Titles")
        displayTitle.grid(row=4, column=2)

        showDesc = Button(frame2, text="Show Description")
        showDesc.grid(row=4, column=3)

        Label(frame2, text="'"*400).grid(row=5,column=0, columnspan=5)

        frame3 = Frame(self)
        frame3.grid(row=3, column=0)
        Label(frame3, text="Project Description:").grid(row=0, column=2, sticky=W)

        scrollCanvasX = Scrollbar(frame3, orient=HORIZONTAL)
        scrollCanvasX .grid(row=2,column=0, sticky=N+EW)
        scrollCanvasY = Scrollbar(frame3, orient=VERTICAL)
        scrollCanvasY .grid(row=1,column=1, sticky=W+NS)
        canvas = Canvas(frame3, bg="white", width=650, height=300)
        canvas.grid(row=1, column=0, sticky=EW+NS)
        scrollCanvasY.config(command=canvas.yview)
        scrollCanvasX.config(command=canvas.xview)

        scrollText= Scrollbar(frame3)
        textBox = Text(frame3, height=20, width=60, yscrollcommand=scrollText.set, fg="blue")
        scrollText.grid(row=1, column=3, sticky=W+NS, rowspan=2)
        textBox.grid(row=1, column=2, rowspan=2)
        scrollText.config(command=textBox.yview)

        fetch.bind("<Button-1>", get_html)
        displayTitle.bind("<Button-1>", listFill)
        showDesc.bind("<Button-1>", showDescpription)

    def comboYear(self):
        years=[]
        for i in self.soup.find_all(class_  = "list-group-item"):
            yearString = i.find_next('p').string
            years.append(yearString.encode("utf-8").split()[2])
            years.append(yearString.encode("utf-8").split()[6])
        years.sort()
        maxYear=years[len(years)-1]
        minYear=years[0]
        listYears=["All Years"]
        for i in range(int(minYear), int(maxYear)+1):
            listYears.append(i)
        return listYears

    def comboPrincipal(self):
        principal=[]
        for i in self.soup.find_all(class_  = "list-group-item"):
            principalStr = i.find_all("p")
            for j in principalStr[2].find_all("a"):
                if j.encode("utf-8").strip().split()[2]+" "+j.encode("utf-8").strip().split()[3] not in principal:
                    principal.append(j.encode("utf-8").strip().split()[2]+" "+j.encode("utf-8").strip().split()[3])
        # sorting by last name
        pt = []
        for i in principal:
            pt.append((i.split()[1], i.split()[0]))
        pt.sort()
        principal= [i[1]+" "+i[0] for i in pt]
        principal.insert(0,"All Investigators")
        return principal

    def comboFunding(self):
        institutions=["All Institutions"]
        for i in self.soup.find_all(class_  = "list-group-item"):
            institutionsStr = i.find_all("p")
            for j in institutionsStr[1]:
                if "<" not in j.encode("utf-8").strip() and "" != j.encode("utf-8").strip() and j.encode("utf-8").strip() not in institutions:
                    institutions.append(j.encode("utf-8").strip())
        institutions.sort()
        return institutions

def main():
    root = Tk()
    root.title("Course Analyzer - Sehir Limited Edition")
    root.resizable(width=FALSE, height=FALSE)
    app = GUI(root)
    root.mainloop()

main()