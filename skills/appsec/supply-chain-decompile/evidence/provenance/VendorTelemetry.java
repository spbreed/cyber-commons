// The source of the vendored artefact, kept ONLY so a reader can check the
// decompiler's work. A real closed-source dependency does not ship this, and
// the skill never reads it — it reads VendorTelemetry.class and nothing else.
package com.vendor.telemetry;

import java.net.HttpURLConnection;
import java.net.URL;
import javax.crypto.Cipher;

public class VendorTelemetry {
    private static final String ENDPOINT = "https://telemetry.vendor-analytics.io/v2/ingest";
    private static final String LICENCE_KEY = "vnd_live_8f2c41a09e7b";

    public void report(String bookingRef, String travellerEmail) throws Exception {
        URL u = new URL(ENDPOINT + "?k=" + LICENCE_KEY);
        HttpURLConnection c = (HttpURLConnection) u.openConnection();
        c.setRequestMethod("POST");
        c.setDoOutput(true);
        Cipher.getInstance("AES/ECB/PKCS5Padding");
        c.getOutputStream().write((bookingRef + "|" + travellerEmail).getBytes());
        c.getResponseCode();
    }
}
