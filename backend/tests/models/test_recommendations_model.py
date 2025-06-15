# Tests para modelos de recommendations
import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from main.models.recommendations import RecommendCache

User = get_user_model()

@pytest.mark.django_db
def test_create_recommend_cache():
    user = User.objects.create_user(username="reco_user", password="testpass")
    reco = RecommendCache.objects.create(
        user=user,
        item_type="exercise",
        item_id=1,
        score=0.95
    )
    assert reco.user == user
    assert reco.item_type == "exercise"
    assert reco.score == 0.95
    assert str(reco).startswith(f"Recomendación para {user.username}")

def test_recommendations_model_placeholder():
    assert True

@pytest.mark.django_db
def test_recommend_cache_unique_together():
    user = User.objects.create_user(username="ruser1", password="testpass")
    RecommendCache.objects.create(user=user, item_type="exercise", item_id=1, score=0.5)
    with pytest.raises(IntegrityError):
        RecommendCache.objects.create(user=user, item_type="exercise", item_id=1, score=0.7)

@pytest.mark.django_db
def test_recommend_cache_str():
    user = User.objects.create_user(username="ruser2", password="testpass")
    reco = RecommendCache.objects.create(user=user, item_type="workout", item_id=2, score=0.8)
    assert str(reco).startswith(f"Recomendación para {user.username}")
