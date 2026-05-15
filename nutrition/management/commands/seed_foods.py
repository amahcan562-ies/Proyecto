import json
from pathlib import Path

from django.core.management.base import BaseCommand

from nutrition.models import Food


class Command(BaseCommand):
    help = "Carga un catalogo inicial de alimentos sin duplicados."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="",
            help="Ruta opcional al JSON de alimentos.",
        )

    def handle(self, *args, **options):
        data_path = options["path"].strip()
        if data_path:
            json_path = Path(data_path)
        else:
            json_path = (
                Path(__file__).resolve().parents[2] / "data" / "foods.json"
            )

        if not json_path.exists():
            self.stderr.write(f"No se encontro el archivo: {json_path}")
            return

        with json_path.open("r", encoding="utf-8") as handle:
            foods = json.load(handle)

        created = 0
        updated = 0
        for item in foods:
            name = item.get("name", "").strip()
            if not name:
                continue
            brand = item.get("brand", "").strip()
            defaults = {
                "image_url": item.get("image_url", "").strip(),
                "calories_per_100g": item.get("calories_per_100g", 0),
                "protein_per_100g": item.get("protein_per_100g", 0),
                "carbs_per_100g": item.get("carbs_per_100g", 0),
                "fat_per_100g": item.get("fat_per_100g", 0),
                "fiber_per_100g": item.get("fiber_per_100g", 0),
                "is_active": item.get("is_active", True),
            }

            _, was_created = Food.objects.update_or_create(
                name=name,
                brand=brand,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            f"Alimentos cargados. Nuevos: {created}. Actualizados: {updated}."
        )

