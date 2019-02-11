import tkinter as tk

root=tk.Tk()

class Handler:

    def __init__(self, w):
        self.w = w
        self.w.bind("<Button-1>", self.xaxis)
        w.bind("<ButtonRelease-1>", self.yaxis)
        w.bind("<ButtonRelease-1>", self.create)


    def xaxis(self, event):
        self.x1, self.y1 = (event.x - 1), (event.y - 1)

    def yaxis(self, event):
        self.x2, self.y2 = (event.x + 1), (event.y + 1)

    def create(self, event):
        self.yaxis(event)
        self.w.create_rectangle(self.x1,self.y1,self.x2,self.y2,fill='Black')

w = tk.Canvas(root, width=200, height=200)
w.config(cursor='cross')
w.pack(expand=tk.YES, fill=tk.BOTH)

Handler(w)


root.mainloop()