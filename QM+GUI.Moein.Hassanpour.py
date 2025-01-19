import customtkinter as ctk
from tkinter import messagebox
from itertools import combinations
import string

# توابع برنامه اصلی
def check_range(minterms, vars_count):
    for num in minterms:
        if int(num) < 0 or int(num) > (2**vars_count) - 1:
            return True
    return False

def quine_mccluskey(minterms, vars_count):
    def combine_terms(term1, term2):
        diff = 0
        combined = ''
        for i in range(len(term1)):
            if term1[i] != term2[i]:
                diff += 1
                combined += '-'
            else:
                combined += term1[i]
        return combined if diff == 1 else None

    groups = {}
    for minterm in [format(m, f"0{vars_count}b") for m in minterms]:
        ones = minterm.count('1')
        groups.setdefault(ones, []).append(minterm)

    prime_implicants = set()
    while groups:
        new_groups = {}
        marked = set()
        for g1, g2 in combinations(sorted(groups), 2):
            if g2 - g1 != 1:
                continue
            for term1 in groups[g1]:
                for term2 in groups[g2]:
                    combined = combine_terms(term1, term2)
                    if combined:
                        marked.add(term1)
                        marked.add(term2)
                        ones = combined.count('1')
                        new_groups.setdefault(ones, []).append(combined)
        for group in groups.values():
            for term in group:
                if term not in marked:
                    prime_implicants.add(term)
        groups = new_groups

    coverage_table = {minterm: [] for minterm in minterms}
    for pi in prime_implicants:
        for m in minterms:
            binary_m = format(m, f"0{vars_count}b")
            match = all(pi[i] == binary_m[i] or pi[i] == '-' for i in range(vars_count))
            if match:
                coverage_table[m].append(pi)

    essential_prime_implicants = set()
    for minterm, pi_list in coverage_table.items():
        if len(pi_list) == 1:
            essential_prime_implicants.add(pi_list[0])

    return prime_implicants, essential_prime_implicants

def extract_final_expression(minterms, pi, epi, vars_count, letters):
    covered_minterms = set()
    for e in epi:
        for m in minterms:
            binary_m = format(m, f"0{vars_count}b")
            if all(e[i] == binary_m[i] or e[i] == '-' for i in range(len(e))):
                covered_minterms.add(m)

    remaining_minterms = set(minterms) - covered_minterms
    coverage_table = {m: [] for m in remaining_minterms}
    for p in pi - epi:
        for m in remaining_minterms:
            binary_m = format(m, f"0{vars_count}b")
            if all(p[i] == binary_m[i] or p[i] == '-' for i in range(len(p))):
                coverage_table[m].append(p)

    additional_pi = set()
    for m, possible_pi in coverage_table.items():
        if possible_pi:
            additional_pi.add(possible_pi[0])

    final_pi = epi.union(additional_pi)

    def to_expression(pi):
        expression = []
        for i, bit in enumerate(pi):
            if bit == '1':
                expression.append(letters[i])
            elif bit == '0':
                expression.append(letters[i]+"'")
        return ''.join(expression)

    return ' + '.join(to_expression(p) for p in final_pi)

# GUI با customtkinter
ctk.set_appearance_mode("dark")  # حالت تیره
ctk.set_default_color_theme("green")  # تم رنگی سبز

app = ctk.CTk()
app.geometry("600x500")
app.title("Quine-McCluskey Minimizer")

# فریم اصلی
frame = ctk.CTkFrame(app, corner_radius=15)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# عنوان
title_label = ctk.CTkLabel(frame, text="ساده‌سازی منطقی با روش Quine-McCluskey", 
                           font=("Helvetica", 18, "bold"))
title_label.pack(pady=15)

# ورودی تعداد متغیرها
vars_label = ctk.CTkLabel(frame, text="تعداد متغیرها:")
vars_label.pack(pady=5)
vars_entry = ctk.CTkEntry(frame, placeholder_text="مثال: 3")
vars_entry.pack(pady=5)

# ورودی مینترم‌ها
minterms_label = ctk.CTkLabel(frame, text="مینترم‌ها را وارد کنید (با فاصله):")
minterms_label.pack(pady=5)
minterms_entry = ctk.CTkEntry(frame, placeholder_text="مثال: 1 3 7")
minterms_entry.pack(pady=5)

# محدوده مجاز
range_label = ctk.CTkLabel(frame, text="")
range_label.pack(pady=5)

# تغییر بازه مجاز هنگام وارد کردن تعداد متغیرها
def update_range_label(*args):
    try:
        vars_count = int(vars_entry.get())
        range_label.configure(text=f"محدوده مجاز: 0 تا {2**vars_count - 1}")
    except ValueError:
        range_label.configure(text="")

vars_entry.bind("<KeyRelease>", update_range_label)

# دکمه محاسبه
def calculate_expression():
    try:
        vars_count = int(vars_entry.get())
        minterms = list(map(int, minterms_entry.get().split()))
        if check_range(minterms, vars_count):
            messagebox.showerror("خطا", f"حداقل یکی از مینترم‌ها خارج از محدوده است! محدوده مجاز: 0 تا {2**vars_count - 1}")
            return
        letters = list(string.ascii_uppercase[:vars_count])
        pi, epi = quine_mccluskey(minterms, vars_count)
        final_expr = extract_final_expression(minterms, pi, epi, vars_count, letters)
        output_text.set(final_expr)
    except Exception as e:
        messagebox.showerror("خطا", f"مشکلی پیش آمد:\n{e}")

calc_button = ctk.CTkButton(frame, text="محاسبه", command=calculate_expression)
calc_button.pack(pady=10)

# خروجی
output_text = ctk.StringVar()
output_label = ctk.CTkLabel(frame, textvariable=output_text, wraplength=500, 
                            font=("Courier New", 14), text_color="#FFD700")
output_label.pack(pady=20)

# اجرای برنامه
app.mainloop()
