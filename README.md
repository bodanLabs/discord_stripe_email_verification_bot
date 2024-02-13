**Discord Verification Bot**

Description
This Discord bot automates the verification process for users on a Discord server. It verifies users by checking their email against active subscriptions in a Stripe account and assigns a specific role to verified users. The bot also supports commands for managing email verification status and querying subscription status.

Features
Email Verification: Users can verify their identity by providing the email associated with their active subscription.
Role Assignment: Automatically assigns a predefined role to users with an active subscription.
Admin Commands: Special commands for administrators to manage user verifications and check database entries.
Subscription Check: Periodically checks the subscription status of verified users and updates their roles accordingly.

Installation
Clone the repository to your local machine.
Install the required dependencies by running pip install -r requirements.txt in your terminal.
Create a `config.json` file in the root directory with the following structure:
json
Copy code
{
  "token": "YOUR_BOT_TOKEN",
  "stripeKey": "YOUR_STRIPE_API_KEY",
  "email": "YOUR_EMAIL",
  "emailPassword": "YOUR_EMAIL_PASSWORD",
  "roleName": "ROLE_NAME_FOR_VERIFIED_USERS",
  "guildID": "YOUR_GUILD_ID",
  "ownerID": "DISCORD_OWNER_ID",
  "devID": "DISCORD_DEV_ID"
}
Set up your SQLite database by running the provided SQL script to create the necessary tables.
Run the bot using python bot.py.
Usage
After the bot is running, it listens for commands and interactions to verify users. The main commands include:

/setup: Initializes the verification process by sending a message with verification instructions.
/delete_email: Allows users to remove their email from the database and restart the verification process.
/admin_delete_email: Admin command to delete a user's email from the database.
/check_email: Checks and displays the email assigned to the user's Discord account.
/admin_check_email: Admin command to check the email assigned to any user's Discord account.
/admin_get_all: Admin command to export all database entries to a file.
The bot also includes a task loop that periodically checks the subscription status of all verified users and updates their roles accordingly.

Contributing
Contributions to this project are welcome! Please fork the repository and submit a pull request with your proposed changes.

License
This project is open source and available under the MIT License.
