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
