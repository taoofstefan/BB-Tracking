from __future__ import annotations

import pytest

from service import parse_optional_positive_float, safe_video_suffix


def test_parse_optional_positive_float_handles_empty_values():
    assert parse_optional_positive_float(None, "scale") is None
    assert parse_optional_positive_float("", "scale") is None


def test_parse_optional_positive_float_rejects_non_positive_values():
    with pytest.raises(ValueError, match="scale"):
        parse_optional_positive_float("0", "scale")


def test_parse_optional_positive_float_parses_positive_values():
    assert parse_optional_positive_float("12.5", "scale") == pytest.approx(12.5)


def test_safe_video_suffix_allows_known_video_suffixes():
    assert safe_video_suffix("lift.mp4") == ".mp4"
    assert safe_video_suffix("lift.MOV") == ".mov"
    assert safe_video_suffix("lift.txt") == ".mp4"
    assert safe_video_suffix(None) == ".mp4"


def test_create_app_health_endpoint_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())

    assert client.get("/health").json() == {"status": "ok"}


def test_create_app_health_endpoint_allows_dev_cors_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())
    response = client.get("/health", headers={"Origin": "file://"})

    assert response.headers["access-control-allow-origin"] == "*"
