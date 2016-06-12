__author__ = "mustafa salih oguz"
from Tkinter import *
from PIL import Image, ImageTk
from tkColorChooser import askcolor
import random

class GUI(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.drawWhat="rec"
        self.state = "drawing"
        self.fillColor = "blue"
        self.borderColor = "light blue"
        self.shapes = {} # = {1:(startx,stary,endx,endy)
        self.shapeCount=1
        self.overlap = 9999
        self.UI()

    def UI(self):
        def oval(event):
            """pressing oval button. changes what to draw, useage state, cursor and label's relief"""
            self.drawWhat="oval"
            self.state="drawing"
            self.reliefConfig(button_oval)
            self.canvas.config(cursor="plus")
        def line(event):
            """pressing line button. changes what to draw, useage state, cursor and label's relief"""
            self.drawWhat="line"
            self.state="drawing"
            self.reliefConfig(button_line)
            self.canvas.config(cursor="plus")
        def rec(event):
            """pressing rectangle button. changes what to draw, useage state, cursor and label's relief"""
            self.drawWhat="rec"
            self.state="drawing"
            self.reliefConfig(button_rec)
            self.canvas.config(cursor="plus")
        def drag(event):
            """pressing drag button. changes useage state, cursor and label's relief"""
            self.state="dragging"
            self.reliefConfig(button_drag)
            self.canvas.config(cursor="hand2")
        def erase(event):
            """pressing erase button. changes useage state, cursor and label's relief"""
            self.state="erasing"
            self.reliefConfig(button_eraser)
            self.canvas.config(cursor="X_cursor")

        self.grid()
        frame1 = Frame(self)
        frame1.grid(row=0, column=0)
        Label(frame1, text="My Paint", bg="orange", height=2, fg="white").grid(row=0, column=0, columnspan=13, sticky=EW)

        image = Image.open("assets/rectangle.png")
        photo_rec = ImageTk.PhotoImage(image)

        image = Image.open("assets/oval.png")
        photo_oval = ImageTk.PhotoImage(image)

        image = Image.open("assets/line.png")
        photo_line = ImageTk.PhotoImage(image)

        image = Image.open("assets/drag.png")
        photo_drag = ImageTk.PhotoImage(image)

        image = Image.open("assets/eraser.png")
        photo_eraser = ImageTk.PhotoImage(image)

        button_rec = Label(frame1, image=photo_rec, relief=SUNKEN)
        button_rec.image=photo_rec
        button_rec.grid(row=1, column=0)

        button_oval = Label(frame1, image=photo_oval, relief=RAISED)
        button_oval.image=photo_oval
        button_oval.grid(row=1, column=1)

        button_line = Label(frame1, image=photo_line, relief=RAISED)
        button_line.image = photo_line
        button_line.grid(row=1, column=2)

        button_eraser = Label(frame1, image=photo_eraser, relief=RAISED)
        button_eraser.image=photo_eraser
        button_eraser.grid(row=1, column=4)

        button_drag = Label(frame1, image=photo_drag, relief=RAISED)
        button_drag.image=photo_drag
        button_drag.grid(row=1, column=3)

        self.buttons = [button_rec, button_oval, button_eraser, button_drag, button_line]

        Label(frame1, text="Fill Color:").grid(row=1, column=5)

        self.label_fill_color = Label(frame1, text="       ", bg=self.fillColor)
        self.label_fill_color.grid(row=1, column=6)

        Label(frame1, text="Border Color:").grid(row=1, column=7)

        self.label_border_color = Label(frame1, text="       ", bg=self.borderColor)
        self.label_border_color.grid(row=1, column=8)

        Label(frame1, text="Weight:").grid(row=1, column=9)

        self.spin_weight = Spinbox(frame1, from_=0, to=100, width=6)
        self.spin_weight.grid(row=1, column=10)

        button_beutiful = Button(frame1, text="Beautiful Layout")
        button_beutiful.grid(row=1, column=11)

        self.label_overlap = Label(frame1, text="Overlapping Count")
        self.label_overlap.grid(row=1, column=12)

        self.canvas = Canvas(frame1, height=500, width=800, bg="white", cursor="plus")
        self.canvas.grid(row=2, column=0, columnspan=13, sticky=EW+NW)

        self.canvasCreateShape={"oval":self.canvas.create_oval, "rec":self.canvas.create_rectangle, "line":self.canvas.create_line}

        button_rec.bind("<Button-1>", rec)
        button_oval.bind("<Button-1>", oval)
        button_line.bind("<Button-1>", line)
        button_drag.bind("<Button-1>", drag)
        button_eraser.bind("<Button-1>",erase)
        button_beutiful.bind("<Button-1>", self.beautifulLayout)

        self.label_fill_color.bind('<ButtonPress-1>', self.getFillColor)
        self.label_border_color.bind('<ButtonPress-1>', self.getBorderColor)

        self.canvas.bind('<ButtonPress-1>', self.drawStart)
        self.canvas.bind('<B1-Motion>', self.drawShape)
        self.canvas.bind('<ButtonRelease-1>', self.drawEnd)

    def reliefConfig(self, chosen):
        """makes all of the labels' relief sunken except the one that is clicked"""
        for i in self.buttons:
            if i != chosen:
                i.config(relief=RAISED)
            else:
                i.config(relief=SUNKEN)

    def drawStart(self, event):
        """runs when clicked to the canvas and works if current state is drawing. creates the shape"""
        if self.state != "drawing":
            return
        self.startx, self.starty = event.x, event.y
        if self.drawWhat != "line":  #creating desired shape
            item = self.canvasCreateShape[self.drawWhat](self.startx, self.starty, event.x, event.y, fill=self.fillColor, width=int(self.spin_weight.get()), outline=self.borderColor, tag=str(self.shapeCount))
        else:
            item = self.canvasCreateShape[self.drawWhat](self.startx, self.starty, event.x, event.y, fill=self.fillColor, width=int(self.spin_weight.get()), tag=str(self.shapeCount))

        self.canvas.tag_bind(item, '<ButtonPress-1>', self.dragOrDelete)
        self.canvas.tag_bind(item, '<B1-Motion>', self.dragShape)
        self.canvas.tag_bind(item, '<ButtonRelease-1>', self.dragEnd)

        self.shape = item

    def drawShape(self, event):
        """runs when mouse moved while button 1 clicked and extends created shape"""
        if self.state == "drawing":
            self.canvas.coords(self.shape, self.startx, self.starty, event.x, event.y)  # extends shape by updating event.x while startx stays same

    def drawEnd(self, event):
        """runs when mouse button 1 released and saves drawn shape to self.shapes"""
        if self.state == "drawing":
            self.shapes[self.shapeCount]=[self.startx, self.starty, event.x, event.y]  # saves shape with coordinates of two corners
            self.shapeCount += 1

    def dragOrDelete(self, event):
        """when clicked on a shape, decides wheter delete it or drag it"""
        if self.state == "erasing":
            self.eraseItem(event)
        elif self.state == "dragging":
            self.dragStart(event)

    def dragStart(self, event):
        """Selects this item for dragging."""
        self.dragx, self.dragy = event.x, event.y
        self.dragitem = self.canvas.find_closest(event.x, event.y)  # find shape to drag
        self.startx, self.starty = event.x, event.y

    def dragShape(self, event):
        """Move this item using the pixel coordinates in the event object."""
        # see how far we have moved
        if self.state != "dragging":
            return
        dx = event.x - self.dragx
        dy = event.y - self.dragy
        self.canvas.move(self.dragitem, dx, dy)  # calculate the movement and move the shape while mouse moves
        self.dragx, self.dragy = event.x, event.y

    def dragEnd(self, event):
        """updates current coordinates of draged item in self.shapes"""
        self.dragitem = self.canvas.find_closest(event.x, event.y)
        self.shapes[self.dragitem[0]]=[self.startx, self.starty, event.x, event.y]  # updating shapes coordinates

    def eraseItem(self, event):
        """deletes clicked shape"""
        deleted = self.canvas.find_closest(event.x, event.y)
        self.canvas.delete(self.canvas.find_closest(event.x, event.y))  # deleting chosen shape
        del self.shapes[deleted[0]]

    def getFillColor(self, event):
        """user choose fill color of shape when clicked to color option"""
        color = askcolor()
        self.label_fill_color.config(bg=color[1])  # changing color and color label's color
        self.fillColor = color[1]

    def getBorderColor(self, event):
        """user choose border color of shape when clicked to color option"""
        color = askcolor()
        self.label_border_color.config(bg=color[1])  # changing color and color label's color
        self.borderColor = color[1]

    def overlapCount(self, shapes):
        """counts how many overlaps are there in the canvas or would be if optimized in a certain way"""
        overlap = 0
        taken = []
        for i in shapes.keys():
            # getting x and y coordinates of the shape
            istartx = shapes[i][0]
            istarty = shapes[i][1]
            iendx = shapes[i][2]
            iendy = shapes[i][3]

            # checking if the drawing the shape started from bottom to top
            if istartx > iendx and istarty > iendy:
                istartx, istarty, iendx, iendy = iendx, iendy, istartx, istarty

            all = self.canvas.find_overlapping(istartx, istarty, iendx, iendy)  # all overlaps

            for j in all:
                if i!=j and (i, j) not in taken:  # if it is a different shape and haven't compared before increase overlap
                    taken.append((j,i))
                    overlap += 1
        return overlap

    def beautifulLayout(self, event):
        """runs when beautiful layout button clikced. finds overlaps and if neccessary calls optimization function.
        Then rearranges shapes in the canvas"""
        overlaps = self.overlapCount(self.shapes)
        self.overlap = overlaps

        if overlaps > 0:  # if there is a need for optimizing
            modifier = self.randomoptimize()

            if modifier != None:
                for i in self.shapes.keys():
                    xlength = abs(self.shapes[i][0]-self.shapes[i][2])  # length of x side of the shape
                    ylength = abs(self.shapes[i][1]-self.shapes[i][3])  # length of y side of the shape

                    # updating saved coordinates of the shape
                    self.shapes[i][0] = modifier[i][0]
                    self.shapes[i][1] = modifier[i][1]
                    self.shapes[i][2] = xlength+modifier[i][0]
                    self.shapes[i][3] = ylength+modifier[i][1]

                    #updating place of the shape
                    self.canvas.coords(self.canvas.find_withtag(i), self.shapes[i][0], self.shapes[i][1], self.shapes[i][2], self.shapes[i][3])
                # updating label demonstrating overlapping change
                self.label_overlap.config(text="Overlapping Changed From %s To %s" % (self.overlap, self.overlapCount(self.shapes)))

    def randomoptimize(self):
        """trying to find optimized way of displaying shapes by randomly replacing shapes in order to reduce overlaps"""
        best = self.overlap  # making best case current overlap count (not working for some reason)
        bestr = None

        for _ in range(50000):  # for better result 50.000 iterations
            r={}
            trylist = self.shapes  # cloning shapes' info
            for i in self.shapes.keys():
                xlength = abs(self.shapes[i][0]-self.shapes[i][2])  # length of x side of the shape
                ylength = abs(self.shapes[i][1]-self.shapes[i][3])  # length of y side of the shape
                rnd=[1000, 1000]
                while not ((xlength+rnd[0]) < 700 and (ylength+rnd[1]) < 400):  # getting random numbers until it is in the visible screen
                    rnd = [random.randint(1, 700), random.randint(1, 400)]
                r[i] = rnd

                # modify the clone shape info with random numbers
                trylist[i][0] = rnd[0]
                trylist[i][1] = rnd[1]
                trylist[i][2] = xlength+rnd[0]
                trylist[i][3] = ylength+rnd[1]

            # Get the cost with clone shape info
            cost = self.overlapCount(trylist)

            # Compare it to the best one so far
            if cost < best:
                best = cost
                bestr = r
                if cost == 0:
                    return bestr
        return bestr  # return random numbers that made clone shape info optimized

if __name__ == "__main__":
    root = Tk()
    root.title("My Paint")
    root.resizable(width=FALSE, height=FALSE)
    app = GUI(root)
    root.mainloop()