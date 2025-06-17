from datetime import timedelta
from django.utils import timezone
from main.models.recommendations import RecommendCache
from main.models.exercise import Exercise
from main.models.workout import Workout
import pandas as pd

CACHE_TTL_HOURS = 6

def get_cached_recommendations(user_id, item_type, top_n, ttl_hours=CACHE_TTL_HOURS):
    now = timezone.now()
    cutoff = now - timedelta(hours=ttl_hours)
    cached = RecommendCache.objects.filter(
        user_id=user_id, item_type=item_type, recommended_at__gte=cutoff
    ).order_by('-score')[:top_n]
    if cached.count() == top_n:
        ids = [c.item_id for c in cached]
        if item_type == 'exercise':
            items = Exercise.objects.filter(id__in=ids)
            id_to_name = {e.id: e.exerciseName for e in items}
            names = [id_to_name.get(i, '') for i in ids]
            return pd.DataFrame({'id': ids, 'exerciseName': names})
        elif item_type == 'workout':
            items = Workout.objects.filter(id__in=ids)
            id_to_name = {w.id: w.workoutName for w in items}
            names = [id_to_name.get(i, '') for i in ids]
            return pd.DataFrame({'id': ids, 'workoutName': names})
    return None
