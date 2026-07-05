from src.data.sites import SITES
from src.ui.widgets.leaflet_map_view import _build_html


def test_build_html_contains_all_sites():
    html = _build_html()
    for site in SITES:
        assert site.site_id in html
        assert site.name in html


def test_build_html_uses_osm_tiles():
    html = _build_html()
    assert "tile.openstreetmap.org" in html
    assert "leaflet" in html.lower()
