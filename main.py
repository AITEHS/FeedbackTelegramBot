import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyParameters
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes,CallbackContext, CallbackQueryHandler

global group_id 

#Feedback Group ID
group_id =" "

#TG Bot token
bot_token = " "

#Dictionary that assignes topic ID to each user
topics_users =  {

                }

#logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


#Actions when the bot starts
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.message_thread_id)
    if update.message.chat_id in topics_users.values():
        pass
    else:
        

        keyboard = [
            [InlineKeyboardButton("Block", callback_data='1'),
            ]
                    ] #buttons list

        reply_markup = InlineKeyboardMarkup(keyboard)                    #create inline keyboard with beforementioned keyboard

        new_topic = await context.bot.create_forum_topic(chat_id=group_id, name=update.effective_chat.first_name) #create new topic

        await context.bot.send_message(chat_id=group_id, text="Name:\t"+update.effective_chat.first_name+"\nID:\t"+str(update.effective_chat.id)+"\nLanguage:\t"+update.message.from_user.language_code, reply_to_message_id=new_topic.message_thread_id,  reply_markup=reply_markup) #Message with info about user 
       
        topics_users[new_topic.message_thread_id]=update.effective_chat.id #add user id with corresponding topic id to the dictionary

        print(new_topic.message_thread_id)

#block button
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    
    choice = query.data
    
    #blocking button
    if choice == '1':
        print("button pressed")
        print(update.callback_query.chat_instance)
        print(topics_users)
        await context.bot.send_message(chat_id=update.callback_query.message.chat.id,text = "кнопку натиснуто",message_thread_id=update.callback_query.message.message_thread_id)
        """for tmi, uid in topics_users.items():  
            if uid == update.callback_query.from_user.id: #пройти по словнику до знаходження відповідного користувача
                topics_users["0"] = topics_users[tmi]     #створити копію пари значень блокованого користувача
                del topics_users[tmi]                     #видалити оргінальне значення гілки чату, залишити 0 - повідомлення не приходитимуть
                print(topics_users)
                break"""

#TMI - Dict keys, topic id
#UID - Dict values, user id
            
#message forwarding 
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(topics_users)
    print(update.message.message_thread_id)



    #user to group
    if update.effective_chat.id in topics_users.values():                                                                                                                 #current chat id from dict values
        for tmi, uid in topics_users.items():                                                                                                                             #for each dict pair
            print ("CHAT:"+str(tmi)+"+"+str(update.effective_chat.id)+"+"+str(uid))
            print("TMI:",str(tmi))
            if uid == update.effective_chat.id and int(tmi) != 0:                                                                                                         #User id corrsponds with topic id and is not 0(the user isn't blocked)                              
                try:
                    print('tryGtC')
                    rp = ReplyParameters(message_id =update.message.reply_to_message.message_id ,chat_id=update.message.chat_id)                                           #reply settings
                    await context.bot.copy_message(chat_id=group_id, from_chat_id=uid,message_id=update.message.message_id,message_thread_id=tmi,reply_parameters =rp)     #send message      
                except:
                    print('exceptGtC')
                    await context.bot.copy_message(chat_id=group_id, from_chat_id=uid,message_id=update.message.message_id,message_thread_id=tmi)                          #send message
            else:                                                                                                                                                          #repeat until the user is found
                print('continue')
                continue

    #від чату до користувача            
    if update.message.message_thread_id in topics_users.keys():                                                                                 #topic id in dict keys
        for tmi, uid in topics_users.items():                                                                                                   #for each pair from dictionary
            print ("GROUP TO CHAT:"+str(tmi)+"+"+str(update.message.message_thread_id))                             
            if tmi == update.message.message_thread_id:                                                                                         #topic id corresponds with the current one 
                try:                                                                                                                            #check if the reply is possible
                    print('tryCtG')
                    rp = ReplyParameters(message_id =update.message.reply_to_message.message_id ,chat_id=update.message.chat_id)                #reply settings
                    await context.bot.copy_message(chat_id=uid, from_chat_id=group_id,message_id=update.message.message_id,reply_parameters=rp) #send message
                except:                                                                                                                         #execute if not possible
                    print("exceptCtG")
                    await context.bot.copy_message(chat_id=uid, from_chat_id=group_id,message_id=update.message.message_id)                     #send message
                   
if __name__ == '__main__':

    #build
    application = ApplicationBuilder().token(bot_token).build()

  
    respond_handler = MessageHandler(  filters.ALL & (~filters.COMMAND), respond)
    start_handler = CommandHandler("start", start)
    button_handler = CallbackQueryHandler(button)

   
    application.add_handler(button_handler)
    application.add_handler(respond_handler)
    application.add_handler(start_handler)

    application.run_polling()