import json
import asyncio
from discord import ui, app_commands
from discord.ui import Button, View
import discord
from discord.ext import tasks
import smtplib
from email.mime.text import MIMEText
import random
import sqlite3
import stripe

f = open('config.json')
config = json.load(f)
bot_token = config['token']
stripe_key = config['stripeKey']
main_email = config['email']
mail_password = config['emailPassword']
role_name = config['roleName']
guild_id = config['guildID']
owner_id = config['ownerID']
developer_id = config['devID']

stripe.api_key = stripe_key

emoji = "🦾"

db = sqlite3.connect('database.sqlite')
cursor = db.cursor()

TOKEN = bot_token

intents = discord.Intents.all()
colors = [1752220, 1146986, 3066993, 2067276, 3447003, 2123412, 10181046, 7419530, 15277667, 11342935, 15844367,
          12745742, 15105570, 11027200, 15158332, 10038562, 9807270, 9936031, 8359053, 12370112, 3426654, 2899536,
          16776960]
color = 0xFF10F0


class client(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=guild_id))
            self.synced = True
            print(f"We have logged in as {self.user}.")


aclient = client()
tree = app_commands.CommandTree(aclient)


class modal1(ui.Modal, title="Verify"):
    email = ui.TextInput(label="The Email you bought the service with", style=discord.TextStyle.short,
                         placeholder="email@email.xyz", required=True, max_length=35)

    async def on_submit(self, interaction: discord.Interaction):
        all = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        length = 10
        verification_code = "".join(random.sample(all, length))
        cursor.execute(f"SELECT email FROM users WHERE email = '{self.email}'")
        checkEmail = cursor.fetchone()
        if checkEmail is None:
            cursor.execute(f"SELECT email FROM users WHERE userID = '{interaction.user.id}'")
            check_user = cursor.fetchone()
            if check_user is None:
                cursor.execute(
                    f"""INSERT INTO users (userID,email,emailCode) VALUES ("{interaction.user.id}","{self.email}","{verification_code}")""")
                db.commit()

                check_button = Button(custom_id="check", emoji=emoji)

                async def check_button_callback(interaction):
                    await interaction.response.send_modal(modal2())

                check_button.callback = check_button_callback
                view = View(timeout=None)
                view.add_item(check_button)

                embed = discord.Embed(title=f"Great, {interaction.user.name}.",
                                      description=f"Thank you for going through our verification system,\n"
                                                  f"In order to continue with the verification, we sent you a code to your email: **{self.email}**\n"
                                                  f"Please use the button from this message to confirm your email by adding the code.\n"
                                                  f"If you encounter any issue, please reach out to any of our admins.")
                await interaction.response.defer()
                await asyncio.sleep(0)
                await interaction.followup.send(embed=embed, ephemeral=True, view=view)
                smtp_ssl_host = 'smtp.gmail.com'
                smtp_ssl_port = 465
                username = main_email
                password = mail_password
                sender = main_email
                target = f'{self.email}'

                msg = MIMEText(f'Your verification code is: {verification_code}')
                msg['Subject'] = 'Verification Code'
                msg['From'] = main_email
                msg['To'] = target

                server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
                server.login(username, password)
                server.sendmail(sender, target, msg.as_string())
                server.quit()
            else:
                embed = discord.Embed(title=f"Ups, {interaction.user.name}, something went wrong.",
                                      description="We see that you already have an email assigned to your discord account.\n"
                                                  "If you want to delete that, please use **/delete_email**\n"
                                                  "If you think this is a problem, please reach out to any of our admins.")
                await interaction.response.defer()
                await asyncio.sleep(0)
                await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=f"Ups, {interaction.user.name}, something went wrong.",
                                  description="We see that this email is already assigned to another user.\n"
                                              "If you think this is a mistake, please reach out to any of our admins")
            await interaction.response.defer()
            await asyncio.sleep(0)
            await interaction.followup.send(embed=embed, ephemeral=True)


class modal2(ui.Modal, title="Check Email"):
    cod = ui.TextInput(label="Insert the code from email", style=discord.TextStyle.short, placeholder="0000000000",
                       required=True, max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        cursor.execute(f"SELECT emailCode FROM users WHERE userID = '{interaction.user.id}'")
        emailCode = cursor.fetchone()[0]
        if str(emailCode) == str(self.cod):
            cursor.execute(f"SELECT email FROM users WHERE userID = '{interaction.user.id}'")
            userEmail = cursor.fetchone()[0]
            query = stripe.Customer.search(query=f"email:'{userEmail}'")

            x = 0

            for sub in query['data']:
                subs = stripe.Subscription.list(limit=10, customer=sub['id'], status="active")
                if len(subs['data']) >= 1:
                    x += 1
                else:
                    x += 0
            if x >= 1:
                status = True
            else:
                status = False
            if status == True:
                guild = interaction.guild
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                member = guild.get_member(interaction.user.id)
                await member.add_roles(role)
                await interaction.response.defer()
                await asyncio.sleep(0)
                await interaction.followup.send("Congrats! We found your subscription and you got the right role.\n"
                                                "If you can't see the role, please reach out to any of our admins.",
                                                ephemeral=True)
            else:
                await interaction.response.defer()
                await asyncio.sleep(0)
                await interaction.followup.send(
                    "Unfortunately we couldn't find an active subscription on your account.", ephemeral=True)
        else:
            embed = discord.Embed(title=f"Ups, {interaction.user.name}, something went wrong.",
                                  description="The code you tried is incorrect, please add your email again from the first message.\n"
                                              "If you think this is a mistake, please reach out to any of our admins.")
            await interaction.response.defer()
            await asyncio.sleep(0)
            await interaction.followup.send(embed=embed, ephemeral=True)
            cursor.execute(f"DELETE FROM users WHERE userID = '{interaction.user.id}'")
            db.commit()


@tree.command(guild=discord.Object(id=guild_id), name="setup", description="setup")
async def setup(interaction: discord.Interaction):
    if interaction.user.id == int(owner_id) or interaction.user.id == int(developer_id):
        input_button = Button(custom_id="input", emoji=emoji)
        link_button = Button(url="https://www.google.ro", label="Buy")

        async def input_button_callback(interaction):
            await interaction.response.send_modal(modal1())

        input_button.callback = input_button_callback
        view = View(timeout=None)
        view.add_item(input_button)
        view.add_item(link_button)
        embed = discord.Embed(title=":index_pointing_at_the_viewer: VERIFICATION :index_pointing_at_the_viewer:",
                              description="In order to get access to our discord channels, you need to verify your entity first\n\n"
                                          "The process you have to follow:\n"
                                          f"1. Press on the button attached to this message {emoji}\n"
                                          f"2. Insert the email you user for purchase in the new window\n"
                                          f"3. Press the button from the second message you get\n"
                                          f"4. Go to your email and get the verification code\n"
                                          f"5. Insert the verification code in the new window.\n\n"
                                          f"Voila! If everything goes as planned, you will have access to the server in no time!")
        await interaction.response.defer()
        await asyncio.sleep(0)
        await interaction.followup.send(embed=embed, view=view)
        checkSubs.start()
        print("Automated verification started")


@tree.command(guild=discord.Object(id=guild_id), name="delete_email", description="delete_email")
async def delete_email(interaction: discord.Interaction):
    cursor.execute(f"DELETE FROM users WHERE userID = '{interaction.user.id}'")
    db.commit()
    embed = discord.Embed(description="Your email was remove, please restart the verification process.")
    await interaction.response.defer()
    await asyncio.sleep(0)
    await interaction.followup.send(embed=embed)
    guild = interaction.guild
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    member = guild.get_member(interaction.user.id)
    await member.remove_roles(role)


@tree.command(guild=discord.Object(id=guild_id), name="admin_delete_email", description="admin_delete_email")
async def admin_delete_email(interaction: discord.Interaction, user: discord.User):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
    else:
        cursor.execute(f"SELECT email FROM users WHERE userID = '{user.id}'")
        user_email = cursor.fetchone()
        if user_email is None:
            await interaction.response.send_message("This user did not have an email assigned", ephemeral=True)
        else:
            cursor.execute(f"DELETE FROM users WHERE userID = '{user.id}'")
            db.commit()
            await interaction.response.send_message(f"{user_email[0]} was remove from {user.name}", ephemeral=True)


@tree.command(guild=discord.Object(id=guild_id), name="check_email", description="check_email")
async def check_email(interaction: discord.Interaction):
    cursor.execute(f"SELECT email FROM users WHERE userID = '{interaction.user.id}'")
    email = cursor.fetchone()
    if email is not None:
        await interaction.response.send_message(f"You have the following email assigned **{email[0]}**")
    else:
        await interaction.response.send_message(f"You don't have any email assigned.")


@tree.command(guild=discord.Object(id=guild_id), name="admin_check_email", description="admin_check_email")
async def admin_check_email(interaction: discord.Interaction, user: discord.User):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
    else:
        cursor.execute(f"SELECT email FROM users WHERE userID = '{user.id}'")
        user_email = cursor.fetchone()
        if user_email is None:
            await interaction.response.send_message("This user does not have an email assigned", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"{user.name} does have the following email assigned: {user_email[0]}", ephemeral=True)


@tree.command(guild=discord.Object(id=guild_id), name="admin_get_all", description="admin_get_all")
async def admin_get_all(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
    else:
        cursor.execute(f"SELECT * FROM users")
        all_data = cursor.fetchall()
        with open('data.txt', 'w') as f:
            x = 1
            for data in all_data:
                string = f"{x}. Discord ID: {data[0]}, Email: {data[1]}\n"
                f.write(string)
                x += 1
            f.close()
        with open("data.txt", "rb") as file:
            await interaction.response.send_message("You can see the full Database in the attached file:",
                                                    file=discord.File(file, "data.txt"))


@tasks.loop(seconds=60)
async def checkSubs():
    cursor.execute(f"SELECT email FROM users")
    all_emails_from_db = cursor.fetchall()
    for db_email in all_emails_from_db:
        cursor.execute(f"SELECT userID FROM users WHERE email = '{db_email[0]}'")
        user_id = cursor.fetchone()
        query = stripe.Customer.search(query=f"email:'{db_email[0]}'")

        x = 0

        for sub in query['data']:
            subs = stripe.Subscription.list(limit=10, customer=sub['id'], status="active")
            if len(subs['data']) >= 1:
                x += 1
            else:
                x += 0
        if x >= 1:
            status = True
        else:
            status = False
        if status == True:
            continue
        else:
            guild = await aclient.fetch_guild(guild_id)
            role = discord.utils.get(guild.roles, name=role_name)
            try:
                member = await guild.fetch_member(int(user_id[0]))
            except:
                member = None
            if member is not None:
                if role in member.roles:
                    print("intra")
                    await member.remove_roles(role)
                    cursor.execute(f"DELETE FROM users WHERE userID = '{member.id}'")
                    db.commit()
                    print(f"Subscriptia lui {member.name} cu emailul {db_email[0]} nu mai este valabila, rol eliminat.")


aclient.run(bot_token)
