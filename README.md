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


## Tutorials

### Integrate with Sonnar
coming soon...

## Endpoints

<details>
    <summary><code>GET</code> <code>/tgx/api</code></summary>
    
#### Parameters

>|name|type     |data type    | description |
>|----|---------|-------------|-------------|
>|t   |required |string       |Type of search that sshould be one ot the following item (`caps`, `search`, `tvsearch`, `movie`)|
>|q   |required |string       |Serach terms (query). The name of the movie or tv show for example: `the lord of the rings`| 


#### Responses
>| http code | content-type | response |
>|-----------|--------------|----------|
>|200        | application/rss+xml | XML string |

#### Example cURL
> ```shell
> curl -X 'GET' 'http://localhost:9876/tgx/api?t=search&q=lord%20of%20the%20rings' -H 'accept: application/json'
> ```

<details>
  <summary>Content example</summary>

  ```xml
<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
  <rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:torznab="http://torznab.com/schemas/2015/feed" version="2.0">
    <channel>
      <atom:link href="http://localhost" rel="self" type="application/atom+xml"/>
      <title>TGx</title>
      <description>Torrent Galaxy site</description>
      <link>https://torrentgalaxy.one</link>
      <language>en-US</language>
      <category>search</category>
      <item>
        <title>The Lord of the Rings The Fellowship of the Ring 2001 Extended Cut BluRay 1</title>
        <guid>magnet:?xt=urn:btih:CE2279B546802321EAF95674249D869C3F833F25&amp;dn=The%20Lord%20of%20the%20Rings%20The%20Fellowship%20of%20the%20Ring%202001%20Extended%20Cut%20BluRay%201&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce</guid>
        <jackettindexer id="TGx">Torrent Galaxy</jackettindexer>
        <type>public</type>
        <description>The Lord of the Rings The Fellowship of the Ring 2001 Extended Cut BluRay 1 (leechers: 33)</description>
        <comments>
        </comments>
        <pubDate>Thu, 03 Jul 2025 14:15:37 +0000</pubDate>
        <size>14643762600</size>
        <link>magnet:?xt=urn:btih:CE2279B546802321EAF95674249D869C3F833F25&amp;dn=The%20Lord%20of%20the%20Rings%20The%20Fellowship%20of%20the%20Ring%202001%20Extended%20Cut%20BluRay%201&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce</link>
        <category>Movies</category>
        <enclosure url="magnet:?xt=urn:btih:CE2279B546802321EAF95674249D869C3F833F25&amp;dn=The%20Lord%20of%20the%20Rings%20The%20Fellowship%20of%20the%20Ring%202001%20Extended%20Cut%20BluRay%201&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce" type="application/x-bittorrent"/>
        <torznab:attr name="category" value="Movies"/>
        <torznab:attr name="seeders" value="16"/>
        <torznab:attr name="peers" value="16"/>
        <torznab:attr name="leechers" value="33"/>
        <torznab:attr name="magneturl" value="magnet:?xt=urn:btih:CE2279B546802321EAF95674249D869C3F833F25&amp;dn=The%20Lord%20of%20the%20Rings%20The%20Fellowship%20of%20the%20Ring%202001%20Extended%20Cut%20BluRay%201&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce"/>
        <torznab:attr name="downloadvolumefactor" value="0"/>
        <torznab:attr name="uploadvolumefactor" value="1"/>
        <torznab:attr name="size" value="14643762600"/>
      </item>
      <item>
        <title>Kiff.Lore.of.the.Ring.Light.2025.1080p.WEB.H264-RVKD</title>
        <guid>magnet:?xt=urn:btih:64895277F1D520EAB33B101F00F4ED75E0D07D19&amp;dn=Kiff.Lore.of.the.Ring.Light.2025.1080p.WEB.H264-RVKD&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce</guid>
        <jackettindexer id="TGx">Torrent Galaxy</jackettindexer>
        <type>public</type>
        <description>Kiff.Lore.of.the.Ring.Light.2025.1080p.WEB.H264-RVKD (leechers: 13)</description>
        <comments>
        </comments>
        <pubDate>Mon, 30 Jun 2025 16:54:20 +0000</pubDate>
        <size>692426065</size>
        <link>magnet:?xt=urn:btih:64895277F1D520EAB33B101F00F4ED75E0D07D19&amp;dn=Kiff.Lore.of.the.Ring.Light.2025.1080p.WEB.H264-RVKD&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce</link>
        <category>Movies</category>
        <enclosure url="magnet:?xt=urn:btih:64895277F1D520EAB33B101F00F4ED75E0D07D19&amp;dn=Kiff.Lore.of.the.Ring.Light.2025.1080p.WEB.H264-RVKD&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce" type="application/x-bittorrent"/>
        <torznab:attr name="category" value="Movies"/>
        <torznab:attr name="seeders" value="8"/>
        <torznab:attr name="peers" value="8"/>
        <torznab:attr name="leechers" value="13"/>
        <torznab:attr name="magneturl" value="magnet:?xt=urn:btih:64895277F1D520EAB33B101F00F4ED75E0D07D19&amp;dn=Kiff.Lore.of.the.Ring.Light.2025.1080p.WEB.H264-RVKD&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce"/>
        <torznab:attr name="downloadvolumefactor" value="0"/>
        <torznab:attr name="uploadvolumefactor" value="1"/>
        <torznab:attr name="size" value="692426065"/>
      </item>
      <item>
        <title>Kiff.Lore.of.the.Ring.Light.2025.720p.WEB.H264-RVKD</title>
        <guid>magnet:?xt=urn:btih:89DB7D2E4095F6649B4031A7384C2576ADFF0710&amp;dn=Kiff.Lore.of.the.Ring.Light.2025.720p.WEB.H264-RVKD&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce</guid>
        <jackettindexer id="TGx">Torrent Galaxy</jackettindexer>
        <type>public</type>
        <description>Kiff.Lore.of.the.Ring.Light.2025.720p.WEB.H264-RVKD (leechers: 23)</description>
        <comments>
        </comments>
        <pubDate>Mon, 30 Jun 2025 15:13:09 +0000</pubDate>
        <size>428959297</size>
        <link>magnet:?xt=urn:btih:89DB7D2E4095F6649B4031A7384C2576ADFF0710&amp;dn=Kiff.Lore.of.the.Ring.Light.2025.720p.WEB.H264-RVKD&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce</link>
        <category>Movies</category>
        <enclosure url="magnet:?xt=urn:btih:89DB7D2E4095F6649B4031A7384C2576ADFF0710&amp;dn=Kiff.Lore.of.the.Ring.Light.2025.720p.WEB.H264-RVKD&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce" type="application/x-bittorrent"/>
        <torznab:attr name="category" value="Movies"/>
        <torznab:attr name="seeders" value="41"/>
        <torznab:attr name="peers" value="41"/>
        <torznab:attr name="leechers" value="23"/>
        <torznab:attr name="magneturl" value="magnet:?xt=urn:btih:89DB7D2E4095F6649B4031A7384C2576ADFF0710&amp;dn=Kiff.Lore.of.the.Ring.Light.2025.720p.WEB.H264-RVKD&amp;tr=udp%3A%2F%2Ftracker1.bt.moack.co.kr%3A80%2Fannounce&amp;tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.theoks.net%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&amp;tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&amp;tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&amp;tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce"/>
        <torznab:attr name="downloadvolumefactor" value="0"/>
        <torznab:attr name="uploadvolumefactor" value="1"/>
        <torznab:attr name="size" value="428959297"/>
      </item>
    </channel>
  </rss>
```
</details>

</details>


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
