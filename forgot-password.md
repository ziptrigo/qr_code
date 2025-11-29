# Forgot password flow

In the login flow I want to add a "forgot password" flow.

Below the login button, add a link to the forgot password flow.
The flow should be:

In a new page, ask for the email address.
There's an "ok" button that confirms the email address and a "cancel" button that returns to the
login page.

After clicking "ok":
* The user sees a message stating that if the account exists, an email will be sent to it with a
  password reset link.  After this message, there's no other feedback or action.
* At this point, in the backend, an email is sent to the user.

Email:
Under qr_code/static/emails add a `password_reset` file. This file is to be a template for the
email. The template should have variables to be replaced. The suggestion is to use Jinja2, but
other suggestions are welcome.

The template should have:
* Subject
* Body in HTML format
* Body in plain text format

To send the email, abstract the sending logic.
We're going to implement that logic using AWS SES at this point, but later this may be changed and 
we want this change to be transparent to the rest of the code.

In the email being send, there's a link to reset the password.
This link is to be valid for a few hours. Implement a mechanism to invalidate this link after that
time has elapsed.  This time should be configurable.

upon clicking the link, if the account exists, the user is redirected to a page where he can set a
new password.  Create a page where the user can set the new password (with password and password
confirmation).
If the account doesn't exist, the user is redirected to the login page.
If the account exists, but the link has expired, the user is redirected to a page that says that
the link has expired, with an ok button that redirects to the login page.

Ask any clarification questions as needed.