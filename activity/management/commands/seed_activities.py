import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db.models import Q

from activity.models import PhysicalActivity


class Command(BaseCommand):
    help = "Carga un catalogo inicial de actividades sin duplicados."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="",
            help="Ruta opcional al JSON de actividades.",
        )

    def handle(self, *args, **options):
        data_path = options["path"].strip()
        if data_path:
            json_path = Path(data_path)
        else:
            json_path = Path(__file__).resolve().parents[2] / "data" / "activities.json"

        if not json_path.exists():
            self.stderr.write(f"No se encontro el archivo: {json_path}")
            return

        with json_path.open("r", encoding="utf-8") as handle:
            activities = json.load(handle)

        created = 0
        updated = 0
        keep_keys = set()
        for item in activities:
            name = item.get("name", "").strip()
            if not name:
                continue

            keep_keys.add(name)
            defaults = {
                "met_value": item.get("met_value", 1.0),
                "intensity": item.get("intensity", PhysicalActivity.IntensityChoices.MODERATE),
                "is_active": item.get("is_active", True),
            }

            _, was_created = PhysicalActivity.objects.update_or_create(
                name=name,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        deleted = 0
        if keep_keys:
            to_delete = PhysicalActivity.objects.exclude(Q(name__in=keep_keys))
            deleted = to_delete.count()
            to_delete.delete()

        self.stdout.write(
            f"Actividades cargadas. Nuevas: {created}. Actualizadas: {updated}. Eliminadas: {deleted}."
        )

