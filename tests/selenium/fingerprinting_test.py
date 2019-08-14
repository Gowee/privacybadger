#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

import pbtest


class FingerprintingTest(pbtest.PBSeleniumTest):
    """Tests to make sure fingerprinting detection works as expected."""

    def detected_fingerprinting(self, domain):
        return self.js((
            "let bg = chrome.extension.getBackgroundPage(),"
            "  tracker_origin = window.getBaseDomain(arguments[0]);"
            ""
            "return ("
            "  Object.keys(bg.badger.tabData).some(tab_id => {"
            "    let fpData = bg.badger.tabData[tab_id].fpData;"
            "    return fpData &&"
            "      fpData.hasOwnProperty(tracker_origin) &&"
            "      fpData[tracker_origin].canvas &&"
            "      fpData[tracker_origin].canvas.fingerprinting === true;"
            "  })"
            ");"
        ), domain);

    def detected_tracking(self, domain, page_url):
        return self.js((
            "let bg = chrome.extension.getBackgroundPage(),"
            "  tracker_origin = window.getBaseDomain(arguments[0]),"
            "  site_origin = window.getBaseDomain((new URI(arguments[1])).host),"
            "  map = bg.badger.storage.snitch_map.getItemClones();"
            ""
            "return ("
            "  map.hasOwnProperty(tracker_origin) &&"
            "  map[tracker_origin].indexOf(site_origin) != -1"
            ");"
        ), domain, page_url)

    # TODO can fail because our content script runs too late: https://crbug.com/478183
    @pbtest.repeat_if_failed(3)
    def test_canvas_fingerprinting_detection(self):
        PAGE_URL = (
            "https://gitcdn.link/cdn/ghostwords/"
            "ff6347b93ec126d4f73a9ddfd8b09919/raw/6b215b3f052115d36831ecfca758081ca7da7e37/"
            "privacy_badger_fingerprint_test_fixture.html"
        )
        FINGERPRINTING_DOMAIN = "cdn.jsdelivr.net"

        # visit the page
        self.load_url(PAGE_URL)

        # open the options page for querying
        self.load_url(self.options_url)

        # check that we detected the fingerprinting domain as a tracker
        self.assertTrue(
            self.detected_tracking(FINGERPRINTING_DOMAIN, PAGE_URL),
            "Canvas fingerprinting domain was detected as a tracker."
        )

        # check that we detected canvas fingerprinting
        self.assertTrue(
            self.detected_fingerprinting(FINGERPRINTING_DOMAIN),
            "Canvas fingerprinting domain was detected as a fingerprinter."
        )


if __name__ == "__main__":
    unittest.main()
