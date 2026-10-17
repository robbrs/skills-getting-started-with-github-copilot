ACTIVITY = "Chess Club"
EXISTING_EMAIL = "michael@mergington.edu"
NEW_EMAIL = "newstudent@mergington.edu"


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert ACTIVITY in data
    assert expected_fields <= set(data[ACTIVITY])


def test_signup_adds_participant(client):
    # Arrange
    url = f"/activities/{ACTIVITY}/signup"

    # Act
    response = client.post(url, params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {NEW_EMAIL} for {ACTIVITY}"}
    participants = client.get("/activities").json()[ACTIVITY]["participants"]
    assert NEW_EMAIL in participants


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    url = "/activities/Nonexistent Club/signup"

    # Act
    response = client.post(url, params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    # Arrange
    url = f"/activities/{ACTIVITY}/signup"

    # Act
    response = client.post(url, params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant(client):
    # Arrange
    url = f"/activities/{ACTIVITY}/signup"

    # Act
    response = client.delete(url, params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {EXISTING_EMAIL} from {ACTIVITY}"}
    participants = client.get("/activities").json()[ACTIVITY]["participants"]
    assert EXISTING_EMAIL not in participants


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    url = "/activities/Nonexistent Club/signup"

    # Act
    response = client.delete(url, params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up_returns_404(client):
    # Arrange
    url = f"/activities/{ACTIVITY}/signup"

    # Act
    response = client.delete(url, params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_signup_then_unregister_round_trip(client):
    # Arrange
    url = f"/activities/{ACTIVITY}/signup"
    client.post(url, params={"email": NEW_EMAIL})

    # Act
    response = client.delete(url, params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 200
    participants = client.get("/activities").json()[ACTIVITY]["participants"]
    assert NEW_EMAIL not in participants
