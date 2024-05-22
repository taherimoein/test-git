from database.screening_query import *
from database.program_query import *
from database.member_query import *
from utils.base_fuction import *
import re,environ,requests
from telegram.ext import *
from telegram import *

# cinema seven server path
cinemaSevenServerPath = 'F:/Project/Django/cinema-seven/media/'
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# Connecting to Telegram API
# Updater retrieves information and dispatcher connects commands
tokenID = env('token')
print(tokenID)
updater = Updater(tokenID)
dispatcher = updater.dispatcher


# default variable
thisWeeksProgram = 'برنامه این هفته'
myTicketsText = 'بلیط های من'
supportText = 'پشتیبانی'


def startCommand(update: Update, content: CallbackContext):
    # get user data
    userFirstName = update.message.chat.first_name
    userChatID = update.message.chat_id
    # check existence member
    checkStatus, memberExistenceStatus, error = check_existence_member(userChatID)
    if checkStatus:
        if not memberExistenceStatus:
            # enter invitation code message
            enterInvitationCodeMessage = "برای عضویت در سینما هفت، لطفا کد دعوت خود را به صورت \n"
            enterInvitationCodeMessage += "code:123456\n"
            enterInvitationCodeMessage += "وارد نمایید.\n\n"
            enterInvitationCodeMessage += "(توجه: همه حروف کوچک و بدون فاصله باشد)"

            content.bot.send_message(chat_id=update.effective_chat.id, text=enterInvitationCodeMessage)
        else:
            # check member block status
            checkMemberBlockStatus, blockStatus, error = check_member_block_status(userChatID)
            if checkMemberBlockStatus:
                if not blockStatus:
                    # block message
                    blockMessage = "دسترسی شما به بات غیرفعال شده است."

                    content.bot.send_message(chat_id=update.effective_chat.id, text=blockMessage)
                else:
                    # welcome message
                    welcomeMessage = f"سلام {userFirstName} 👋\n"
                    welcomeMessage += "به سینما هفت خوش آمدی!"
                    # menu
                    buttons = [[KeyboardButton(thisWeeksProgram)],[KeyboardButton(myTicketsText)],[KeyboardButton(supportText)]]

                    content.bot.send_message(chat_id=update.effective_chat.id, text=welcomeMessage, reply_markup=ReplyKeyboardMarkup(buttons,\
                        one_time_keyboard=True, resize_keyboard=True))
            else:
                # error message
                errorMessage = "خطایی رخ داده است! (member 02)"
                content.bot.send_message(chat_id=update.effective_chat.id, text=errorMessage)
    else:
        # error message
        errorMessage = "خطایی رخ داده است! (member 01)"
        content.bot.send_message(chat_id=update.effective_chat.id, text=errorMessage)


def messageCommand(update: Update, content: CallbackContext):
    # check message text
    if thisWeeksProgram in update.message.text:
        weekProgram = get_week_program()
        weekProgramStr = generate_week_program_str(weekProgram)

        content.bot.send_message(chat_id=update.effective_chat.id, text=weekProgramStr)

    elif myTicketsText in update.message.text:
        msg = 'برای نمایش جزئیات بلیط روی بلیط مورد نظر کلیک کنید.'
        buttons = [[InlineKeyboardButton('بیلط یک', callback_data='ticket_one')],[InlineKeyboardButton('بیلط دو', callback_data='ticket_two')],[InlineKeyboardButton('بیلط سه', callback_data='ticket_three')]]
        content.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=InlineKeyboardMarkup(buttons))

    elif supportText in update.message.text:
        msg = 'برای برقراری ارتباط با پشتیبانی سینما 7 می توانید با شماره\n+989399740632\nتماس بگیرید.'
        content.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    
    else:
        msg = 'عبارت وارد شده نامفهوم می باشد.'
        content.bot.send_message(chat_id=update.effective_chat.id, text=msg)



def codeCommand(update: Update, content: CallbackContext):
    # check code
    code = update.message.text
    code = code.split(':')[1]
    checkStatus, userHaveCodeStatus, invitationCodeStatus, error = check_invitation_code(code)
    if checkStatus:
        if not userHaveCodeStatus:
            if invitationCodeStatus:
                # get user data
                userJson = {
                    'first_name': update.message.chat.first_name,
                    'last_name': update.message.chat.last_name,
                    'telegram_chat_id': update.message.chat_id,
                    'telegram_username': update.message.chat.username,
                    'invitation_code_used': code
                }
                
                # insert to db
                create_member(userJson)

                # welcome message
                welcomeMessage = f"سلام {userJson['first_name']} 👋\n"
                welcomeMessage += "به سینما هفت خوش آمدی!"
                # menu
                buttons = [[KeyboardButton(thisWeeksProgram)],[KeyboardButton(myTicketsText)],[KeyboardButton(supportText)]]

                content.bot.send_message(chat_id=update.effective_chat.id, text=welcomeMessage, reply_markup=ReplyKeyboardMarkup(buttons,one_time_keyboard=True, resize_keyboard=True))
            else:
                # error message
                errorMessage = "کد دعوت وارد شده، معتبر نمی باشد. (member 05)"
                content.bot.send_message(chat_id=update.effective_chat.id, text=errorMessage)
        else:
            # error message
            errorMessage = "کد دعوت قبلا برای شما ثبت شده است! (member 04)"
            content.bot.send_message(chat_id=update.effective_chat.id, text=errorMessage)
    else:
        # error message
        errorMessage = "خطایی رخ داده است! (member 03)"
        content.bot.send_message(chat_id=update.effective_chat.id, text=errorMessage)


def programDescriptionCommand(update: Update, content: CallbackContext):
    # get program description
    programID = update.message.text.replace('/p_description_', '')
    programDescription = get_program_field(programID, 'description')
    content.bot.send_message(chat_id=update.effective_chat.id, text=programDescription)


def programInfoCommand(update: Update, content: CallbackContext):
    # get program attached file
    programID = update.message.text.replace('/p_info_', '')
    # get file
    programAttachedFile = get_program_field(programID, 'attached_file')
    programAttachedFileUrl = cinemaSevenServerPath + programAttachedFile
    file = open(programAttachedFileUrl, 'rb')
    msg = content.bot.send_message(chat_id=update.effective_chat.id, text='در حال ارسال فایل...')
    content.bot.send_document(chat_id=update.effective_chat.id, document=file, caption='فایل توضیحات')
    content.delete_message(chat_id=message.chat_id,message_id=message.message_id,*args,**kwargs)


def programTeaserCommand(update: Update, content: CallbackContext):
    # get program teaser
    programID = update.message.text.replace('/p_teaser_', '')
    # get teaser
    programTeaserFile = get_program_field(programID, 'teaser')
    programTeaserFileUrl = cinemaSevenServerPath + programTeaserFile
    teaser = open(programTeaserFileUrl, 'rb')
    msg = content.bot.send_message(chat_id=update.effective_chat.id, text='در حال ارسال فایل...')
    content.bot.send_video(chat_id=update.effective_chat.id, video=teaser, caption='فایل تیزر')
    content.bot.delete_message(chat_id=update.effective_chat.id,message_id=msg.message_id)


def screeningViewHallCommand(update: Update, content: CallbackContext):
    # get screening id
    screeningID = update.message.text.replace('/s_view_hall_', '')
    # get hall json
    screeningHallJson = get_screening_hall(screeningID)
    buttons = get_hall_buttons(screeningHallJson, screeningID)
    content.bot.send_message(chat_id=update.effective_chat.id, text='لطفا صندلی مورد نظر خود را انتخاب نمایید.',reply_markup=InlineKeyboardMarkup(buttons))


def queryHandler(update: Update, content: CallbackContext):
    # get query
    query = update.callback_query.data
    # check query pattern
    if re.search('^screening_\d*_chair_\d*$', query):
        queryList = query.split('_')
        screeningID = int(queryList[1])
        chairID = int(queryList[3])
        # check chair status
        chairStatus = int(get_chair_status(screeningID, chairID))
        if chairStatus == 0:
            content.bot.send_message(chat_id=update.effective_chat.id, text='chair free')
            update.callback_query.answer('chair free')
        elif chairStatus == 1:
            content.bot.send_message(chat_id=update.effective_chat.id, text='chair rezerv')
        else:
            content.bot.send_message(chat_id=update.effective_chat.id, text='chair buyed')


    # if thisWeeksProgram in update.message.text:
    #     msg = 'فیلم مورد نظر خود را انتخاب کنید.'
    #     buttons = [[InlineKeyboardButton('فیلم یک', callback_data='movie_one')],[InlineKeyboardButton('فیلم دو', callback_data='movie_two')],[InlineKeyboardButton('فیلم سه', callback_data='movie_three')]]
    #     content.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=InlineKeyboardMarkup(buttons))

    # elif myTicketsText in update.message.text:
    #     msg = 'برای نمایش جزئیات بلیط روی بلیط مورد نظر کلیک کنید.'
    #     buttons = [[InlineKeyboardButton('بیلط یک', callback_data='ticket_one')],[InlineKeyboardButton('بیلط دو', callback_data='ticket_two')],[InlineKeyboardButton('بیلط سه', callback_data='ticket_three')]]
    #     content.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=InlineKeyboardMarkup(buttons))

    # elif supportText in update.message.text:
    #     msg = 'برای برقراری ارتباط با پشتیبانی سینما 7 می توانید با شماره\n+989399740632\nتماس بگیرید.'
    #     content.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    
    

# creating handlers
dispatcher.add_handler(CallbackQueryHandler(queryHandler))
dispatcher.add_handler(CommandHandler('start', startCommand))
dispatcher.add_handler(MessageHandler(Filters.text((thisWeeksProgram, myTicketsText, supportText)), messageCommand))
dispatcher.add_handler(MessageHandler(Filters.regex('^(/p_description_\d*)$'),programDescriptionCommand))
dispatcher.add_handler(MessageHandler(Filters.regex('^(/p_info_\d*)$'),programInfoCommand))
dispatcher.add_handler(MessageHandler(Filters.regex('^(/p_teaser_\d*)$'),programTeaserCommand))
dispatcher.add_handler(MessageHandler(Filters.regex('^(/s_view_hall_\d*)$'),screeningViewHallCommand))
dispatcher.add_handler(MessageHandler(Filters.regex('^code:\d{6}$'),codeCommand))

# start_handler = CommandHandler('start', start)
# support_handler = CommandHandler('support', support)
# support_msg_handler = MessageHandler([Filters.text], support_message)
# settings_handler = CommandHandler('settings', settings)
# get_language_handler = RegexHandler('^([a-z]{2}_[A-Z]{2}) - .*',
#                                     kb_settings_select,
#                                     past_groups=True)
# help_handler = CommandHandler('help', start)
# unknown_handler = MessageHandler([Filters.command], unknown)

# # adding handlers
# dispatcher.add_handler(start_handler)
# # dispatcher.add_handler(support_handler)
# dispatcher.add_handler(settings_handler)
# # dispatcher.add_handler(get_language_handler)
# # dispatcher.add_handler(help_handler)
# # dispatcher.add_handler(unknown_handler)

# # Message handler must be the last one
# # dispatcher.add_handler(support_msg_handler)

# to run this program:
updater.start_polling()
# to stop it:
# updater.stop()