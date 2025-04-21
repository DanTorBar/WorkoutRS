import zipfile
import unicodedata
from lxml import etree
from datetime import datetime, timedelta
from importers.utils import parse_date, parse_float, parse_gender

WORKOUT_INTENSITY = {
    "HKWorkoutActivityTypeWalking":        ("light", 3.0),
    "HKWorkoutActivityTypeYoga":           ("light", 2.5),
    "HKWorkoutActivityTypeCycling":        ("moderate", 6.0),
    "HKWorkoutActivityTypeRunning":        ("intense", 8.0),
    "HKWorkoutActivityTypeSwimming":       ("intense", 7.0),
    "HKWorkoutActivityTypeHiking":         ("moderate", 6.0),
    "HKWorkoutActivityTypeTraditionalStrengthTraining": ("intense", 6.0),
    "HKWorkoutActivityTypeHighIntensityIntervalTraining": ("intense", 9.0),
}

def _parse_effective_high(obs, ns):
    """Devuelve datetime del <effectiveTime><high value="…+ZZZZ"/> o None."""
    high = obs.find('cda:effectiveTime/cda:high', namespaces=ns)
    if high is None or not high.get('value'):
        return None
    v = high.get('value')  # e.g. "20220921185824+0200"
    try:
        return datetime.strptime(v, "%Y%m%d%H%M%S%z")
    except ValueError:
        # prueba sin zona
        try:
            return datetime.strptime(v, "%Y%m%d%H%M%S")
        except ValueError:
            return None

def parse_apple_export(zip_path):
    data = {}
    light = moderate = intense = 0.0
    ns = {'cda': 'urn:hl7-org:v3'}

    # Variables para trackear la fecha más reciente
    best_height_dt = None
    best_weight_dt = None

    try:
        with zipfile.ZipFile(zip_path) as z:
            namelist = z.namelist()

            # 1) Perfil y vital signs
            cda_file = next((fn for fn in namelist if fn.lower().endswith("export_cda.xml")), None)
            if cda_file:
                with z.open(cda_file) as f:
                    root = etree.parse(f).getroot()

                    # Nombre
                    name_el = root.find('.//cda:name[@use="CL"]', namespaces=ns)
                    if name_el is not None:
                        data['first_name'] = name_el.text

                    # Género
                    gender_el = root.find('.//cda:administrativeGenderCode', namespaces=ns)
                    if gender_el is not None:
                        disp = gender_el.get('displayName') or gender_el.get('code')
                        data['gender'] = parse_gender(disp)

                    # Fecha de nacimiento
                    birth_el = root.find('.//cda:birthTime', namespaces=ns)
                    if birth_el is not None and birth_el.get('value'):
                        try:
                            data['date_of_birth'] = datetime.strptime(
                                birth_el.get('value'), "%Y%m%d"
                            ).date()
                        except ValueError:
                            pass

                    # Recorremos cada <observation> bajo entries de tipo DRIV
                    for obs in root.findall('.//cda:entry[@typeCode="DRIV"]//cda:observation', namespaces=ns):
                        code_el = obs.find('cda:code', namespaces=ns)
                        val_el  = obs.find('cda:value', namespaces=ns)
                        if code_el is None or val_el is None:
                            continue

                        code = code_el.get('code')
                        val  = parse_float(val_el.get('value'))
                        dt   = _parse_effective_high(obs, ns)

                        # Altura: LOINC 8302‑2
                        if code == "8302-2" and val is not None and dt:
                            if best_height_dt is None or dt > best_height_dt:
                                best_height_dt = dt
                                data['height'] = val

                        # Peso: LOINC 3141‑9
                        elif code == "3141-9" and val is not None and dt:
                            if best_weight_dt is None or dt > best_weight_dt:
                                best_weight_dt = dt
                                data['weight'] = val


            # 2) Localizar el XML de datos de registro (export*.xml)
            candidates = [
                fn for fn in namelist
                if fn.lower().endswith('.xml')
                   and 'export_cda' not in fn.lower()
                   and 'export' in fn.lower()
            ]
            if not candidates:
                return data
            export_file = max(candidates, key=lambda fn: z.getinfo(fn).file_size)

            # 3) Procesar workouts (últimos 30 días)
            with z.open(export_file) as f:
                ctx = etree.iterparse(f, tag="Workout", recover=True)
                today = datetime.now().date()
                cutoff = today - timedelta(days=30)
                workout_days = set()

                for _, w in ctx:
                    start = parse_date(w.get("startDate"))
                    dur   = (parse_float(w.get("duration")) or 0.0) / 60.0
                    wtype = w.get("workoutActivityType")
                    if start and start >= cutoff and dur > 0 and wtype:
                        workout_days.add(start)
                        lvl = WORKOUT_INTENSITY.get(wtype, (None,))[0]
                        if lvl == "light":
                            light += dur
                        elif lvl == "moderate":
                            moderate += dur
                        elif lvl == "intense":
                            intense += dur
                    w.clear()

                if workout_days:
                    days_count = len(workout_days)
                    data['imported_neat_min']       = int((light / days_count) * 7)
                    data['imported_cardio_mod_min'] = int((moderate / days_count) * 7)
                    data['imported_cardio_vig_min'] = int((intense / days_count) * 7)

            # 4) Fallback ActivitySummary si no hay workouts
            if not data.get('imported_neat_min'):
                with z.open(export_file) as f:
                    ctx = etree.iterparse(f, tag="ActivitySummary", recover=True)
                    total_cal, total_days = 0.0, 0
                    for _, el in ctx:
                        day = parse_date(el.get("dateComponents"))
                        if day:
                            total_cal += parse_float(el.get("activeEnergyBurned")) or 0.0
                            total_days += 1
                        el.clear()

                    if total_days:
                        avg_cal = total_cal / total_days
                        daily_mod_min = avg_cal / 5.0
                        data['imported_cardio_mod_min'] = int(daily_mod_min * 7)

    except Exception as e:
        print(f"[EXCEPTION] Error processing Apple Health ZIP: {e}")
        return data

    return data
