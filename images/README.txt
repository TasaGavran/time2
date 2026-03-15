LOKALNE SLIKE ZA TIME CAFFE SAJT
=================================

Trenutno sajt koristi placeholder slike (placehold.co) da ne bi bilo 404 grešaka.
Da biste koristili svoje slike:

1. Stavite fajlove ovde sa imenima: hero.jpg, about.jpg, gallery1.jpg … gallery6.jpg
2. U index.html zamenite:
   - Hero: u styles.css klasi .hero-bg postavite background-image na url("assets/images/hero.jpg"), pa rezervni URL
   - About: src slike u sekciji "O nama" na ./assets/images/about.jpg (dodajte onerror za rezervu)
   - Galerija: svaki <img> i data-src na ./assets/images/gallery1.jpg itd. (sa onerror na placehold.co)
3. Isto u galerija.html za gallery1–6.

Formati: JPG ili PNG. Preporučene dimenzije: hero 1600×900, about 1200×800, galerija min 600×400.
