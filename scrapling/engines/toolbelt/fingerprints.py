"""
Functions related to generating headers and fingerprints generally.
"""

from functools import lru_cache
from platform import system as platform_system

from browserforge.headers import Browser, HeaderGenerator
from browserforge.headers.generator import SUPPORTED_OPERATING_SYSTEMS

from scrapling.core._types import Dict, Literal, Tuple

__OS_NAME__ = platform_system()
OSName = Literal["linux", "macos", "windows"]
# Current versions hardcoded for now (Playwright doesn't allow us to know the
# browser version without launching it).
chromium_version = 149
chrome_version = 149


@lru_cache(1, typed=True)
def get_os_name() -> OSName | Tuple:
    """Return the current OS in BrowserForge's expected format."""
    match __OS_NAME__:  # pragma: no cover
        case "Linux":
            return "linux"
        case "Darwin":
            return "macos"
        case "Windows":
            return "windows"
        case _:
            return SUPPORTED_OPERATING_SYSTEMS


def _platform_user_agent(version: int, os_name: OSName | Tuple) -> str:
    """Create a deterministic desktop Chrome user agent for the host OS."""
    if os_name == "windows":
        platform = "Windows NT 10.0; Win64; x64"
    elif os_name == "macos":
        platform = "Macintosh; Intel Mac OS X 10_15_7"
    else:
        platform = "X11; Linux x86_64"

    return (
        f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
    )


def _relaxed_chrome_headers(version: int, os_name: OSName | Tuple) -> Dict:
    """Generate headers when BrowserForge lacks an exact version datapoint.

    BrowserForge's bundled traffic data can lag behind Playwright's Chromium
    release. In that case, retain the requested operating system and desktop
    Chrome constraints but allow BrowserForge to choose an available version.
    The browser identity fields are then aligned with the installed Chromium
    version so importing Scrapling never fails solely because its data model is
    behind the browser release.
    """
    try:
        headers = HeaderGenerator(browser="chrome", os=os_name, device="desktop").generate()
    except ValueError:
        # Last-resort generation keeps the service available on unusual hosts.
        headers = HeaderGenerator(browser="chrome", device="desktop").generate()

    headers["User-Agent"] = _platform_user_agent(version, os_name)
    headers["sec-ch-ua"] = (
        f'"Not_A Brand";v="99", "Chromium";v="{version}", '
        f'"Google Chrome";v="{version}"'
    )
    headers["sec-ch-ua-mobile"] = "?0"
    platform_name = "Windows" if os_name == "windows" else "macOS" if os_name == "macos" else "Linux"
    headers["sec-ch-ua-platform"] = f'"{platform_name}"'
    return headers


def generate_headers(browser_mode: bool | str = False) -> Dict:
    """Generate realistic browser-like headers using BrowserForge.

    Exact browser-version matching is attempted first. If BrowserForge's data
    does not yet include the installed Chromium version, browser-mode requests
    fall back to a relaxed Chrome profile instead of crashing at import time.
    """
    os_name = get_os_name()
    version = chrome_version if browser_mode == "chrome" else chromium_version
    browsers = [Browser(name="chrome", min_version=version, max_version=version)]

    if not browser_mode:
        os_name = ("windows", "macos", "linux")
        browsers.extend(
            [
                Browser(name="firefox", min_version=142),
                Browser(name="edge", min_version=140),
            ]
        )

    try:
        return HeaderGenerator(browser=browsers, os=os_name, device="desktop").generate()
    except ValueError:
        if browser_mode:
            return _relaxed_chrome_headers(version, os_name)
        # Non-browser requests are not tied to the local Chromium binary, so a
        # fully relaxed desktop profile is preferable to terminating the call.
        return HeaderGenerator(device="desktop").generate()


__default_useragent__ = generate_headers(browser_mode=False).get("User-Agent")
