# callback-phishing - Labtainer configuration pack

This ZIP contains the configuration layer for the three-container Callback Phishing / TOAD lab.
It follows the same layout used in the earlier Labtainer exercises: `config/`, `instr_config/`, `docs/`, and `dockerfiles/`.

## Network and containers

- `CALLBACK_NET`: `172.21.0.0/24`, gateway `172.21.0.100`
- `attacker-srv`: `172.21.0.2`
- `support-bot`: `172.21.0.3`
- `victim-pc`: `172.21.0.4`

## Assessment goals

The six goals are exactly:

1. `email_sent`
2. `victim_called`
3. `script_delivered`
4. `shell_connected`
5. `data_exfiltrated`
6. `lab_complete`

## Assessment contract

The Python source must write these exact markers when the corresponding event really occurs:

- `attacker_callback.log`: `CALLBACK_CONNECTED`, `SECRET_DATA_RECEIVED`
- `support.log`: `VICTIM_CONNECTED`, `SUPPORT_GUIDANCE_SENT`
- `victim_mail.log`: `EMAIL_RECEIVED`
- `victim_callback.log`: `CALLBACK_SENT`

Do not print these markers merely to satisfy checkwork. They are intended to represent real events inside the isolated lab.

## Placement

Extract the `callback-phishing` directory into the Labtainer `labs/` directory during development. The exercise source files are not included in this configuration-only package.
