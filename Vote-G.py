import json
import random
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AdvancedLotterySystem:
    def __init__(self, master):
        self.master = master
        master.title(" قرعه کشی آنلاین بازی چای کرک احمد و ایران کیش بستک ")
        master.geometry("1200x800")
        master.configure(bg='#f0f0f0')
        
        self.style = ttk.Style()
        self.configure_styles()
        
        self.create_widgets()
        self.data = self.load_and_clean_data()

    def configure_styles(self):
        self.style.theme_use('clam')
        
        # تنظیمات استایل جدول
        self.style.configure('Treeview',
                           font=('B Nazanin', 12),
                           rowheight=30,
                           background='#ffffff',
                           fieldbackground='#ffffff')
        
        self.style.configure('Treeview.Heading',
                           font=('B Titr', 13, 'bold'),
                           background='#3498db',
                           foreground='white')
        
        self.style.map('Treeview',
                     background=[('selected', '#2980b9')],
                     foreground=[('selected', 'white')])

    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # بخش انتخاب تیم
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(control_frame,
                text="انتخاب تیم:",
                font=('B Titr', 14)).pack(side=tk.LEFT, padx=10)
        
        self.team_var = tk.StringVar()
        self.team_combo = ttk.Combobox(
            control_frame,
            textvariable=self.team_var,
            values=["چای کرک احمد", "ایران کیش بستک"],
            state="readonly",
            font=('B Nazanin', 12),
            width=25
        )
        self.team_combo.pack(side=tk.LEFT, padx=10)
        self.team_combo.current(0)
        
        ttk.Button(control_frame,
                 text="شروع قرعه کشی",
                 command=self.run_lottery).pack(side=tk.LEFT, padx=10)

        # بخش جدول نتایج
        self.create_results_table(main_frame)

    def create_results_table(self, parent):
        # ایجاد فریم برای جدول و اسکرول بار
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # ایجاد Treeview
        self.results_table = ttk.Treeview(
            table_frame,
            columns=('id', 'name', 'phone'),
            show='headings',
            selectmode='browse'
        )
        
        # تنظیمات ستون‌ها
        self.results_table.heading('id', text='شناسه', anchor='center')
        self.results_table.heading('name', text='نام و نام خانوادگی', anchor='center')
        self.results_table.heading('phone', text='شماره تماس', anchor='center')
        
        self.results_table.column('id', width=120, anchor='center')
        self.results_table.column('name', width=300, anchor='center')
        self.results_table.column('phone', width=200, anchor='center')
        
        # ایجاد اسکرول بار
        scrollbar = ttk.Scrollbar(table_frame,
                                orient=tk.VERTICAL,
                                command=self.results_table.yview)
        self.results_table.configure(yscrollcommand=scrollbar.set)
        
        # چیدمان المان‌ها
        self.results_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_and_clean_data(self):
        try:
            with open('votes.json', 'r', encoding='utf-8') as file:
                raw_data = json.load(file)
            
            # حذف رکوردهای تکراری و نامعتبر
            seen_ids = set()
            clean_data = []
            
            for item in raw_data:
                log_id = item.get('Log ID')
                phone = str(item.get('شماره موبایل', '')).strip()
                
                if log_id and log_id not in seen_ids and len(phone) >= 11:
                    seen_ids.add(log_id)
                    clean_data.append(item)
            
            return clean_data
            
        except Exception as e:
            messagebox.showerror("خطا!", f"خطا در پردازش داده‌ها:\n{str(e)}")
            self.master.destroy()

    def format_phone_number(self, number):
        """فرمت‌دهی و مخفی‌سازی شماره تلفن"""
        num_str = str(number).strip()
        if len(num_str) == 11:
            return f"{num_str[:4]} {num_str[4:7]}•• {num_str[-3:]}"
        return "•••• •••• ••••"

    def run_lottery(self):
        # پاکسازی جدول قبلی
        for item in self.results_table.get_children():
            self.results_table.delete(item)
        
        selected_team = self.team_var.get()
        candidates = [
            v for v in self.data
            if v.get("Choices", "").strip() == selected_team
        ]
        
        if len(candidates) < 4:
            messagebox.showerror("خطا!", "تعداد شرکت کنندگان کافی نیست!")
            return

        try:
            winners = random.sample(candidates, 4)
        except ValueError:
            messagebox.showerror("خطا!", "خطا در انتخاب برندگان!")
            return

        # افزودن برندگان به جدول
        for winner in winners:
            self.results_table.insert('', tk.END, values=(
                winner['Log ID'],
                winner['نام و نام خانوادگی'],
                self.format_phone_number(winner['شماره موبایل'])
            ))
        
        # ذخیره نتایج
        self.save_results(selected_team, winners)

    def save_results(self, team, winners):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"نتایج_{team}_{timestamp}.csv"
        
        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                # نوشتن هدر فایل
                f.write("شناسه,نام کامل,شماره تماس\n")
                
                # نوشتن داده‌ها
                for winner in winners:
                    f.write(
                        f"{winner['Log ID']},"
                        f"{winner['نام و نام خانوادگی']},"
                        f"{self.format_phone_number(winner['شماره موبایل'])}\n"
                    )
            
            messagebox.showinfo("ذخیره شد!", f"نتایج در قالب CSV ذخیره شد:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("خطا!", f"خطا در ذخیره فایل:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedLotterySystem(root)
    root.mainloop()