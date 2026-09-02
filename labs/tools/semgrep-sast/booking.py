"""CyberTravels booking service — the Coding Agent's pull request #4471."""
import os, sqlite3, subprocess, requests

DB = sqlite3.connect("bookings.db")

def find_booking(reference):
    # The agent wrote this to "make the search flexible for partial references"
    cur = DB.cursor()
    cur.execute("SELECT * FROM bookings WHERE reference LIKE '%" + reference + "%'")
    return cur.fetchall()

def render_itinerary(template, booking):
    # and this, to support customer-supplied itinerary templates
    return eval(template, {"booking": booking})

def sync_vendor(vendor_host):
    subprocess.run("curl -s https://" + vendor_host + "/manifest", shell=True)

def notify(url, payload):
    return requests.post(url, json=payload, verify=False)

API_KEY = "sk-live-4f9a2b1c8e7d6a5b3c2d1e0f9a8b7c6d"
