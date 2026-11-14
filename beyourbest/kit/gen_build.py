s=open('../build.py',encoding='utf-8').read()
s=s.replace("T=json.load(open('timing.json'))","T=json.load(open('/home/claude/beyourbest/v2/timing.json'))")
i_ad=s.index('# ---------- adegan ----------')
i_ov=s.index('# ---------- overlay ----------')
i_cards=s.index('def cards(t):')
i_frame=s.index('def frame_svg(t):')
head=s[:i_ad]
ov=s[i_ov:i_cards]
tail=s[i_frame:]
# judul baru
a=ov.index('TITLES=[');b=ov.index('def rich')
ov=ov[:a]+'''TITLES=[(0,'POLA PIKIR','Dua murid,','*nilai sama*'),(1,'MURID PERTAMA','“Aku memang','*nggak pintar*”'),(4,'MURID KEDUA','Ada *cara belajar*','yang belum pas'),(6,'NILAI SAMA','Cara *memaknai*','berbeda jauh'),(8,'BUKU MINDSET','Carol Dweck,','*psikolog* Stanford'),(10,'POLA PIKIR TETAP','Kemampuan itu','*sudah bawaan*'),(13,'POLA PIKIR BERTUMBUH','Kemampuan bisa','*dikembangkan*'),(14,'PENELITIAN','*373 siswa* kelas 7','selama *dua tahun*'),(17,'HASILNYA','Percaya bisa berkembang','nilai *naik*'),(19,'HASILNYA','Percaya itu tetap','nilai *datar*'),(21,'BUKAN SOAL PINTAR','Yang beda:','*mau bertahan*'),(23,'PENELITIAN LAIN','Otak bisa *menguat*','lewat belajar'),(25,'HASILNYA','Nilai *tidak turun*','pembanding *merosot*'),(28,'ARTINYA','Keyakinan ikut','menentukan *gigih*'),(31,'SETELAH GAGAL','Menyerah,','atau *cari cara lain*'),(36,'REFLEKSI','Kamu ada di','*kubu* yang mana?'),(38,'BEYOURBEST','Topik apa lagi','yang mau *kita bahas*?')]
'''+ov[b:]
ov=ov.replace("t>gs(28) or (gs(26)+0.6<t<gs(28))","t>gs(38)-0.1 or t<3.2")
new=open('scenes_part.py',encoding='utf-8').read()
open('build2.py','w',encoding='utf-8').write(head+new.split('#@@OVERLAY')[0]+ov+new.split('#@@OVERLAY')[1]+tail)
