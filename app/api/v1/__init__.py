from dateutil import tz
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Response, Request
from ics import Calendar, Event

router = APIRouter()


class CalendarResponse(Response):
    media_type = "text/calendar"

    def render(self, content: Calendar) -> bytes:
        return content.serialize().encode("utf-8")


@router.get("/daysmart/{organization}/{team_id}.ics", response_class=CalendarResponse)
async def daysmart(
    request: Request,
    organization: str,
    team_id: int,
    team_from: str | None = None,
    team_to: str | None = None,
) -> CalendarResponse:
    client = request.state.client
    # TODO:  THE BELOW LIST IS INCOMPLETE/MISSING EARLY GAMES!
    resp = await client.get(
        f"https://apps.daysmartrecreation.com/dash/jsonapi/api/v1/events/?company={organization}&filter[publish]=true&filter[or.hteam_id]={team_id}&filter[or.and.vteam_id]={team_id}&include=homeTeam,visitingTeam,resource"
    )
    resp.raise_for_status()
    # TODO:  pydantic this
    content = resp.json()

    def translate(s):
        if team_from and team_to and s == team_from:
            return team_to
        return s

    cal = Calendar()
    teams = {int(o["id"]): o for o in content["included"] if o["type"] == "team"}
    locations = {
        int(o["id"]): o for o in content["included"] if o["type"] == "resource"
    }
    for event in content["data"]:
        if not event["attributes"]["publish"]:
            continue
        hteam_id = event["attributes"]["hteam_id"]
        vteam_id = event["attributes"]["vteam_id"]
        location_id = event["attributes"]["resource_id"]
        location_name = locations[location_id]["attributes"]["name"]
        hteam_name = translate(teams[hteam_id]["attributes"]["name"])
        vteam_name = translate(teams[vteam_id]["attributes"]["name"])
        cal.events.append(
            Event(
                summary=f"{vteam_name} at {hteam_name}",
                begin=datetime.fromisoformat(event["attributes"]["start_gmt"] + "Z"),
                end=datetime.fromisoformat(event["attributes"]["end_gmt"] + "Z"),
                location=location_name,
                uid=f"{event['id']}@blackhawks",
            )
        )

    return CalendarResponse(cal)


@router.get("/gamesheet/{season_id}/{team_id}.ics", response_class=CalendarResponse)
async def gamesheet(
    request: Request,
    season_id: int,
    team_id: int,
    tzstr: str = "America/Chicago",
    team_from: str | None = None,
    team_to: str | None = None,
) -> CalendarResponse:
    client = request.state.client
    resp = await client.get(
        f"https://gamesheetstats.com/api/useSchedule/getSeasonSchedule/{season_id}?filter[gametype]=overall&filter[teams]={team_id}&filter[limit]=1000"
    )
    resp.raise_for_status()
    # TODO:  pydantic this
    content = resp.json()

    def translate(s):
        if team_from and team_to and s == team_from:
            return team_to
        return s

    tzinfo = tz.gettz(tzstr)

    cal = Calendar()
    for day in content["1000_0"]:
        for game in day["games"]:
            # Gamesheet reports games with UTC zone info, but in local time.  Allow user to override localtime
            dt = datetime.fromisoformat(game["scheduleStartTime"][:-1])
            dt = dt.replace(tzinfo=tzinfo).astimezone(timezone.utc)
            cal.events.append(
                Event(
                    summary=f"{translate(game['visitorTeam']['name'])} at {translate(game['homeTeam']['name'])}",
                    begin=dt,
                    duration=timedelta(hours=1),
                    location=game["location"],
                    uid=f"{season_id}.{game['id']}",
                )
            )

    return CalendarResponse(cal)
