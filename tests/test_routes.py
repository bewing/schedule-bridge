from datetime import datetime, timezone

from ics import Calendar
from httpx import Response

from util import load_json, get_test_file


def test_gamesheet(client, respx_mock):
    mock_json = load_json(get_test_file("gamesheet.json"))
    respx_mock.get(
        "https://gamesheetstats.com/api/useSchedule/getSeasonSchedule/1?filter[gametype]=overall&filter[teams]=15&filter[limit]=1000"
    ).return_value = Response(status_code=200, json=mock_json)
    resp = client.get("/api/v1/gamesheet/1/15.ics")
    cal = Calendar.parse_multiple(resp.text)[0]
    assert len(cal.events) == 9
    # TODO:  test more


def test_gamesheet_rename(client, respx_mock):
    mock_json = load_json(get_test_file("gamesheet.json"))
    respx_mock.get(
        "https://gamesheetstats.com/api/useSchedule/getSeasonSchedule/1?filter[gametype]=overall&filter[teams]=15&filter[limit]=1000"
    ).return_value = Response(status_code=200, json=mock_json)
    resp = client.get(
        "/api/v1/gamesheet/1/15.ics?team_from=Maple Leafs&team_to=Senators"
    )
    cal = Calendar.parse_multiple(resp.text)[0]
    assert cal.events[4].summary == "Black Hawks at Senators"


TIMETOSCORE_URL = (
    "https://stats.asec.timetoscore.com/team-cal.php?team=4368&season=38&format=iCal"
)


def test_timetoscore(client, respx_mock):
    respx_mock.get(TIMETOSCORE_URL).return_value = Response(
        status_code=200, text=get_test_file("timetoscore.ics").read_text()
    )
    resp = client.get("/api/v1/timetoscore/asec/38/4368.ics")
    cal = Calendar.parse_multiple(resp.text)[0]
    assert len(cal.events) == 21
    assert cal.events[0].summary == "Puckin’ Pandas Copper AA at Chiefs"
    assert cal.events[0].begin == datetime(2026, 9, 13, 3, 40, tzinfo=timezone.utc)
    assert all(event.description is None for event in cal.events)
    assert "X-WR-TIMEZONE:America/Chicago" in resp.text
    assert "US/Pacific" not in resp.text


def test_timetoscore_rename(client, respx_mock):
    respx_mock.get(TIMETOSCORE_URL).return_value = Response(
        status_code=200, text=get_test_file("timetoscore.ics").read_text()
    )
    resp = client.get(
        "/api/v1/timetoscore/asec/38/4368.ics?team_from=Chiefs&team_to=Blackhawks"
    )
    cal = Calendar.parse_multiple(resp.text)[0]
    assert cal.events[0].summary == "Puckin’ Pandas Copper AA at Blackhawks"
    assert cal.events[1].summary == "Blackhawks at Chicago Pride Hockey"
    assert "X-WR-CALNAME:TEAM: Blackhawks" in resp.text


def test_timetoscore_rejects_bad_league(client, respx_mock):
    resp = client.get("/api/v1/timetoscore/evil.com%23/38/4368.ics")
    assert resp.status_code == 422
    assert not respx_mock.calls
