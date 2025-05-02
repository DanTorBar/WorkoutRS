import os
import csv
import json
import re
import zipfile
from datetime import datetime
from io import TextIOWrapper
from importers.utils import parse_date, parse_float, parse_gender


def parse_fitbit_export(zip_file):
    data = {}
    profiles = []
    height_json_files = []
    weight_json_files = []
    light_files = []
    mod_files = []
    vig_files = []

    with zipfile.ZipFile(zip_file) as z:
        all_files = z.namelist()

        # Detectar el prefijo base dinámicamente
        global_export_prefix = next(
            (os.path.dirname(fn) + "/" for fn in all_files if "Global Export Data" in fn), ""
        )
        profile_csv = next(
            (fn for fn in all_files if fn.endswith("Your Profile/Profile.csv")), None
        )

        # --- Perfil CSV ---
        if profile_csv:
            with z.open(profile_csv) as f:
                text = TextIOWrapper(f, "utf-8")
                reader = csv.DictReader(text)
                profiles.extend(reader)

        # --- Clasificar ficheros de Global Export ---
        for fn in all_files:
            if fn.startswith(global_export_prefix):
                if re.search(r"height-\d{4}-\d{2}-\d{2}\.json$", fn):
                    height_json_files.append(fn)
                elif re.search(r"weight-\d{4}-\d{2}-\d{2}\.json$", fn):
                    weight_json_files.append(fn)
                elif "lightly_active_minutes-" in fn:
                    light_files.append(fn)
                elif "moderately_active_minutes-" in fn:
                    mod_files.append(fn)
                elif "very_active_minutes-" in fn:
                    vig_files.append(fn)

    # 2) Perfil
    if profiles:
        p = profiles[0]
        data["first_name"] = p.get("first_name") or None
        data["last_name"] = p.get("last_name") or None
        try:
            dob = p.get("date_of_birth")
            print(dob)
            data["date_of_birth"] = parse_date(dob) if dob else None
        except Exception:
            pass
        data["gender"] = parse_gender(p.get("gender"))

    # 3) Altura y peso
    def _extract_latest_json(files, conv):
        if not files:
            return None
        files.sort(reverse=True)
        for fn in files:
            with zipfile.ZipFile(zip_file) as z:
                with z.open(fn) as f:
                    try:
                        records = json.load(f)
                    except Exception:
                        continue
                    if not records:
                        continue
                    sorted_records = sorted(
                        records,
                        key=lambda r: parse_date(r.get("dateTime") or r.get("date")),
                        reverse=True,
                    )
                    for r in sorted_records:
                        val = r.get("value") or r.get("bmi")
                        if val is not None:
                            try:
                                return round(conv(val), 2)
                            except:
                                continue
        return None

    h = _extract_latest_json(height_json_files, parse_float)
    if h is not None:
        data["height"] = h / 10

    b = _extract_latest_json(weight_json_files, parse_float)
    if b is not None:
        if h is not None:
            w = round((b * (h ** 2)) / 1000000, 2)
            data["weight"] = w

    # 4) Actividad

    def _extract_months(files):
        months = set()
        for fn in files:
            match = re.search(r'(\d{4}-\d{2})-\d{2}\.json$', fn)
            if match:
                months.add(match.group(1))
        return sorted(months)

    all_months = (
        _extract_months(light_files) +
        _extract_months(mod_files) +
        _extract_months(vig_files)
    )
    unique_months = sorted(set(all_months))
    prefix = unique_months[-2] if len(unique_months) >= 2 else None

    def _choose_file(files):
        return next((fn for fn in files if prefix and prefix in fn), None)

    light_fn = _choose_file(light_files)
    mod_fn = _choose_file(mod_files)
    vig_fn = _choose_file(vig_files)

    def _avg_minutes(fn):
        if not fn:
            return 0
        with zipfile.ZipFile(zip_file) as z, z.open(fn) as f:
            records = json.load(f)
        minutes = []
        for r in records:
            try:
                dt = parse_date(r["dateTime"])
            except:
                continue
            if dt:
                minutes.append(int(r.get("value", 0)))
                
        return sum(minutes) / len(minutes) if minutes else 0

    daily_light = _avg_minutes(light_fn)
    daily_mod = _avg_minutes(mod_fn)
    daily_vig = _avg_minutes(vig_fn)

    data["imported_neat_min"] = int(daily_light * 7)
    data["imported_cardio_mod_min"] = int(daily_mod * 7)
    data["imported_cardio_vig_min"] = int(daily_vig * 7)

    return data
