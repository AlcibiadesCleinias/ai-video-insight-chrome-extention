AI Video Insight - Google Chrome Extension
---

# Could it be improved?
- frontend <-> backend interaction improve: e.g. frontend -> send video id (or id), then checking API if each of summary 
is ready, ratio is ready, etc.
- send video ids to make backend preload all desirable info
- caching: {on API level, for data fetching concurrent process}
- add simple gridy models
- use different models, and use the first answer available with e.g. asyncio.FIRST_COMPLETED

# ToDo
- [ ] # TODO: api could rely on user open token rather than on centralised token.
- [ ] tests
- [ ] add info about votes from comments to AI.
- [ ] youtube info fetchers consists of blocking code (not python async compatible)