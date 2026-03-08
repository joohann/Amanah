# Bijdragen aan Amanah

Bedankt voor je interesse in het verbeteren van Amanah!

## Ontwikkelomgeving opzetten

```bash
git clone https://github.com/joohann/amanah
cd amanah
pip install ruff pylint
```

## Regels

- Branch van `dev`, niet van `main`
- Gebruik `feat/beschrijving` of `fix/beschrijving` als branchnaam
- Update altijd `CHANGELOG.md` en versienummers bij een release
- Voer `ruff check custom_components/amanah/` uit voor je een PR opent
- Voer `python3 scripts/check_versions.py` uit om versie consistentie te controleren

## Versie bijwerken

Bij elke nieuwe release: update op **drie** plekken tegelijk:

1. `custom_components/amanah/manifest.json` → `"version"`
2. `custom_components/amanah/const.py` → `VERSION` en `VERSION_DATE`
3. `CHANGELOG.md` → nieuwe sectie bovenaan

De CI (`validate.yml`) controleert automatisch of deze drie overeenkomen.

## Een release aanmaken

1. Zorg dat alle wijzigingen op `main` staan
2. Maak een tag aan: `git tag v1.1.0`
3. Push: `git push origin v1.1.0`
4. De `release.yml` workflow maakt automatisch een GitHub Release aan
