import zipfile
import json
import re
import csv
import os
from io import TextIOWrapper
from datetime import datetime
from importers.utils import parse_float

def parse_googlefit_export(zip_file):
    data = {
        'imported_neat_min': None,
        'imported_cardio_mod_min': None,
        'imported_cardio_vig_min': None,
        'height_cm': None,
        'weight_kg': None,
    }

    def find_daily_metrics_csv(files):
        # Posibles nombres en distintos idiomas
        expected_filenames = {
            'Métricas de actividad diaria.csv',
            'Daily Activity Metrics.csv',
        }
        for fn in files:
            if os.path.basename(fn) in expected_filenames:
                return fn
        return None

    with zipfile.ZipFile(zip_file) as z:
        files = z.namelist()

        # 1) Carpeta raíz de Google Fit
        fit_prefix = None
        for fn in files:
            parts = fn.split('/')
            for i, p in enumerate(parts):
                if p.lower() == 'fit':
                    fit_prefix = '/'.join(parts[:i+1])
                    break
            if fit_prefix:
                break

        if not fit_prefix:
            raise ValueError("No se encontró la carpeta de Google Fit en el ZIP")
        print(f"[DEBUG] Google Fit prefix: {fit_prefix}")

        # 2) Procesar CSV de métricas diarias
        csv_fn = find_daily_metrics_csv(files)

        if csv_fn:
            print(csv_fn.title())
            with z.open(csv_fn) as f:
                reader = csv.DictReader(TextIOWrapper(f, 'utf-8'))
                rows = list(reader)[-30:]  # Últimos 30 días

            n = len(rows) or 1
            sum_total   = sum(parse_float(r.get('Recuento de Minutos Activos', 0)) or 0 for r in rows)
            sum_mod     = sum(parse_float(r.get('Minutos de cardio',         0)) or 0 for r in rows)
            sum_run_ms  = sum(parse_float(r.get('Correr duración (ms)',     0)) or 0 for r in rows)
            sum_walk_ms = sum(parse_float(r.get('Caminar duración (ms)',    0)) or 0 for r in rows)

            print(f"[DEBUG] Sumas: {sum_total}, {sum_mod}, {sum_run_ms}, {sum_walk_ms}")

            daily_total    = sum_total   / n
            daily_mod      = sum_mod     / n
            daily_run_min  = (sum_run_ms  / 1000 / 60) / n
            daily_walk_min = (sum_walk_ms / 1000 / 60) / n

            print(f"[DEBUG] Promedios diarios: {daily_total}, {daily_mod}, {daily_run_min}, {daily_walk_min}")

            daily_neat = max(daily_walk_min + (daily_total - daily_mod - daily_run_min), 0)

            data['imported_neat_min']       = int(daily_neat * 7)
            data['imported_cardio_mod_min'] = int(daily_mod   * 7)
            data['imported_cardio_vig_min'] = int(daily_run_min * 7)

        def _extract_raw_measure(fragment):
            pattern = re.compile(
                rf'.*raw_com\.google\.{re.escape(fragment)}.*\.json$',
                re.IGNORECASE
            )
            candidates = [fn for fn in files if pattern.search(fn)]
            if not candidates:
                return None
            candidates.sort(key=lambda fn: z.getinfo(fn).file_size, reverse=True)

            for fn in candidates:
                with z.open(fn) as f:
                    try:
                        obj = json.load(f)
                    except json.JSONDecodeError:
                        continue
                dps = obj.get("Data Points") or obj.get("dataPoints") or []
                if not isinstance(dps, list) or not dps:
                    continue
                dps.sort(key=lambda dp: int(dp.get("endTimeNanos", 0)), reverse=True)
                first = dps[0].get("fitValue") or []
                if isinstance(first, list) and first:
                    val = first[0].get("value", {}).get("fpVal")
                    v = parse_float(val)
                    if v is not None:
                        return v
            return None

        h = _extract_raw_measure("height")
        if h is not None:
            data['height_cm'] = round(h * 100, 2)

        w = _extract_raw_measure("weight")
        if w is not None:
            data['weight_kg'] = round(w, 2)

    return data
