# Data and credential handling

1. NASA Earthdata bearer tokens are secret. Do **not** commit them, include them in example logs, put them in test fixtures, or store them in a chat/transcript used for public submission.
2. Authenticate interactively through the research scripts or through a carefully protected local credential store. Never put the token into a GitHub remote URL or source-code constant.
3. Treat authenticated download URLs and redirect URLs as potentially short-lived signed URLs. Do not paste them into documentation.
4. Use the smallest required date/AOI and keep downloaded HDF5/GeoTIFF source files local; commit source identifiers and provenance, not gigabytes of raw data.
5. Do not assert any numerical NISAR change findings until radar measurement arrays have been extracted and checked.
6. If a credential was shared in a chat, revoke/rotate it after the relevant session. This repo contains **no** Earthdata token.
