#تابع چک کردن صحت مینترم های ورودی
def check_range(list, Vars):
    for num in list:
        if int(num) < 0 or int(num) > (2**Vars)-1:
            return True
    return False

Vars = int(input("تعداد متغیرهای مدار را تعیین کنید:"))

#ایحاد متغیر ها
import string
letters = list(string.ascii_uppercase[:Vars])


#دریافت مینترم ها
while True:
    Minterms = input("مینترم ها را با فاصله وارد کنید(example: 2 4 5):\n")
    minterms = [int(num) for num in Minterms.split()]
    if check_range(minterms, Vars):
        print("حداقل یکی از اعداد وارد شده خارج از محدوده است.")
    else:
        break

# ایجاد لیست مینترم ها بصورت باینری
digits = f"0{Vars}b"
bin_Minterms = [format(i, digits) for i in minterms]
print(" --> مینترم های وارد شده: \n",
      bin_Minterms)

from itertools import combinations


def quine_mccluskey(minterms):
    # تابعی برای مقایسه دو minterm و ایجاد ترکیب جدید
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

    # تولید Prime Implicants
    groups = {}
    for minterm in bin_Minterms:
        ones = minterm.count('1')
        groups.setdefault(ones, []).append(minterm)

    # ترکیب گروه‌ها
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

        # اضافه کردن غیرترکیب‌شده‌ها به prime implicants
        for group in groups.values():
            for term in group:
                if term not in marked:
                    prime_implicants.add(term)

        groups = new_groups

    # جدول پوشش برای استخراج EPI
    coverage_table = {minterm: [] for minterm in minterms}
    for pi in prime_implicants:
        covered_minterms = []
        for m in minterms:
            binary_m = format(m, f"0{Vars}b")
            match = all(
                pi[i] == binary_m[i] or pi[i] == '-' for i in range(Vars))
            if match:
                coverage_table[m].append(pi)

    # شناسایی EPI‌ها
    essential_prime_implicants = set()
    for minterm, pi_list in coverage_table.items():
        if len(pi_list) == 1:  # فقط یک PI این minterm را پوشش می‌دهد
            essential_prime_implicants.add(pi_list[0])

    return prime_implicants, essential_prime_implicants

pi, epi = quine_mccluskey(minterms)
print(" --> PIs:", pi)
print(" --> Essential PI:", epi)

def extract_final_expression(minterms, pi, epi):
    # حذف minterms پوشش داده‌شده توسط EPI‌ها
    covered_minterms = set()
    for e in epi:
        for m in minterms:
            binary_m = format(m, f"0{max(minterms).bit_length()}b")
            if all(e[i] == binary_m[i] or e[i] == '-' for i in range(len(e))):
                covered_minterms.add(m)

    remaining_minterms = set(minterms) - covered_minterms

    # جدول پوشش برای PI‌های باقی‌مانده
    coverage_table = {m: [] for m in remaining_minterms}
    for p in pi - epi:
        for m in remaining_minterms:
            binary_m = format(m, f"0{max(minterms).bit_length()}b")
            if all(p[i] == binary_m[i] or p[i] == '-' for i in range(len(p))):
                coverage_table[m].append(p)

    # انتخاب حداقل PI‌ها برای پوشش minterms باقی‌مانده
    # در اینجا از روش ساده greedy برای انتخاب استفاده می‌شود
    additional_pi = set()
    for m, possible_pi in coverage_table.items():
        if possible_pi:
            additional_pi.add(possible_pi[0])  # اولین PI را انتخاب کنید (می‌توان روش بهینه‌تری استفاده کرد)

    # ترکیب EPI و PI اضافی
    final_pi = epi.union(additional_pi)

    # تبدیل به معادله منطقی
    def to_expression(pi):
        expression = []
        for i, bit in enumerate(pi):
            if bit == '1':
                expression.append(letters[i])
            elif bit == '0':
                expression.append(letters[i]+"'")
        return ''.join(expression)

    final_expression = ' + '.join(to_expression(p) for p in final_pi)
    return final_expression

final_expression = extract_final_expression(minterms, pi, epi)
print(" ==> Final Expression:")
print('\t',(len(final_expression)+2)*"█")
print("\t"+" █" + final_expression + "█")
print('\t',(len(final_expression)+2)*"█")
