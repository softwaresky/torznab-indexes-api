# Tornazb indexer api

FastAPI service finding torrent from the sites same as **[jackett](https://github.com/Jackett/Jackett)**.
Basically scrape / parse site and return the data in **[tornazb structure](https://torznab.github.io/spec-1.3-draft/torznab/Specification-v1.3.html#torznab-api-specification)**  (.XML) 
This service can be running locally and integrate with **Sonnar**,  **Raddar** or any sistem that support tornazb format

### Supported Torrents / Trackers:

<details>
<summary>Public Trackers</summary>
    
* TorrentGalaxy [TGX](https://torrentgalaxy.one/)
    
</details>

This can be expanded with other torrent site that needs scraping.


## Integrate with Sonnar
coming soon...

## Endpoints
- [Search Query](./docs/search_query.md): `GET /tgx/api`




## Build and deploy
This can be locally deployed on your MiniPC, RaspberryPi or some server that support docker.

1. Build docker images using this command
   ```shell
   docker build -t torznab-indexes-api .
   ```
2. Running docker container using host port 8899 this can change. The container port should be 8000.
   ```shell
   docker run --name torznab-indexes-api --port 8899:8000 torznab-indexes-api
   ```
