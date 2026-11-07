class kalkulator:
    def __init__(self, angka1, angka2):
        self.angka1 = angka1
        self.angka2 = angka2
        
    def penjumlahan(self):
        return self.angka1 + self.angka2
    
    def penmgurangan (self):
        return self.angka1 - self.angka2
    
    def perkalian (self):
        return self.angka1 * self.angka2

    def pembagian (self):
        if self.angka2 != 0:
            return self.angka1 / self.angka2
        else:
            return "Error: Pembagian dengan nol tidak diperbolehkan"
        
print(" === KALKULATOR SEDERHANA === ")

user_input1 = float(input("Masukan angka pertama: "))
user_input2 = float(input("Masukan angka kedua: "))

hasil_penjumlahan = kalkulator(user_input1, user_input2).penjumlahan()
hasil_pengurangan = kalkulator(user_input1, user_input2).penmgurangan()
hasil_perkalian = kalkulator(user_input1, user_input2).perkalian()
hasil_pembagian = kalkulator(user_input1, user_input2).pembagian()

print("hasil dari pernjumlahan = ", hasil_penjumlahan)
print("hasil pengurangan = ", hasil_pengurangan)
print("hasil pengurangan = ", hasil_perkalian)
print("hasil pembagian = ", hasil_pembagian)

kalkulator.kali_dua = lambda x: x * 2

hasil_dua_kali_1 = kalkulator.kali_dua(user_input1)
hasil_dua_kali_2 = kalkulator.kali_dua(user_input2)

print("Hasil dua kali angka pertama:", hasil_dua_kali_1)
print("Hasil dua kali angka kedua:", hasil_dua_kali_2)