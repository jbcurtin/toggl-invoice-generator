# Bill Generator using Toggl.com API

A script that will generate a PDF from Toggl.com API. Easy to automate from CRON or use from
26 the Command Line Interface. Following Flask App Factory Pattern and 12 Factor App best practices. All configuration
can be accomplished through Environment Variables.

Having a script to automate generation of bills helps reduce time and imporve
efficiency in communication. Using this tool, you'll be able to send bills once
a month without much thought as long as you continue to enter your hours
diligently throughout the month.

## Quickstart

```
pip install toggl-api-bill-generator
toggl-bill-gen -g
source dev.sh
toggl-bill-gen -o month
```

## Functionality Breakdown

| Logical Type | ENVVar Names|
| --- | --- |
| Service Provider| SERVICE_PROVIDER, SERVICE_PROVIDER_EMAIL, SERVICE_PROVIDER_PHONE, SERVICE_PROVIDER_ADDRESS, SERVICE_PROVIDER_ADDRESS_TWO, SERVICE_PROVIDER_CITY, SERVICE_PROVIDER_STATE, SERVICE_PROVIDER_POSTAL|
| Recipient| RECIPIENT, RECIPIENT_EMAIL, RECIPIENT_PHONE, RECIPIENT_ADDRESS, RECIPIENT_ADDRESS_TWO, RECIPIENT_CITY, RECIPIENT_STATE, RECIPIENT_POSTAL|
| Misc| FULFILLMENT_DELAY, INVOICE_NUMBER |
