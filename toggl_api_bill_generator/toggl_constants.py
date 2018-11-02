ENVFileTemplate="""
#!/usr/bin/env bash

# https://github.com/toggl/toggl_api_docs
export TOGGL_API_TOKEN=''

# Sometimes you have a billable rate and a non-billable rate.
export BILLABLE_RATE='10.0'
export NON_BILLABLE_RATE='5.0'
export FULFILLMENT_DELAY='30'

# Make sure to iterate the invoice number with each use
export INVOICE_NUMBER=space-needle-0
export OUTPUT_DIR=$PWD
export INVOICE_FILENAME='Invoice.pdf'

export SERVICE_PROVIDER='The Freemont Troll'
export SERVICE_PROVIDER_EMAIL='freemont-troll@jbcurtin.io'
export SERVICE_PROVIDER_PHONE=''
export SERVICE_PROVIDER_ADDRESS='Troll Ave N'
export SERVICE_PROVIDER_ADDRESS_TWO='#office'
export SERVICE_PROVIDER_CITY='Seattle'
export SERVICE_PROVIDER_STATE='WA'
export SERVICE_PROVIDER_POSTAL='98103'

export RECIPIENT='Seattle Space Needle'
export RECIPIENT_EMAIL='space-needle@jbcurtin.io'
export RECIPIENT_PHONE=''
export RECIPIENT_ADDRESS='400 Broad St'
export RECIPIENT_ADDRESS_TWO='#office'
export RECIPIENT_CITY='Seattle'
export RECIPIENT_STATE='WA'
export RECIPIENT_POSTAL='98109'
"""
