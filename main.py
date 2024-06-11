import telebot
from telebot import types

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('7325490598:AAHMYv8_R4vuatbOtKBlKf2ZEuAynOqmKlE')

member_id = "1130639695314381082"
channel_username = "@sukifindz"  # Replace with your channel username

# Dictionary to store temporary data
bot_data = {}

# Function to send message to all channels
def send_to_all_channels(text, photo_id):
    try:
        channel_info = bot.get_chat(channel_username)
        bot.send_photo(channel_info.id, photo_id, caption=text, parse_mode='HTML')
    except Exception as e:
        print(f"Error sending to channel {channel_username}: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome! Please send me a Sugargoo link.")
    # Set the conversation state to start
    bot_data[message.chat.id] = {'state': 'WAITING_FOR_LINK'}

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    try:
        chat_id = message.chat.id
        if bot_data.get(chat_id)['state'] == 'WAITING_FOR_LINK':
            sugargoo_link = message.text.strip()

            # Ask for the article name
            bot.send_message(chat_id, "Please provide the article name.")
            # Update conversation state
            bot_data[chat_id]['sugargoo_link'] = sugargoo_link
            bot_data[chat_id]['state'] = 'WAITING_FOR_ARTICLE_NAME'

        elif bot_data.get(chat_id)['state'] == 'WAITING_FOR_ARTICLE_NAME':
            article_name = message.text.strip()

            # Ask for the price
            bot.send_message(chat_id, "Please provide the price of the article.")
            # Update conversation state
            bot_data[chat_id]['article_name'] = article_name
            bot_data[chat_id]['state'] = 'WAITING_FOR_PRICE'

        elif bot_data.get(chat_id)['state'] == 'WAITING_FOR_PRICE':
            price = message.text.strip()

            # Retrieve the saved data
            sugargoo_link = bot_data[chat_id]['sugargoo_link']
            article_name = bot_data[chat_id]['article_name']

            # Ask the user to confirm the link
            markup = types.InlineKeyboardMarkup()
            confirm_button = types.InlineKeyboardButton("Yes", callback_data="confirm")
            cancel_button = types.InlineKeyboardButton("Cancel", callback_data="cancel")
            markup.add(confirm_button, cancel_button)

            response_message = (f"Is this the correct product link?\n\n"
                                f"🖇 <a href='{sugargoo_link}'>Product Link</a>\n\n"
                                f"🎰 <a href='https://www.sugargoo.com/mobile?memberId={member_id}'>Register here for bonus</a>")

            bot.send_message(chat_id, response_message, reply_markup=markup, parse_mode='HTML')
            # Update conversation state
            bot_data[chat_id]['price'] = price
            bot_data[chat_id]['state'] = 'WAITING_FOR_PHOTO'

    except Exception as e:
        bot.send_message(chat_id, f"Error processing the message: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        chat_id = call.message.chat.id
        if call.data == "confirm":
            sugargoo_link = bot_data[chat_id]['sugargoo_link']
            if sugargoo_link:
                # Ask for pictures
                bot.send_message(chat_id, "Please send the pictures of the product.")
            else:
                bot.send_message(chat_id, "Link not found. Please send another Sugargoo link.")
        elif call.data == "cancel":
            # Ask for another link
            bot.send_message(chat_id, "Please send another Sugargoo link.")
    except Exception as e:
        bot.send_message(chat_id, f"Error processing the request: {e}")

@bot.message_handler(func=lambda message: True, content_types=['photo'])
def handle_photo(message):
    try:
        chat_id = message.chat.id
        # Retrieve the saved data
        sugargoo_link = bot_data[chat_id]['sugargoo_link']
        article_name = bot_data[chat_id]['article_name']
        price = bot_data[chat_id]['price']

        # Send the message with the picture above the description
        product_link = sugargoo_link

        # Constructing the response message
        response_message = (f"🌬 Suki Finds\n"
                            f"🔎 Article: {article_name}\n"
                            f"💵 Price: {price}\n\n"
                            f"🖇 <a href='{product_link}'>Product Link</a>\n\n"
                            f"🎰 <a href='https://www.sugargoo.com/mobile?memberId={member_id}'>Register here for bonus</a>")

        # Send the message to the original chat
        sent_message = bot.send_photo(chat_id, message.photo[-1].file_id, caption=response_message, parse_mode='HTML')
        
        # Send the same message to the channel
        send_to_all_channels(response_message, message.photo[-1].file_id)
    except Exception as e:
        bot.send_message(chat_id, f"Error processing the photo: {e}")

# Start polling
bot.polling()
