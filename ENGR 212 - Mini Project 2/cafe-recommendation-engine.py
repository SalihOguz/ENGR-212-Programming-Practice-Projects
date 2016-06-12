__author__ = 'mustafa salih oguz'
from Tkinter import *
from xlrd import *
from recommendations import *
import anydbm, ttk, tkMessageBox, pickle

class GUI(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.recNo = 10
        self.based=""
        self.similarity=""
        self.ratings={"User":{}}
        self.UI()

    def UI(self):
        def addRated(event):
            """Runs when clicked on add button. Adds chosen meal to listbox and database"""
            db = anydbm.open("ownratings.db", "c")
            db[choice.get().encode("utf-8")] = str(slide.get())  # adding the chosen meal and point to db as "meal":"point"
            topBox.delete(0, END)  # clean listbox to prevent writing values again and again
            for i in db:  # adding meals to the listbox
                topBox.insert(END,  i+" --> "+db[i])

        def removeRated(event):
            """Runs when clicked on remove button. Removes chosen meal from listbox and database"""
            try:
                db = anydbm.open("ownratings.db", "w")
                del db[topBox.get(topBox.curselection(), last=None).split(" --> ")[0].encode("utf-8")]  #deleting chosen one
                topBox.delete(0, END)  #updating listbox
                for i in db:
                    topBox.insert(END,  i+" --> "+db[i])
            except:
                pass

        def listUpdate():
            """used when program started in order to take rated meal's data from db and show on the listbox"""
            try:
                db = anydbm.open("ownratings.db", "r")
                for i in db:
                    topBox.insert(END,  i+" --> "+db[i])  # adding values to the listbox
            except:
                pass

        def getRecommendation(event):
            """takes the parameters from entry and radiobutton in order to make recommendation.
            Then fills 2 listboxes that are related with recommendations which are left and middle listboxes"""
            #getting recommendation number from entry
            try:
                self.recNo = int(number.get())
            except:
                tkMessageBox.showinfo("Number of Recommendations Error", "You need to write a number into the text box")
                return

            #getting data from radiobuttons
            self.based = based.get()
            self.similarity = similarity.get()

            #Chaning label's texts according to the radiobutton choices
            if self.based == "user":
                secondBoxLabel.config(text="Users similar to you")
                thirdBoxLabel.config(text="User ratings (select a user on the left)")
            else:
                secondBoxLabel.config(text="Your ratings")
                thirdBoxLabel.config(text="Similar items (select an entree on the left)")

            #getting ratings into a better position for recommendations
            try:
                db = anydbm.open("ownratings.db","r")
            except:
                tkMessageBox.showinfo("Database Error", "You need to rate and add some meals to your list")
                return
            for i in db:
                self.ratings["User"][i]=int(db[i])
            db.close()

            #taking data from ccratings database and make up a dictionary with user's ratings previously added
            db = anydbm.open("cc_ratings.db","r")
            for key, value in db.items():
                self.ratings[key]=pickle.loads(db[key])

            similarityDict={"sim_distance":sim_distance,"sim_jaccard":sim_jaccard,"sim_pearson":sim_pearson}  # to make code shorter

            # FILLING LEFT AND MIDDLE LISTBOXES
            leftBox.delete(0, END)  # cleaning the listbox for new data
            middleBox.delete(0, END)
            rightBox.delete(0, END)

            # middle listbox in third part
            if self.based == "user":  # user based recommendation. Similar users
                middleBoxs = topMatches(self.ratings,"User",5,similarityDict[similarity.get()])
                for i in middleBoxs:
                    middleBox.insert(END, "%.2f - %s" % ((i[0]),i[1]))
            else:  # item based recommendation. Rated items
                for i in topBox.get(0, END):  # copying the data in the listbox at top to the middle listbox
                    middleBox.insert(END, i)

            # result box = left listbox
            recData = getRecommendations(self.ratings, "User", similarityDict[similarity.get()])  # getting recommendations
            leftBox.insert(END,"Similarity Score --> Recommendation")
            count=0
            for i in recData:  # adding recommendations to the left listbox
                count+=1
                if count > int(number.get()):
                    break
                leftBox.insert(END, "%.2f --> %s" % (i[0], i[1]))

        def showSelectedRatings(event):
            """Shows the ratings of selected user or item from the middle listbox to the right listbox"""
            rightBox.delete(0, END)  # cleaning the middle box for update
            try:
                if self.based == "user":  # user based right box
                    selectedUser = middleBox.get(middleBox.curselection(), last=None).split(" - ")[1]  # getting the selected user
                    rightBox.insert(END, "%s also rated the following\n" % selectedUser)  # printing the header
                    selectedRates=[]  #getting and sorting the rates
                    for key, value in self.ratings[selectedUser].items():
                        selectedRates.append((value, key))
                    selectedRates.sort(reverse=True)
                    for i in selectedRates:  # inserting rates to the right listbox
                        rightBox.insert(END, "%s --> %d" % (i[1], i[0]))

                else:  # item based right box
                    selectedItem = middleBox.get(middleBox.curselection(), last=None).split(" --> ")[0]  # getting chosen item from listbox
                    similarList=[]
                    for i in calculateSimilarItems(self.ratings)[selectedItem.encode("utf-8")]:  # finding similar items and rates
                        similarList.append((i[0],i[1]))
                    similarList.sort(reverse=True)  # sorting similar items
                    rightBox.insert(END,"Similarity Score --> Recommendation")
                    for i in similarList:  # inserting rates to the right listbox
                        rightBox.insert(END, "%.2f --> %s" % (i[0],i[1]))
            except:
                pass

        self.grid()
        frame1 = Frame(self)
        frame1.grid(row=0, column=0)
        frame2 = Frame(self)
        frame2.grid(row=1, column=0)
        frame3 = Frame(self)
        frame3.grid(row=2, column=0)
        Label(frame1, text="Cafe Crown Recommendation Engine - SEHIR Special Edition", bg="black", fg="yellow", font="-weight bold", height=2).grid(row=0, column=0, columnspan=6, sticky=EW)
        Label(frame1, text="Welcome!\nPlease rate entries that you have had at CC, and we will recommend you what you may like to have!", font="26").grid(row=1, column=0, columnspan=6, sticky=EW)
        Label(frame1, text='"'*150).grid(row=2, column=0, columnspan=6, sticky=EW)
        Label(frame1, text="Choose a meal:", fg="maroon").grid(row=3, column=0)
        Label(frame1, text="Enter your rating:", fg="maroon").grid(row=3, column=1)

        scrollTop = Scrollbar(frame1)
        scrollTop.grid(row=3, column=4, sticky=W+NS,rowspan=2)
        topBox = Listbox(frame1, height=5, width="35")
        topBox.grid(row=3, column=3, sticky=EW, rowspan=2)
        scrollTop.config(command=topBox.yview)

        listUpdate()

        #MENU
        choice = StringVar()
        comboBox = ttk.Combobox(frame1, width=25, textvariable=choice, values=self.readMenu(), state='readonly')
        comboBox.current(0)
        comboBox.grid(row=4, column=0, sticky=W, padx=15)

        slide = Scale(frame1, from_=1, to=10, orient=HORIZONTAL)
        slide.grid(row=4, column=1, sticky=W)

        remove = Button(frame1, text="Remove\nSelected", fg="red", width=10)
        remove.grid(row=4, column=5, padx=15)

        add = Button(frame1, text="Add", fg="blue", width=10)
        add.grid(row=4, column=2, padx=15)

        add.bind("<Button-1>", addRated)
        remove.bind("<Button-1>", removeRated)

        Label(frame2, text='"'*150).grid(row=0,column=0, columnspan=6, sticky=EW)
        Label(frame2, text='Get Recommendations', font="-weight bold").grid(row=1,column=0, columnspan=6, sticky=EW)
        Label(frame2, text='"'*150).grid(row=2,column=0, columnspan=6, sticky=EW)
        Label(frame2, text="Settings:", fg="maroon", font="-weight bold").grid(row=3, column=0,sticky=W, padx=5)
        Label(frame2, text="Number of recommendations:").grid(row=4, column=0, sticky=W, padx=5)
        Label(frame2, text="Choose recommendation method", fg="purple").grid(row=4, column=2, sticky=W, padx=30)
        Label(frame2, text="Choose similarity metric", fg="purple").grid(row=7, column=2, sticky=W, padx=30)

        number = Entry(frame2, width=5)
        number.insert(END, "10")
        number.grid(row=4, column=1, sticky=W)

        #RADIBUTTONS
        based = StringVar()
        based.set("user")
        Radiobutton(frame2, text="user based", variable=based, value="user").grid(row=5, column=2, sticky=W, padx=30)
        Radiobutton(frame2, text="item based", variable=based, value="item").grid(row=6, column=2, sticky=W, padx=30)

        similarity = StringVar()
        similarity.set("sim_distance")
        Radiobutton(frame2, text="Euclidean Score", variable=similarity, value="sim_distance").grid(row=8, column=2, sticky=W, padx=30)
        Radiobutton(frame2, text="Pearson Score", variable=similarity, value="sim_pearson").grid(row=9, column=2, sticky=W, padx=30)
        Radiobutton(frame2, text="Jaccard Score", variable=similarity, value="sim_jaccard").grid(row=10, column=2, sticky=W, padx=30)

        recommend = Button(frame2, text="Get Recommendation", fg="blue")
        recommend.grid(row=9, column=3)

        recommend.bind("<Button-1>", getRecommendation)

        Label(frame3, text='"'*150).grid(row=0,column=0, columnspan=6, sticky=EW)
        Label(frame3, text="Result Box (Recommendations):").grid(row=1, column=0, sticky=W, padx=5)
        secondBoxLabel = Label(frame3, text="Users similar you", bg="purple", fg="white")
        secondBoxLabel.grid(row=3, column=2, sticky=EW+N, padx=5)
        thirdBoxLabel = Label(frame3, text="User ratings (select a user on the left)", bg="maroon", fg="white")
        thirdBoxLabel.grid(row=3, column=3, sticky=EW+N, padx=5)

        scrollLeft = Scrollbar(frame3)
        scrollLeft .grid(row=3,column=1, sticky=W+NS, rowspan=2)
        leftBox = Listbox(frame3, yscrollcommand=scrollLeft.set, height=6, width=35)
        leftBox .grid(row=3, column=0, sticky=EW, rowspan=2, padx=5)
        scrollLeft .config(command=leftBox .yview)

        middleBox = Listbox(frame3, height=5, width=25)
        middleBox .grid(row=4, column=2, sticky=EW, padx=5)

        scrollRight = Scrollbar(frame3)
        scrollRight .grid(row=4,column=4, sticky=W+NS)
        rightBox = Listbox(frame3, yscrollcommand=scrollRight .set, height=5, width=35)
        rightBox .grid(row=4, column=3, sticky=EW, padx=5)
        scrollRight .config(command=rightBox .yview)

        middleBox.bind("<<ListboxSelect>>", showSelectedRatings)

    def readMenu(self):
        """takes data from Menu.xlsx and fill the combobox with meals"""
        menu=()
        book = open_workbook("Menu.xlsx")
        sheet = book.sheet_by_index(0)
        for row_index in range(1,sheet.nrows):
            menu += sheet.cell(row_index, 0).value.encode('utf-8'),
        return menu

def main():
    root = Tk()
    root.title("Cafe Crown Recommendation Engine")
    root.resizable(width=FALSE, height=FALSE)
    app = GUI(root)
    root.mainloop()

main()