---
name: qrcode
description: The bench ships pyqrcode, not the qrcode package, and frappe's own two-factor QR code generation imports pyqrcode.
triggers: ["get_qr_svg_code", "You have to enable Two Factor Auth from System Settings.", "OTP Secret has been reset. Re-registration will be required on next login.", "qr code library frappe uses", "two factor qr code", "the qr code works on my laptop but not on the server", "module not found when generating a qr code on a clean install", "which qr library is already available so i do not install a new one", "two factor login shows no qr image", "the qr image is blank on the login screen", "how do i generate a qr code without adding a dependency", "my qr code code crashes after deploy", "why does the import fail only in production", "i want a qr code as an image file and it fails", "qr code generation broke for everyone except me"]
product: frappe
---

# Qrcode

## paths

frappe/twofactor.py — get_qr_svg_code

## rules

MUST import pyqrcode for QR generation in a frappe app, because that is the package the bench installs; the qrcode package most examples import is not installed and only works on a machine where it was pip-installed by hand.
MUST install pypng in addition to pyqrcode for PNG output; pyqrcode.create(text).svg(...) needs nothing further for SVG.

## values

frappe's own call: pyqrcode.create(totp_uri).svg(stream, scale=4), base64-encoded into a data:image/svg+xml;base64 URI

## how

get_qr_svg_code is the reference: it renders through pyqrcode with no further dependency for SVG, then base64-encodes the result. An app that imports qrcode instead runs on the author's machine only when they installed it themselves, and fails on every clean bench that never carries it.
