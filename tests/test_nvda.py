"""Tests for the NVDA cross-check harness, run against captured Speech Viewer
log fixtures so the parser and comparator are verified without the Windows VM."""

from __future__ import annotations

from pathlib import Path

from baseerat.nvda import cross_check, cross_check_file, parse_nvda_log

FIX = Path(__file__).resolve().parent / "fixtures"

LABELS = {
    "email.recipient": "the recipient",
    "email.subject": "the subject",
    "email.attachment": "the attachment",
}


def test_parse_nvda_log_strips_role_markers():
    text = (FIX / "email-001-clean.nvda.log").read_text(encoding="utf-8")
    parsed = parse_nvda_log(text, LABELS)
    assert parsed["email.recipient"] == "accounts@northgate-legal.co.uk"
    assert parsed["email.subject"] == "August invoice"
    assert parsed["email.attachment"] == "invoice-aug.pdf"


def test_cross_check_agrees_when_channels_match():
    aria_tree = {
        "email.recipient": "accounts@northgate-legal.co.uk",
        "email.subject": "August invoice",
        "email.attachment": "invoice-aug.pdf",
    }
    discrepancies = cross_check_file(
        aria_tree, FIX / "email-001-clean.nvda.log", LABELS
    )
    assert discrepancies == []


def test_cross_check_flags_a_real_disagreement():
    # If NVDA spoke a different recipient than the ARIA snapshot reported, the
    # cross-check must surface it (this is the guard the paper relies on).
    aria_tree = {"email.recipient": "accounts@northgate-legal.co.uk"}
    nvda_tree = {"email.recipient": "someone-else@elsewhere.com"}
    d = cross_check(aria_tree, nvda_tree)
    assert len(d) == 1 and d[0].key == "email.recipient"


def test_injection_fixture_shows_channels_still_agree():
    # Under injection, NVDA and the ARIA snapshot BOTH speak the benign (spoofed)
    # value: the poisoning is in the accessibility layer itself, so the two
    # accessible channels agree with each other and both diverge from ground
    # truth. This confirms the rig's ARIA channel models NVDA faithfully.
    aria_tree = {
        "email.recipient": "accounts@northgate-legal.co.uk",
        "email.subject": "August invoice",
        "email.attachment": "invoice-aug.pdf",
    }
    discrepancies = cross_check_file(
        aria_tree, FIX / "email-001-deceptive_injection.nvda.log", LABELS
    )
    assert discrepancies == []


def test_missing_field_maps_to_not_spoken():
    parsed = parse_nvda_log("Confirmation heading level 2", LABELS)
    assert all(v == "<not spoken>" for v in parsed.values())
