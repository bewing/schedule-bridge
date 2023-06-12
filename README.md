# schedule-bridge
A FastAPI application for useful live schedules from common league management platforms

This is primarily a QoL application to massage data from leagues that I deal with into a constant, correct format for BenchApp to monitor/import.

Events are harvested from the API of the provider, time-corrected into actual tzinfo datetimes, possibly renamed to match BenchApp team name, and
then served up as an ICS file for BenchApp to consume.

## Supported league management software
### Gamesheet
Gamesheet has a pretty good API for harvesting events.  You will need to know your season's ID, and the ID of the team you're on.
My provider gives UTC timestamps of local times (!), so I strip the trailing Z from the ISO timestamp and apply a new timezone.

### Daysmart
Note:  Daysmart will remove events from their API a few days after they occur.  Benchapp will not automatically remove missing events, but keep this in mind.

### Deployment
A Dockerfile is provided.  All else is left as an exercise for the user.

## Development Requirements
- python 3.10+
- pip
- poetry
