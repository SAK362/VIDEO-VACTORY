import re
NARR=open('narasi0002.txt',encoding='utf-8').read() if False else None
TEXT="""Bayangkan dua murid menerima nilai matematika yang sama-sama jelek.
Murid pertama berpikir,|“Ya sudah,|aku memang nggak pintar hitungan.”
Murid kedua berpikir,|“Berarti ada cara belajar yang belum pas.”
Nilainya sama.|Tapi cara mereka memaknainya berbeda jauh.
Itulah inti buku Mindset karya Carol Dweck,|psikolog dari Stanford.
Pola pikir tetap meyakini bahwa kemampuan,|termasuk kecerdasan,|sudah bawaan dan sulit berubah.|Pola pikir bertumbuh meyakini bahwa kemampuan bisa dikembangkan lewat belajar dan latihan.
Perbedaan ini terbukti punya dampak.|Dalam sebuah penelitian,|tim Dweck mengikuti tiga ratus tujuh puluh tiga siswa kelas tujuh selama dua tahun.|Siswa yang percaya kecerdasan bisa berkembang,|nilainya cenderung naik.|Siswa yang percaya kecerdasan itu tetap,|nilainya cenderung datar.
Bukan karena yang satu lebih pintar di awal.|Tapi karena yang satu lebih mau bertahan saat pelajaran mulai sulit.
Dalam penelitian lain di kelas tujuh,|sekelompok siswa diajari bahwa otak bisa menguat lewat belajar.|Nilai matematika mereka tidak turun,|padahal pelajaran makin sulit|dan nilai kelompok pembanding merosot.
Artinya,|keyakinan itu bukan teori di awang-awang.|Ia ikut menentukan seberapa gigih seseorang belajar.
Jadi,|pola pikir bukan sekadar soal semangat.|Ia menentukan apa yang kamu lakukan setelah gagal:|menyerah,|atau mencari cara lain.
Saat nilaimu jelek,|kamu biasanya ada di kubu yang mana?
Ikuti BeYourBest,|dan tulis di komentar|topik apa lagi yang mau kamu bahas berikutnya."""
# unit = segmen antar tanda baca; punct = tanda di akhir segmen ('.', ',', '?' atau '' bila lanjut)
UNITS=[];SENT=[]
si=0
for line in TEXT.split('\n'):
    for seg in line.split('|'):
        seg=seg.strip()
        end='.' if seg[-1] in '.?”' and not seg.endswith(',”') else ','
        # akhir kalimat sebenarnya
        UNITS.append({'text':seg,'sent':si,'end':end})
    si+=1
