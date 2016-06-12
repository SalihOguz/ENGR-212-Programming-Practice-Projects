__author__ = "mustafa salih oguz"
from Tkinter import *
from bs4 import BeautifulSoup
import shelve, tkMessageBox, urllib2, time

class GUI(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.db = shelve.open("data.db", writeback=True, flag="c")
        self.ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', 'on'])
        self.splitter = re.compile('\\W*')
        self.result=[]  # keeps publications to wrtie text widget
        self.UI()

    def UI(self):
        def buildIndex(event):
            """runs when clicked to 'build index' button. Takes professors page from given url. Then takes
            all publications and their citation numbers, counts every word in it and forms a database.
            Takes publication type and fills listbox with all types"""
            response = urllib2.urlopen(entry_url.get())
            self.html = response.read()
            self.soup = BeautifulSoup(self.html, 'html.parser')
            publication_types=[]
            # searches for professors' page in given url
            for i in self.soup.find_all(class_ ="col-sm-4 small-gap"):
                # getting professors' page
                response2 = urllib2.urlopen("http://cs.sehir.edu.tr/"+i.find_next('a').get("href"))
                html2 = response2.read()
                soup2 = BeautifulSoup(html2, 'html.parser')

                # finding publications in professors page
                for j in soup2.find_all(id="publication"):
                    list_of_numbers=[]  # holds how many publication written from every type of publication
                    for c in j.find_all("ul"):
                        count=0
                        for l in c.find_all("li"):
                           count+=1
                        list_of_numbers.append(count)

                    pub_types = [i[5:].strip() for i in str(j.find_all("p")).split("</p>") if i[5:]!=""]  # getting all publication types in this professors publications

                    pub_type_and_no =()  # combining publication types and how many publication in that type
                    for item in range(len(list_of_numbers)):
                        pub_type_and_no+=(pub_types[item], list_of_numbers[item]),


                    for pub_name, no in pub_type_and_no:  # getting unique publication types list for listbox
                        if pub_name not in publication_types:
                            publication_types.append(pub_name)

                    count=0
                    get=0
                    for p in j.find_all("li"):
                        # getting publication name and citation count and saving it to database
                        li = str(p)
                        pub_name = li.strip().split("\n")[2]  # publication name
                        cit_no = li.strip().split("\n")[5][3:]  # citation count
                        if cit_no.isalnum():
                            self.db[pub_name] = {"citation_count":int(cit_no)}  # saving to database
                        else:
                            self.db[pub_name] = {"citation_count":0}


                        # getting words and counts in publication name for word frequency and saving it to database
                        for word in pub_name.split():  #
                            word_to_add = [s.lower() for s in self.splitter.split(word) if s != '']
                            # counting adding all words in database for current publication
                            for single in word_to_add:
                                if single not in self.ignorewords and len(single)>1:
                                    if single in self.db[pub_name]:
                                        self.db[pub_name][single]+=1
                                    else:
                                        self.db[pub_name][single]=1

                        # getting publication type of current publication
                        self.db[pub_name]["publication_type"]=pub_type_and_no[get][0]
                        count+=1
                        if count == pub_type_and_no[get][1]:
                            get+=1
                            count=0

            # filling filter papers listbox
            publication_types.sort()
            listFilter.delete(0, END)
            for i in publication_types:
                listFilter.insert(END, i)
            listFilter.select_set(0, END)

        def search(event):
            """getting keywords, ranking criteria, weight, filter paper. Filters all publications with these criterias.
             Then searches"""
            # error situations
            if len(entry_search.get())==0:
                tkMessageBox.showinfo("Keyword Error", "Write at least one keyword to start searching")
                return
            if listFilter.curselection() == ():
                tkMessageBox.showinfo("Paper Category Error", "Choose at least one paper category to start searching")
                return
            if citCon.get()==0 and wordFreq.get()==0:
                tkMessageBox.showinfo("Ranking Criteria Error", "Choose at least one criteria to start searching")
                return
            if (citCon.get()==1  and wordFreq.get()==1) and (entry_freq_weight=="" or entry_cit_weight==""):
               if (citCon.get()==1  and wordFreq.get()==1) and (entry_freq_weight=="" or entry_cit_weight==""):
                tkMessageBox.showinfo("Ranking Criteria Error", "Enter weights for chosen criteria to start searching")
                return

            start_time = time.time()
            self.keywords = [s.lower() for s in self.splitter.split(entry_search.get()) if s != '']  # getting all keywords

            # getting publication types to filter
            selected_from_list=[]
            for i in listFilter.curselection():
                selected_from_list.append(listFilter.get(i))

            results=[]  # will be filtered publications
            for i in self.db:
                words = [s.lower() for s in self.splitter.split(i) if s != '']
                if self.db[i]["publication_type"] not in selected_from_list:  # filtering for publication type
                    continue

                have_any_keyword=False
                for j in self.keywords: # filtering for keywords and saving keywords to results dictionary
                    if j in words:
                        have_any_keyword=True
                        results.append(i)
                        break
                if not have_any_keyword:
                    continue

            if results==[]:  # if no suitable result found for given keywords
                    tkMessageBox.showinfo("No Publication Found", "Try other keywords to start searching")
                    return

            resultsWords = {}
            if wordFreq.get()==1:  # if word frequency  criteria is chosen frequency score calculated
                for i in results:
                    words = [s.lower() for s in self.splitter.split(i) if s != '']
                    resultsWords[i]={}
                    for j in self.keywords:
                        if j in words:
                            resultsWords[i][j] = int(self.db[i][j])
                resultsWords = self.score(resultsWords)

            resultsCitation={}
            if citCon.get()==1:  # if citation count criteria is chosen citation score calculated
                for i in results:
                    resultsCitation[i]={"cit": int(self.db[i]["citation_count"])}
                resultsCitation = self.score(resultsCitation)

            resultFinal={}  # calculating final score by summing at most two kind of score according to criteria
            for i in results:
                resultFinal[i]=0
                if wordFreq.get()==1:
                    resultFinal[i]+= resultsWords[i]*int(entry_freq_weight.get())
                if citCon.get()==1:
                    resultFinal[i]+= resultsCitation[i]*int(entry_cit_weight.get())
            resultFinal = self.normalizescores(resultFinal)

            elapsed_time = time.time() - start_time  # calculating time

            self.label_page_no.config(text=str("1"))
            self.button_next.config(state=NORMAL)
            self.button_prev.config(state=DISABLED)
            self.get_what_to_print(resultFinal, elapsed_time)  # to show result on text widget

        def nextPage(event):
            """next page button event. if there are more publications gets them and shows on the text widget"""
            if self.button_next.cget("state")=="disabled":
                return
            page = self.label_page_no.cget("text")
            self.label_page_no.config(text=str(int(page)+1))  # increasing page no

            self.printOut()  # changing the text on the text widget

            self.button_prev.config(state=NORMAL)
            if len(self.result)<=int(self.label_page_no.cget("text"))*10:
                self.button_next.config(state=DISABLED)

        def prevPage(event):
            """previous button event. if there are more publications behind gets them and shows on the text widget"""
            if self.button_prev.cget("state")=="disabled":
                return
            page = self.label_page_no.cget("text")
            self.label_page_no.config(text=str(int(page)-1))  # decreasing page no

            self.printOut()  # changing the text on the text widget

            self.button_next.config(state=NORMAL)
            if int(self.label_page_no.cget("text"))==1:
                self.button_prev.config(state=DISABLED)

        self.grid();
        frame1 = Frame(self)
        frame1.grid(row=0, column=0)
        Label(frame1, text="SEHIR Scholar", bg="blue", fg="white", width=120, height=2).grid(row=0, column=0, columnspan=5, sticky=EW)
        Label(frame1, text="Url for faculty list:").grid(row=1, column=0)

        entry_url = Entry(frame1, width=50)
        entry_url.grid(row=1, column=1, columnspan=3, pady=10)
        entry_url.insert(END, "http://cs.sehir.edu.tr/en/people/")

        button_index = Button(frame1, text="Build Index")
        button_index.grid(row=1, column=4, sticky=W, pady=10)

        entry_search = Entry(frame1, width = 70, font="-weight bold")
        entry_search.grid(row=2, column=0, columnspan=5, pady=10)

        Label(frame1, text="Ranking Critera").grid(row=3, column=1, sticky=W)
        Label(frame1, text="Weight").grid(row=3, column=2)
        Label(frame1, text="Filter Papers").grid(row=3, column=3)

        wordFreq= IntVar()
        check_word = Checkbutton(frame1, text="Word Frequency", variable=wordFreq)
        check_word.grid(row=4, column=1, sticky=W)

        citCon= IntVar()
        check_citation = Checkbutton(frame1, text="Citation Count", variable=citCon)
        check_citation.grid(row=5, column=1, sticky=W)

        scrollFilter = Scrollbar(frame1,  orient=HORIZONTAL)
        scrollFilter.grid(row=6, column=3, sticky=EW+N)
        listFilter = Listbox(frame1, xscrollcommand=scrollFilter.set, height=6, selectmode=MULTIPLE)
        listFilter.grid(row=4, column=3, sticky=EW, rowspan=2)
        scrollFilter.config(command=listFilter.xview)


        entry_freq_weight = Entry(frame1, width=5)
        entry_freq_weight.grid(row=4, column=2)
        entry_freq_weight.insert(END,"1")

        entry_cit_weight = Entry(frame1, width=5)
        entry_cit_weight.grid(row=5, column=2)
        entry_cit_weight.insert(END,"1")

        button_search= Button(frame1, text="Search")
        button_search.grid(row=4, column=4)

        self.label_public = Label(frame1, text= "0 Publications (0.0 seconds)", fg="red", font="-weight bold")
        self.label_public.grid(row=7, column=0, sticky=E)

        scrollText= Scrollbar(frame1)
        self.textBox = Text(frame1, height=15, width=80, yscrollcommand=scrollText.set)
        scrollText.grid(row=8, column=4, sticky=W+NS, rowspan=2)
        self.textBox.grid(row=8, column=0, rowspan=2, columnspan=4, sticky=E)
        scrollText.config(command=self.textBox.yview)

        frame2 = Frame(self)
        frame2.grid(row=1, column=0)

        Label(frame2, text="Page:", font="-weight bold").grid(row=0, column=1, sticky=E)

        self.button_prev = Button(frame2, text="Previous", state=DISABLED)
        self.button_prev.grid(row=0, column=2, sticky=E, padx=10)

        self.label_page_no = Label(frame2, text="1", bg="blue", fg="white", font="-weight bold")
        self.label_page_no.grid(row=0, column=3)

        self.button_next = Button(frame2, text="Next")
        self.button_next.grid(row=0, column=4, sticky=E, padx=10)

        button_index.bind("<Button-1>", buildIndex)
        button_search.bind("<Button-1>", search)
        self.button_next.bind("<Button-1>", nextPage)
        self.button_prev.bind("<Button-1>", prevPage)

    def normalizescores(self,scores):
        """divides all score by the highest score to make them smaller than 1 and normalize it"""
        maxscore = max(scores.values())
        return dict([(pub_name,float(score)/maxscore) for (pub_name,score) in scores.items()])

    def score(self, results): # results = {pub_name:{word1=1, word2=2}}
        """calculates score by multiplying all repeated keywords"""
        counts = {}
        for pub_name in results:
            score = 1
            for words in results[pub_name]:
                score *= results[pub_name][words]  # score of results = 1 * 2
            counts[pub_name] = score  # counts = {pub_name:2}
        return self.normalizescores(counts)

    def get_what_to_print(self, dict, time):
        """takes search results, sorts and form text that is going to be on text widget"""
        # sorting what to write
        resultSort = []
        for key, value in dict.items():
            resultSort.append((value,key))
        resultSort.sort(reverse=True)

        self.result=[]
        count=1
        for value, key in resultSort:  # taking sorted list of publication name and scores then make them presentable
            self.result.append("%s.    %s [%s Citations] %.4f\n" % (str(count), key, self.db[key]["citation_count"], float(value)))
            count+=1

        self.label_public.config(text= "%d Publications (%.3f seconds)" % (len(self.result), time))  # writing publication count and time passed

        if len(self.result)<10:  # disabling next page button if there is no record to show
            self.button_next.config(state=DISABLED)
        self.printOut()  # printing the information formed above

    def printOut(self):
        """printing and updating search results in text widget. Called after searching and changing page"""
        try:
            self.textBox.delete("1.0", END)
        except:
            pass
        self.written=1  # record no in a page. Will not exceed 10
        publication_no=int(self.label_page_no.cget("text"))*10-9  # calculating starting number of record according to page no
        for i in self.result[publication_no-1:publication_no+9]:  # writing one page of records to the text widget
            # coloring score in search results
            self.textBox.insert(END, i)
            self.textBox.tag_add("score", "%d.%d" % (self.written, len(i)-8), "%d.%d" % (self.written, len(i)-1))
            self.textBox.tag_config("score", foreground="red")

            # finding places of keywords in current text
            keyword_places=[]
            for k in self.keywords:
                for m in re.finditer(k, i.lower()):
                    keyword_places.append("%d-%d" % (m.start()-1, m.end()))

            # coloring keywords in search results
            for j in keyword_places:
                self.textBox.tag_add("keyword", "%d.%s" % (self.written, j.split("-")[0]), "%d.%s" % (self.written, j.split("-")[1]))
                self.textBox.tag_config("keyword", foreground="blue", font="-weight bold")
            self.written+=1

if __name__ == "__main__":
    root = Tk()
    root.title("SEHIR Scholar")
    root.resizable(width=FALSE, height=FALSE)
    app = GUI(root)
    root.mainloop()