import sqlite3

DB_NAME = "vitaldrop_v2.db"

# ---------- Camps list (expanded + email added) ----------
camps = [
    ('MMG District Hospital Blood Bank', 'Ghaziabad', 'Nehru Nagar', 'MMG District Hospital, Nehru Nagar, Ghaziabad, UP', '9876500011', 'mmg.bloodbank@example.com', '', 1),
    ('Yashoda Hospital Blood Bank', 'Ghaziabad', 'Kaushambi', 'Yashoda Hospital, Kaushambi, Ghaziabad, UP', '9876500022', 'yashoda.bloodbank@example.com', '', 1),
    ('Vaishali Community Blood Center', 'Ghaziabad', 'Vaishali', 'Vaishali Sector 3, Ghaziabad, UP', '9876500033', 'vaishali.camp@example.com', '', 1),
    ('Indirapuram Blood Donation Camp', 'Ghaziabad', 'Indirapuram', 'Indirapuram, Ghaziabad, UP', '9876500044', 'indirapuram.camp@example.com', '', 1),
    ('Raj Nagar Extension Camp', 'Ghaziabad', 'Raj Nagar Extn', 'Raj Nagar Extension, Ghaziabad, UP', '9876500055', 'rajnagar.camp@example.com', '', 1),
    ('Kavi Nagar Red Cross Camp', 'Ghaziabad', 'Kavi Nagar', 'Kavi Nagar, Ghaziabad, UP', '9876500066', 'kavinagar.camp@example.com', '', 1),
    ('Vasundhara Blood Support Center', 'Ghaziabad', 'Vasundhara', 'Vasundhara Sector 10, Ghaziabad, UP', '9876500077', 'vasundhara.camp@example.com', '', 1),
    ('Crossing Republic Donation Center', 'Ghaziabad', 'Crossing Republic', 'Crossing Republic, Ghaziabad, UP', '9876500088', 'crossing.camp@example.com', '', 1),
    ('Loni Civil Hospital Unit', 'Ghaziabad', 'Loni', 'Civil Hospital Loni, Ghaziabad, UP', '9876500099', 'loni.hospital@example.com', '', 1),
    ('Sanjay Nagar Blood Camp', 'Ghaziabad', 'Sanjay Nagar', 'Sanjay Nagar, Ghaziabad, UP', '9876500100', 'sanjaynagar.camp@example.com', '', 1),
    ('Govindpuram Donation Camp', 'Ghaziabad', 'Govindpuram', 'Govindpuram, Ghaziabad, UP', '9876500111', 'govindpuram.camp@example.com', '', 1),
    ('Shastri Nagar Blood Camp', 'Ghaziabad', 'Shastri Nagar', 'Shastri Nagar, Ghaziabad, UP', '9876500122', 'shastri.camp@example.com', '', 1),
    ('Modinagar Support Camp', 'Ghaziabad', 'Modinagar', 'Modinagar, Ghaziabad, UP', '9876500133', 'modinagar.camp@example.com', '', 1),
    ('Muradnagar Donation Center', 'Ghaziabad', 'Muradnagar', 'Muradnagar, Ghaziabad, UP', '9876500144', 'muradnagar.camp@example.com', '', 1),
    ('Vijay Nagar Blood Support', 'Ghaziabad', 'Vijay Nagar', 'Vijay Nagar, Ghaziabad, UP', '9876500155', 'vijaynagar.camp@example.com', '', 1),

    # ---------- NEW extra coverage ----------
    ('Sahibabad Blood Donation Camp', 'Ghaziabad', 'Sahibabad', 'Sahibabad Industrial Area, Ghaziabad, UP', '9876500166', 'sahibabad.camp@example.com', '', 1),
    ('Hapur Road Emergency Blood Center', 'Ghaziabad', 'Hapur Road', 'Hapur Road, Ghaziabad, UP', '9876500177', 'hapurroad.camp@example.com', '', 1),
    ('Dasna Blood Support Camp', 'Ghaziabad', 'Dasna', 'Dasna, Ghaziabad, UP', '9876500188', 'dasna.camp@example.com', '', 1),
    ('Duhai Donation Camp', 'Ghaziabad', 'Duhai', 'Duhai, Ghaziabad, UP', '9876500199', 'duhai.camp@example.com', '', 1),
    ('Wave City Blood Camp', 'Ghaziabad', 'Wave City', 'Wave City NH-24, Ghaziabad, UP', '9876500200', 'wavecity.camp@example.com', '', 1),
]

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# ---------- Avoid duplicate insert ----------
for camp in camps:
    cur.execute("""
        SELECT id FROM camps
        WHERE camp_name = ? AND area = ?
    """, (camp[0], camp[2]))

    exists = cur.fetchone()

    if not exists:
        cur.execute("""
            INSERT INTO camps (camp_name, city, area, address, phone, email, google_maps_link, active_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, camp)

conn.commit()
conn.close()

print("✅ Camps inserted/updated successfully!")
