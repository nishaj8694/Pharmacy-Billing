import tkinter as tk
from tkinter import ttk
import os.path
import sqlite3
from tkinter import messagebox
from datetime import datetime,timedelta

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("STORE COLLECTION")
        self.pages = {}
        self.buttons = {}
        self.create_navbar()
        self.window_size()
        self.resizable(False, False)

    def window_size(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        desired_width = int(0.9 * screen_width)
        desired_height = int(0.9 * screen_height)
        center_x = int(screen_width / 2 - desired_width / 2)
        center_y = int(screen_height / 2 - desired_height / 2)
        self.geometry(f"{desired_width}x{desired_height}+{center_x}+{center_y}")

    def navigate(self, page_name):
        for button_name, button in self.buttons.items():
            if button_name == page_name:
                button.config(bg="grey")
            else:    
                button.config(bg="lightgrey")
                

        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill=tk.BOTH, expand=True)

    def create_navbar(self):
        navbar_frame = tk.Frame(self, bg="lightgrey", bd=1, relief=tk.RAISED)
        navbar_frame.pack(side=tk.TOP, fill=tk.X)

        font_type = "Helvetica"
        font_size = 12
        button_font = (font_type, font_size, "bold")

        page_names = ["Home", "Transaction", "Stock", "Depletion"]
        screen_width = self.winfo_screenwidth()
        button_width = screen_width // len(page_names)
        num_characters = int(button_width / font_size)

        for page_name in page_names:
            button_text = page_name[:num_characters]
            button = tk.Button(navbar_frame, text=button_text, padx=5, pady=5,
                               command=lambda page_name=page_name: self.navigate(page_name),
                               width=num_characters, font=button_font, activebackground="red")
            button.pack(side=tk.LEFT, padx=5, pady=5)
            self.buttons[page_name] = button

            if page_name == 'Transaction':
                self.transaction_page()
            elif page_name == 'Stock':
                self.stock_page()
            elif page_name == 'Home':
                self.pages[page_name] = tk.Frame(self)
                label = tk.Label(self.pages[page_name], text=f"This is the {page_name} page", font=("Arial", 20))
                label.pack(pady=20)
               
            elif page_name == 'Depletion':
                self.depletion_page()
                
      
    def transaction_page(self):
        page = tk.Frame(self)
        self.pages['Transaction'] = page

        TotalAmount=0
            
        def TotalAmountPrice():
            global TotalAmount
            TotalAmount = 0
            for item_id in billView.get_children():
                record_values = billView.item(item_id, 'values')
                TotalAmount+=int(record_values[5])
                
            Mnydisplay.config(text=TotalAmount)
            Mnydisplay.update() 
        

        def clearBill():
            itemno1.delete(0,tk.END)
            mny.delete(0,tk.END)
            qty.delete(0,tk.END)

        def selctedBillView(e):
            clearBill()
            selected = billView.focus()
            tem = billView.item(selected, 'values')
            itemno1.insert(0, tem[0])
            mny.insert(0, tem[3])
            qty.insert(0, tem[4])

        def billAddition():
            conn=sqlite3.connect('stock.db')
            c=conn.cursor()
            c.execute('SELECT * FROM stock WHERE itemno=?',itemno1.get())
            data=c.fetchall()
            if int(data[0][3])-int(qty.get())>0:
                for i in data:
                    billView.insert('', 0, values=(i[0], i[1], i[4], i[2], qty.get(), int(i[2])*int(qty.get())))
            else:
                messagebox.showwarning('QUANTITY LOW','YOUR SELECT PRODUCT QUANTTY IS VERY LOW PLEASE SELECT OTHER PRODUCT')        
            clearBill()
            TotalAmountPrice()
            c.close()

        def RemoveItems():
            result = messagebox.askyesno("Remove Items", f"Do you want to Remove the Item ?")
            if result:
                selected = billView.focus()
                try:
                    billView.delete(selected)
                    TotalAmountPrice()
                    clearBill()
                except:
                    messagebox.showinfo("Warning","Medicine can't deleted try againe ")

        def BillEdit():
            selected = billView.focus()
            tem = billView.item(selected, 'values')

            if mny.get()=='':
                billView.insert('', 0, values=(tem[0],tem[1],tem[2],tem[3],qty.get(),int(tem[3])*int(qty.get())))
                billView.delete(selected)
            
            else:
                result = messagebox.askyesno("Change Price", f"Do you want to Change the Price from ${tem[3]} to ${mny.get()} ?")
                if result:
                    billView.insert('', 0, values=(tem[0],tem[1],tem[2],mny.get(),qty.get(),int(mny.get())*int(qty.get())))
                    billView.delete(selected)
                else:
                    pass
                
            TotalAmountPrice()
            clearBill()

        def PrintBill():
            PrintAmount = 0
            conn=sqlite3.connect('stock.db')
            c=conn.cursor()
            today=datetime.now().date() 
            c.execute('SELECT billno FROM total WHERE date=? ORDER BY billno DESC LIMIT?',[today, 1])
            data=c.fetchall()
            global current_bill
            if data:
                current_bill=data[0][0]
                current_bill+=1
            else:
                current_bill=str(today)+str(1)
                current_bill=int(''.join(current_bill.split('-')))

            for item_id in billView.get_children():
                record = billView.item(item_id, 'values')
                local_qt=c.execute('SELECT quanty FROM stock WHERE  itemno=?',record[0])
                current_qt=local_qt.fetchone()
                current_qt=current_qt[0]
                if current_qt-int(record[4])>0:
                   qt=current_qt-int(record[4])                   
                   c.execute('INSERT INTO cusbill (itemno,name,quanty,price,amount,billno) VALUES(?,?,?,?,?,?)',[record[0],record[1],record[4],record[3],record[5],current_bill])
                   conn.commit()
                   c.execute('UPDATE stock SET quanty=? WHERE itemno=?', (qt, record[0]))
                   conn.commit() 
                   PrintAmount+=int(record[5])    
                else:    
                    billView.delete(item_id)

            c.execute('INSERT INTO total (billno,sum,date) VALUES(?,?,?)',[current_bill,PrintAmount,today])                
            conn.commit() 
            c.close()


        left = tk.Frame(page,width=30,height=23)
        left.grid(row=0,column=0,padx=0,pady=0,sticky="n")
        right = tk.Frame(page)
        right.grid(row=0,column=1)
        Bottom = tk.Frame(page)
        Bottom.grid(row=2,column=1)
        itemno = tk.Label(left, text="ID", width=23, font=("Arial", 12))
        itemno1 = tk.Entry(left)
        itemno.grid(row=0, column=0, pady=(20,0))
        itemno1.grid(row=1, column=0)
        price = tk.Label(left, text="Price", font=("Arial", 12))
        mny = tk.Entry(left,)
        price.grid(row=4, column=0, pady=(15,0))
        mny.grid(row=5, column=0, pady=(0, 20))
        quanty1 = tk.Label(left, text="Quantity", font=("Arial", 12))
        qty = tk.Entry(left,)
        quanty1.grid(row=2, column=0, pady=(15,0))
        qty.grid(row=3, column=0,)
        submit = tk.Button(left, text="ADD", width=20, font=("Arial", 12), command=billAddition)
        submit.grid(row=6, column=0, pady=(0, 20))
        update = tk.Button(left, text="REMOVE", width=20, font=("Arial", 12), command=RemoveItems)
        update.grid(row=7, column=0, pady=(0, 20))
        Delete = tk.Button(left, text="UPDATE", width=20, font=("Arial", 12), command=BillEdit)
        Delete.grid(row=8, column=0, pady=(0, 20))
        Total = tk.Label(Bottom, text="Total", width=23, font=("Arial", 12))
        Mnydisplay = tk.Label(Bottom,text=TotalAmount)
        Print = tk.Button(Bottom, text="Print", width=20, font=("Arial", 12), command=PrintBill)
        Total.grid(row=0, column=1,sticky="e")
        Mnydisplay.grid(row=0, column=3,sticky="e")
        Print.grid(row=0, column=0, padx=(5),pady=(5))


        billView = ttk.Treeview(right, columns=('ID', 'MEDICINE NAME', 'EXP', 'PRICE', 'QT','AMOUNT'), height=30)
        billView.place(x=60, y=95)
        billView['show'] = 'headings'
        billView.heading('#0', text='')
        billView.heading('#1', text='ID')
        billView.heading('#2', text='MEDICINE NAME')
        billView.heading('#3', text='EXP')
        billView.heading('#4', text='PRICE')
        billView.heading('#5', text='QT')
        billView.heading('#6', text='AMOUNT')
        billView.column('#0', anchor='c', width=1)
        billView.column('#1', anchor='c', width=150)
        billView.column('#2', anchor='c', width=400)
        billView.column('#3', anchor='c', width=150)
        billView.column('#4', anchor='c', width=150)
        billView.column('#5', anchor='c', width=100)
        billView.column('#6', anchor='c', width=200)
        billView.pack()

        billView.focus()
        billView.bind("<ButtonRelease-1>", selctedBillView)

    def stock_page(self):
        page = tk.Frame(self)
        self.pages['Stock'] = page


        left = tk.Frame(page,width=30,height=23)
        left.grid(row=0,column=0,sticky="n")
        right = tk.Frame(page)
        right.grid(row=0,column=1)

        
        def clearDisplay():
            itno1.delete(0,tk.END)
            name1.delete(0,tk.END)
            price1.delete(0,tk.END)
            quanty.delete(0,tk.END)
            expdate1.delete(0,tk.END)
            rcloc1.delete(0,tk.END)
            subtance1.delete(0,tk.END)   

        def selctedInput(e):
            clearDisplay()
            selected = tr1.focus()
            tem = tr1.item(selected, 'values')
            itno1.insert(0, tem[0])
            name1.insert(0, tem[1])
            price1.insert(0, tem[2])
            quanty.insert(0, tem[3])
            expdate1.insert(0, tem[4])
            rcloc1.insert(0, tem[5])
            subtance1.insert(0, tem[6])

        def ProductAddition():
            if name1.get()=='' or price1.get()=='' or quanty.get()=='' or expdate1.get()==''or rcloc1.get()=='' or subtance1.get()=='':
                
                messagebox.showerror("Product Addition","You must Put values in input field")
               
            else:
                conn=sqlite3.connect('stock.db')
                c=conn.cursor()
                c.execute('SELECT * FROM stock WHERE itemno=? OR name=? OR rloc=?',[itno1.get(),name1.get(),rcloc1.get()])
                data=c.fetchall()
                if not data:
                    try:
                        c.execute('INSERT INTO stock(itemno,name,price,quanty,expdate,rloc,subt) VALUES(?,?,?,?,?,?,?)',[itno1.get(),name1.get(),price1.get(),quanty.get(),expdate1.get(),rcloc1.get(),subtance1.get()])
                    except:
                        messagebox.showerror("Product Addition","Somethings went wrong Please check the Input Fields")
        
                    tr1.insert('', 0, values=(itno1.get(),name1.get(),price1.get(),quanty.get(),expdate1.get(),rcloc1.get(),subtance1.get()))
                    clearDisplay()
                    conn.commit()
                    conn.close()
                else:
                    messagebox.showwarning("Data Addition","The Product is alredy in database")    
            
        def ProductEdit():
            selected = tr1.focus()
            conn = sqlite3.connect('stock.db')
            c = conn.cursor()
            tem = tr1.item(selected, 'values')
            if itno1.get() != '':
                c.execute('update stock set name = ?, price = ?, quanty = ?, expdate = ?, rloc = ?, subt = ? where itemno= ?',[name1.get(), price1.get(), quanty.get(), expdate1.get(), rcloc1.get(),subtance1.get(), itno1.get()])
                conn.commit()
                tr1.insert('', 0, values=(itno1.get(),name1.get(),price1.get(),quanty.get(),expdate1.get(),rcloc1.get(),subtance1.get()))
                tr1.delete(selected)
                clearDisplay()
            else:    
                    messagebox.showwarning("Data Updation","The Product id is empty")    
                

        con=sqlite3.connect('stock.db')
        cn=con.cursor()
        cn.execute('SELECT * FROM stock')
        n=cn.fetchall()
        s=0
        
        def deletedItems():
            selected = tr1.focus()
            try:
                tem = tr1.item(selected, 'values')
                valno = tem[0]
                conn = sqlite3.connect('stock.db')
                c = conn.cursor()
                c.execute("DELETE  FROM stock WHERE itemno=?", (valno,))
                conn.commit()
                tr1.delete(selected)
                clearDisplay()

            except:
                messagebox.showinfo("Warning","Medicine can't deleted try againe ")


        def confirm_delete():
            result = messagebox.askquestion("Confirmation", "Are you sure you want to delete this item?")
            if result == 'yes':
                deletedItems()        

        itno = tk.Label(left, text="ID", width=23, font=("Arial", 12))
        itno1 = tk.Entry(left)
        itno.grid(row=0, column=0, pady=(20,0))
        itno1.grid(row=1, column=0)
        name = tk.Label(left, text="Name", font=("Arial", 12))
        name1 = tk.Entry(left)
        name.grid(row=2, column=0, pady=(15,0))
        name1.grid(row=3, column=0)
        price = tk.Label(left, text="Price", font=("Arial", 12))
        price1 = tk.Entry(left,)
        price.grid(row=4, column=0, pady=(15,0))
        price1.grid(row=5, column=0)
        quanty1 = tk.Label(left, text="Quantity", font=("Arial", 12))
        quanty = tk.Entry(left,)
        quanty1.grid(row=6, column=0, pady=(15,0))
        quanty.grid(row=7, column=0)
        expdate = tk.Label(left, text="EXP(YYYY-MM-DD)", font=("Arial", 12))
        expdate.grid(row=8, column=0, pady=(15,0))
        expdate1 = tk.Entry(left)
        expdate1.grid(row=9, column=0)
        rcloc = tk.Label(left, text="Location", font=("Arial", 12))
        rcloc1 = tk.Entry(left)
        rcloc.grid(row=10, column=0, pady=(15,0))
        rcloc1.grid(row=11, column=0)
        subtance = tk.Label(left, text="Substance", font=("Arial", 12))
        subtance1 = tk.Entry(left,)
        subtance.grid(row=12, column=0, pady=(15,0))
        subtance1.grid(row=13, column=0, pady=(0, 20))
        submit = tk.Button(left, text="CREATE", width=20, bg=('green'), font=("Arial", 12), command=ProductAddition)
        submit.grid(row=14, column=0, pady=(0, 20))
        update = tk.Button(left, text="UPDATE", width=20, bg=('orange'), font=("Arial", 12), command=ProductEdit)
        update.grid(row=15, column=0, pady=(0, 20))
        Delete = tk.Button(left, text="DELETE", width=20, bg=('red'), font=("Arial", 12), command=confirm_delete)
        Delete.grid(row=16, column=0, pady=(0, 20))
        ClearBtn = tk.Button(left, text="CLEAR", width=20, bg=('white'), font=("Arial", 12), command=clearDisplay)
        ClearBtn.grid(row=17, column=0, pady=(0, 20))
    
        tr1 = ttk.Treeview(right, columns=('ID', 'MEDICINE NAME', 'PRICE', 'QT', 'EXP', 'LOC', 'SUBSTANCE'), height=30)
        tr1.place(x=60, y=95)
        tr1['show'] = 'headings'
        tr1.heading('#0', text='')
        tr1.heading('#1', text='ID')
        tr1.heading('#2', text='MEDICINE NAME')
        tr1.heading('#3', text='PRICE')
        tr1.heading('#4', text='QT')
        tr1.heading('#5', text='EXP')
        tr1.heading('#6', text='LOC')
        tr1.heading('#7', text='SUBSTANCE')
        tr1.column('#0', anchor='c', width=1)
        tr1.column('#1', anchor='c', width=100)
        tr1.column('#2', anchor='c', width=310)
        tr1.column('#3', anchor='c', width=100)
        tr1.column('#4', anchor='c', width=50)
        tr1.column('#5', anchor='c', width=100)
        tr1.column('#6', anchor='c', width=50)
        tr1.column('#7', anchor='c', width=450)
        tr1.pack()
        for i in n:
            tr1.insert('', 0, text='hi', values=(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))    
        tr1.focus()
        tr1.bind("<ButtonRelease-1>", selctedInput)
        cn.close()

    def depletion_page(self):
        page = tk.Frame(self)
        self.pages['Depletion'] = page
        
        left = tk.Frame(page,width=30,height=23)
        left.grid(row=0,column=0,sticky="n")
        right = tk.Frame(page)
        right.grid(row=0,column=1)

        def expiry_madicine():
            for item_id in tr1.get_children():
                tr1.item(item_id, 'values')
                tr1.delete(item_id)

            days=selected_option.get()
            day=0
            if days=="Today":
                day=1
            if days=="Weak":
                day=7 
            if days=="2 Weak":
                day=15 
            if days=="Month":
                day=30
            today=datetime.now().date()
            today = today+ timedelta(days=day)
            today= today.strftime('%Y-%m-%d')
            con=sqlite3.connect('stock.db')
            cn=con.cursor()
            data = cn.execute('SELECT * FROM stock WHERE expdate < ?', (today,))
            data=data.fetchall()
            for rec in data:
                tr1.insert('', 0, text='hi', values=(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[6]))

            con.close()
             
           

        def deficiency_madicine():
            
            for item_id in tr1.get_children():
                tr1.item(item_id, 'values')
                tr1.delete(item_id)

            con=sqlite3.connect('stock.db')
            cn=con.cursor()
            cn.execute('SELECT * FROM stock WHERE quanty < 10')
            n=cn.fetchall()

            for i in n:
                tr1.insert('', 0, text='hi', values=(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))   

            con.close()

        # itno = tk.Label(left, text="", width=23, font=("Arial", 12))
        # itno.grid(row=0, column=0, pady=(20,0))
            
        options = ["Today", "Weak", "2 Weak", "Month"]
          
        selected_option = tk.StringVar()    
        selected_option.set(options[0])

        dropdown = ttk.Combobox(left, textvariable=selected_option, values=options)
        dropdown.grid(row=0, column=0, pady=(20,0))
        Delete = tk.Button(left, text="Expired",  width=20, font=("Arial", 12), command=expiry_madicine)
        Delete.grid(row=1, column=0, pady=(0, 20))
        ClearBtn = tk.Button(left, text="Insufficient", width=20, font=("Arial", 12), command=deficiency_madicine)
        ClearBtn.grid(row=2, column=0, pady=(0, 20))
    
        tr1 = ttk.Treeview(right, columns=('ID', 'MEDICINE NAME', 'PRICE', 'QT', 'EXP', 'LOC', 'SUBSTANCE'), height=30)
        tr1.place(x=60, y=95)
        tr1['show'] = 'headings'
        tr1.heading('#0', text='')
        tr1.heading('#1', text='ID')
        tr1.heading('#2', text='MEDICINE NAME')
        tr1.heading('#3', text='PRICE')
        tr1.heading('#4', text='QT')
        tr1.heading('#5', text='EXP')
        tr1.heading('#6', text='LOC')
        tr1.heading('#7', text='SUBSTANCE')
        tr1.column('#0', anchor='c', width=1)
        tr1.column('#1', anchor='c', width=100)
        tr1.column('#2', anchor='c', width=310)
        tr1.column('#3', anchor='c', width=100)
        tr1.column('#4', anchor='c', width=50)
        tr1.column('#5', anchor='c', width=100)
        tr1.column('#6', anchor='c', width=50)
        tr1.column('#7', anchor='c', width=450)
        tr1.pack()
        

if __name__ == "__main__":
    app = Application()
    app.mainloop()
