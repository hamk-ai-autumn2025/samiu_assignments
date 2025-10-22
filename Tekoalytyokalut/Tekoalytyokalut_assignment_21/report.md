# REPORT.md – Django Web Application

**Tekijä:** Sami Ukkonen  
**GitHub-linkki:** [https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/Tekoalytyokalut/Tekoalytyokalut_assignment_21](https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/Tekoalytyokalut/Tekoalytyokalut_assignment_21)

---

## Kuvaus

Django-sovellus *"Möttösen Peruna & Porkkana"* on yksinkertainen maatilan kotisivu, jossa hallitaan tuotteita ja palveluja.  
Admin-liittymässä voi lisätä ja muokata tuotteita ja palveluja. Julkisella sivustolla näkyvät nämä tiedot listattuna.

Rakenteessa on:
- `farm`-sovellus tuotteille ja palveluille  
- `models.py` määrittelee tietorakenteet  
- `admin.py` aktivoi ne hallintapaneeliin  
- `views.py` ja `urls.py` muodostavat näkymät  
- `templates/` sisältää sivupohjat

---

## Käyttöönotto

```bash
cd Tekoalytyokalut_assignment_21
python -m venv .venv && source .venv/bin/activate
pip install django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Admin: http://127.0.0.1:8000/admin/

Etusivu: http://127.0.0.1:8000/