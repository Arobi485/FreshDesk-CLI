Welcome!

This is a project I have been working on to access the more powerful API functions of Freshdesk you cannot access from the web interface.

When starting up you will need to set some things up:
 - Any access to Freshdesk CLI will need a .env file setting up, this file will need to include a API key and domain for your freshdesk (leave the password as x)
 - If you plan on sending emails out you will also need to find your email config ID (this links the emails you are sending to a specific inbox)
 - For sending emails you will also need to set up a HTML file for the email layout, there is a simple template provided in the files (template must be named EmailTemplate.html, any styling made MUST be done inline as Freshdesk does not accept external css files)
 - If you plan on sending BCC emails then you will need to set the BCC inbox email (this will usually be the incoming email for your inbox)

Notes
 - When sending BCC emails, users cannot reply to these emails (sending single emails still works)

Requirements
 - requests
 - python-dotenv
 - InquirerPy
