# Tests para modelos de logs
import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from main.models.logs import ViewLog, ActivityLog

User = get_user_model()

@pytest.mark.django_db
def test_create_view_log():
    user = User.objects.create_user(username="loguser", password="testpass")
    ct = ContentType.objects.get_for_model(User)
    log = ViewLog.objects.create(user=user, content_type=ct, object_id=user.id)
    assert log.user == user
    assert log.content_type == ct
    assert str(log).startswith(f"{user.username} viewed")

@pytest.mark.django_db
def test_create_activity_log():
    user = User.objects.create_user(username="loguser2", password="testpass")
    log = ActivityLog.objects.create(user=user, action="IMPORT", detail="Importación de datos")
    assert log.user == user
    assert log.action == "IMPORT"
    assert str(log).startswith(f"{user.username} IMPORT")

@pytest.mark.django_db
def test_view_log_content_type():
    user = User.objects.create_user(username="loguser1", password="testpass")
    ct = ContentType.objects.get_for_model(User)
    log = ViewLog.objects.create(user=user, content_type=ct, object_id=user.id)
    assert log.item == user

@pytest.mark.django_db
def test_activity_log_str():
    user = User.objects.create_user(username="loguser2", password="testpass")
    log = ActivityLog.objects.create(user=user, action="IMPORT", detail="Importación de datos")
    assert str(log).startswith(f"{user.username} IMPORT")

@pytest.mark.django_db
def test_view_log_ordering():
    user = User.objects.create_user(username="loguser3", password="testpass")
    ct = ContentType.objects.get_for_model(User)
    ViewLog.objects.create(user=user, content_type=ct, object_id=user.id)
    ViewLog.objects.create(user=user, content_type=ct, object_id=user.id)
    logs = list(ViewLog.objects.all())
    assert logs[0].timestamp >= logs[1].timestamp
