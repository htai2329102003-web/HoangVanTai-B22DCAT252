# URL Cloaking & Delayed Activation — Student Guide

## Objective
Observe how one URL can return different content according to the source IP address. This lab uses only a local training page; it does not connect to an external malicious site and does not collect credentials.

## Topology

| Component | Network | Address | Expected result when opening `/` |
|---|---|---|---|
| Scanner | SCANNER_NET | `192.168.1.50` | HTTP 200, normal Supplier Workspace page |
| Server | Both | `192.168.1.100`, `10.0.0.100` | Flask server on TCP/8080 |
| Victim | USER_NET | `10.0.0.50` | HTTP 302, local training simulation page |

## Browser task
1. Start `url-cloaking-lab` using Labtainers.
2. Compare the page shown in the Scanner Browser and Victim Browser.
3. On each browser, record the URL in the address bar and the page title.
4. Open browser Developer Tools → Network and reload the root URL `/`.
5. Record the status code, `Location` header (for the victim), and final URL.
6. Explain why filtering only the scanner's first response can miss content delivered to a normal visitor.

## Expected observations
- Scanner source `192.168.1.50`: `/` returns `200 OK` with the normal workspace page.
- Victim source `10.0.0.50`: `/` returns `302 Found` with `Location: /training-simulation`, followed by `200 OK` on the local simulation page.
- The application logs each decision in the server log.

## Safety note
All displayed names and documents are fictional. The simulation form has no credential fields and the application does not store form submissions or transmit information off the lab network.
