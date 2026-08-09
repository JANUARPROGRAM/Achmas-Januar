# Contoh Custom Type v0.3
#
# Custom type dideklarasikan dengan 'type Nama { field1 field2 ... }'
# lalu instance-nya dibuat dengan 'Nama { field1: nilai1, field2: nilai2 }'.
# Nama type harus diawali huruf besar.

print "=== Deklarasi type & membuat instance ==="
type Point {
    x
    y
}

let p1 = Point { x: 0, y: 0 }
let p2 = Point { x: 3, y: 4 }
print p1
print p2

print "=== Mengakses & mengubah field ==="
print p2.x
print p2.y
p2.x = 10
print p2

print "=== Type dengan field List ==="
type Player {
    name
    scores
}

let player = Player { name: "Astra", scores: [80, 90, 100] }
print player.name
print player.scores
push(player.scores, 95)
print player.scores

print "=== Type dipakai sebagai parameter fungsi ==="
function jarak_horizontal(a, b) {
    let selisih = a.x - b.x
    if selisih < 0 {
        return 0 - selisih
    }
    return selisih
}

print jarak_horizontal(p1, p2)

print "=== List berisi instance custom type ==="
type Item {
    nama
    harga
}

let keranjang = [
    Item { nama: "Buku", harga: 50000 },
    Item { nama: "Pensil", harga: 5000 }
]

let total = 0
let i = 0
while i < len(keranjang) {
    let item = keranjang[i]
    print item.nama
    total = total + item.harga
    i = i + 1
}
print "Total:"
print total
