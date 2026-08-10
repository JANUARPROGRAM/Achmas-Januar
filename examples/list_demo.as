# Contoh Type System v0.3: List, indexing, null
#
# List di AstraLang ditulis dengan [ ] dan bisa berisi tipe data apa pun,
# termasuk List lain (nested list / matrix).

print "=== Membuat & mencetak List ==="
let angka = [10, 20, 30]
print angka

print "=== Indexing ==="
print angka[0]
print angka[2]

print "=== Mengubah elemen (index assignment) ==="
angka[1] = 99
print angka

print "=== Panjang List ==="
print len(angka)

print "=== Menambah & menghapus elemen ==="
push(angka, 40)
print angka
let terakhir = pop(angka)
print "Elemen yang dihapus:"
print terakhir
print angka

print "=== List bersarang (nested list / matrix sederhana) ==="
let matrix = [[1, 2], [3, 4], [5, 6]]
print matrix[0][1]
print matrix[2][0]

print "=== Looping isi List ==="
let buah = ["apel", "jeruk", "mangga"]
let i = 0
while i < len(buah) {
    print buah[i]
    i = i + 1
}

print "=== Nilai null ==="
let kosong = null
print kosong
if kosong == null {
    print "variabel ini memang belum diisi"
}
