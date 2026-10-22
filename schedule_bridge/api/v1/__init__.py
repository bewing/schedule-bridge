from dateutil import tz
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Path, Response, Request
from ics import Calendar, ContentLine, Event

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
    if "included" in content:
        teams = {int(o["id"]): o for o in content["included"] if o["type"] == "teams"}
        locations = {
            int(o["id"]): o for o in content["included"] if o["type"] == "resources"
        }
    for event in content["data"]:
        if not all([event["attributes"]["publish"], event["attributes"]["vteam_id"]]):
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


def _split_matchup(summary: str, location: str | None) -> tuple[str, str] | None:
    """Split a TimeToScore summary ("{location}  {away} @  {home}") into (away, home)."""
    if location:
        summary = summary.removeprefix(location)
    away, separator, home = summary.partition("@")
    if not separator:
        return None
    return away.strip(), home.strip()


@router.get(
    "/timetoscore/{league}/{season_id}/{team_id}.ics", response_class=CalendarResponse
)
async def timetoscore(
    request: Request,
    league: Annotated[str, Path(pattern=r"^[a-z0-9-]+$")],
    season_id: int,
    team_id: int,
    tzstr: str = "America/Chicago",
    team_from: str | None = None,
    team_to: str | None = None,
) -> CalendarResponse:
    client = request.state.client
    resp = await client.get(
        f"https://stats.{league}.timetoscore.com/team-cal.php?team={team_id}&season={season_id}&format=iCal"
    )
    resp.raise_for_status()

    def translate(s):
        if team_from and team_to and s == team_from:
            return team_to
        return s

    cal = Calendar(resp.text)
    for event in cal.events:
        # BenchApp copies DESCRIPTION into the game notes
        event.description = None
        matchup = _split_matchup(event.summary or "", event.location)
        if matchup is None:
            continue
        away, home = matchup
        event.summary = f"{translate(away)} at {translate(home)}"

    # TimeToScore event times are correct UTC instants; only the advertised zone is wrong
    for line in cal.extra:
        if not isinstance(line, ContentLine):
            continue
        if line.name == "X-WR-TIMEZONE":
            line.value = tzstr
        elif line.name == "X-WR-CALNAME" and team_from and team_to:
            line.value = line.value.replace(team_from, team_to)

    return CalendarResponse(cal)
