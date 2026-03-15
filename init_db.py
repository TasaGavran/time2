"""Initialize the database with default admin, categories, and sample menu items."""
from app import create_app
from models import db, User, Category, MenuItem

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("[+] Admin korisnik kreiran (admin / admin123)")

    if not Category.query.first():
        categories_data = [
            ("Topli napici", 1),
            ("Hladni napici", 2),
            ("Kokteli", 3),
            ("Pivo / Vino", 4),
            ("Deserti", 5),
        ]
        cats = {}
        for name, order in categories_data:
            c = Category(name=name, sort_order=order)
            db.session.add(c)
            db.session.flush()
            cats[name] = c.id

        sample_items = [
            (cats["Topli napici"], "Espresso", "Klasičan italijanski espresso", 180, 1),
            (cats["Topli napici"], "Cappuccino", "Espresso sa kremastom mlečnom penom", 250, 2),
            (cats["Topli napici"], "Caffe Latte", "Nežna kombinacija espressa i toplog mleka", 280, 3),
            (cats["Topli napici"], "Turska kafa", "Tradicionalno skuvana domaća kafa", 150, 4),
            (cats["Topli napici"], "Topla čokolada", "Gusta čokolada sa šlagom", 300, 5),
            (cats["Topli napici"], "Čaj", "Izbor biljnih i voćnih čajeva", 180, 6),

            (cats["Hladni napici"], "Ledena kafa", "Osvežavajuća hladna kafa sa ledom", 280, 1),
            (cats["Hladni napici"], "Frappé", "Kremasti hladni espresso napitak", 320, 2),
            (cats["Hladni napici"], "Ceđena pomorandža", "Sveže ceđen sok od pomorandže", 300, 3),
            (cats["Hladni napici"], "Limunada", "Domaća limunada sa mentom", 250, 4),
            (cats["Hladni napici"], "Smoothie", "Voćni smoothie po izboru", 350, 5),
            (cats["Hladni napici"], "Gazirana voda", "San Pellegrino 0.5l", 200, 6),

            (cats["Kokteli"], "Mojito", "Rum, limeta, menta, šećer, soda", 550, 1),
            (cats["Kokteli"], "Aperol Spritz", "Aperol, prosecco, soda", 600, 2),
            (cats["Kokteli"], "Espresso Martini", "Vodka, espresso, Kahlúa", 650, 3),
            (cats["Kokteli"], "Gin Tonic", "Premium gin, tonic, limeta", 550, 4),
            (cats["Kokteli"], "Margarita", "Tekila, cointreau, limeta", 600, 5),

            (cats["Pivo / Vino"], "Točeno pivo 0.5l", "Zaječarsko ili Lav", 300, 1),
            (cats["Pivo / Vino"], "Craft pivo", "Izbor craft piva", 400, 2),
            (cats["Pivo / Vino"], "Belo vino čaša", "Domaće belo vino", 350, 3),
            (cats["Pivo / Vino"], "Crno vino čaša", "Domaće crno vino", 350, 4),
            (cats["Pivo / Vino"], "Roze vino čaša", "Osvežavajući roze", 350, 5),

            (cats["Deserti"], "Cheesecake", "New York cheesecake sa umakom od bobica", 450, 1),
            (cats["Deserti"], "Tiramisu", "Klasični italijanski tiramisu", 420, 2),
            (cats["Deserti"], "Čokoladni fondant", "Topli čokoladni kolač sa tekućim centrom", 480, 3),
            (cats["Deserti"], "Palačinke", "Sa Nutellom, voćem ili džemom", 380, 4),
            (cats["Deserti"], "Sladoled", "Tri kugle po izboru", 300, 5),
        ]

        for cat_id, name, desc, price, order in sample_items:
            item = MenuItem(
                category_id=cat_id,
                name=name,
                description=desc,
                price=price,
                available=True,
                sort_order=order
            )
            db.session.add(item)

        print("[+] Kategorije i primer stavki menija kreirani")

    db.session.commit()
    print("[OK] Baza podataka inicijalizovana uspešno.")
