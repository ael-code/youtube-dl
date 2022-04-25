# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import (
    js_to_json,
)


class LA7IE(InfoExtractor):
    IE_NAME = 'la7.it'
    _VALID_URL = r'''(?x)(https?://)?(?:
        (?:www\.)?la7\.it/([^/]+)/(?:rivedila7|video)/|
        tg\.la7\.it/repliche-tgla7\?id=
    )(?P<id>.+)'''

    _TESTS = [{
        # 'src' is a plain URL
        'url': 'http://www.la7.it/crozza/video/inccool8-02-10-2015-163722',
        'md5': '8b613ffc0c4bf9b9e377169fc19c214c',
        'info_dict': {
            'id': '0_42j6wd36',
            'ext': 'mp4',
            'title': 'Inc.Cool8',
            'description': 'Benvenuti nell\'incredibile mondo della INC. COOL. 8. dove “INC.” sta per “Incorporated” “COOL” sta per “fashion” ed Eight sta per il gesto  atletico',
            'thumbnail': 're:^https?://.*',
            'uploader_id': 'kdla7pillole@iltrovatore.it',
            'timestamp': 1443814869,
            'upload_date': '20151002',
        },
    }, {
        # 'src' is a dictionary
        'url': 'http://tg.la7.it/repliche-tgla7?id=189080',
        'md5': '6b0d8888d286e39870208dfeceaf456b',
        'info_dict': {
            'id': '189080',
            'ext': 'mp4',
            'title': 'TG LA7',
        },
    }, {
        'url': 'http://www.la7.it/omnibus/rivedila7/omnibus-news-02-07-2016-189077',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        player_data = self._search_regex(
            [r'(?s)videoParams\s*=\s*({.+?});', r'videoLa7\(({[^;]+})\);'],
            webpage, 'player data')
        js_sources = self._search_regex(r'src\s*:\s*({.+?})\s*,', player_data, 'sources')
        sources = self._parse_json(js_sources, video_id, transform_source=js_to_json)

        formats = []
        if 'mp4' in sources:
            mp4_url = sources['mp4'].replace("vodpmd.la7.it.edgesuite.net/", "vodpkg.iltrovatore.it/local/mp4/");
            mp4_url = mp4_url.replace("http://", "https://")
            formats.append({
                'url': mp4_url,
                'ext': 'mp4',
                'format_id': 'mp4-direct',
                'format_note': 'mp4 direct download (usually lower quality)',
                'preference': -50,
                })

        if 'm3u8' in sources:
            base_url = sources['m3u8']
            base_url = base_url.replace("csmil", "urlset")
            base_url = base_url.replace("http://", "https://")

            dash_url = base_url.replace("la7-vh.akamaihd.net/i/", "awsvodpkg.iltrovatore.it/local/dash/")
            dash_url = dash_url.replace("master.m3u8", "manifest.mpd")
            formats.extend(self._extract_mpd_formats(dash_url, video_id, mpd_id='dash', fatal=False))

            m3u8_url = base_url.replace("la7-vh.akamaihd.net/i/", "awsvodpkg.iltrovatore.it/local/hls/")
            formats.extend(self._extract_m3u8_formats(m3u8_url, video_id, m3u8_id='hls', fatal=False))

        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': self._og_search_title(webpage, default=None),
            'description': self._og_search_description(webpage, default=None),
            'thumbnail': self._og_search_thumbnail(webpage, default=None),
            'formats': formats
        }
