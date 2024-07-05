from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import CommandHandler,Application,CallbackContext,MessageHandler,filters,CallbackQueryHandler,ContextTypes
import json
import requests
import base64

API_KEY='CONFIDENTIAL'
shortner_api='CONFIDENTIAL'
Database_path='data.json'
BHVC_img_id='AgACAgUAAxkBAAMEZb6uhDoxo3XOhjMI8QABgubM_wKhAAK3uTEbMbn4VTvJi67ucDrpAQADAgADeAADNAQ'
updates_channel_id='-1002076602689'
updates_channel_link='https://t.me/+LLWbhxHMpcVlMmU1'
admin_user_id=1815996487

def url_shortner(long_url:str):
    response = requests.get(f'https://urllinkshort.in/api?api={shortner_api}&url={long_url}')
    if response.ok:
        data = response.json()
        short_url = data.get("shortenedUrl")
        return short_url
    else:
        return None

def url_shortner1(long_url:str):
    encoded_url=base64.urlsafe_b64encode(long_url.encode()).decode()
    short_url=f'https://urllinkshort.in/full?api={shortner_api}&url={encoded_url}'
    return short_url

def add_file_id(file_id:str):
    # print('add file id called')
    with open(Database_path, 'r') as f:
        data = json.load(f)

    Total_files=int(data['Total_files'])
    Total_files=Total_files+1

    data['Total_files']=str(Total_files)
    data['file_ids'].update({str(Total_files):file_id})

    with open(Database_path,'w') as f:
        json.dump(data,f,indent=2)
    
    return Total_files

def add_file_name(file_num:str,file_name:str,file_size:str):
    index=file_name.find(' S0')
    res=False
    if index==-1:
        with open(Database_path,'r') as f:
            data=json.load(f)

        if file_name not in data['names']:
            Total_size=float(data['Total_size'])
            Total_size+=float(file_size)
            data['Total_size']=str(Total_size)
            data['names'].update({file_name:{file_size:file_num}})
            res=True
        else:
            if file_size not in data['names'][file_name]:
                Total_size=float(data['Total_size'])
                Total_size+=float(file_size)
                data['Total_size']=str(Total_size)
                data['names'][file_name].update({file_size:file_num})
                res=True

        with open(Database_path,'w') as f:
            json.dump(data,f,indent=2)
    else:
        index=file_name.find(' S0')
        episode=file_name[index+1:index+7]
        episode=episode+' - '+file_size+'GB'
        series=file_name[:index+1]+file_name[index+8:]

        with open(Database_path,'r') as f:
            data=json.load(f)
        if series not in data['names']:
            Total_size=float(data['Total_size'])
            Total_size+=float(file_size)
            data['Total_size']=str(Total_size)
            data['names'].update({series:{episode:file_num}})
            res=True
        else:
            if episode not in data['names'][series]:
                Total_size=float(data['Total_size'])
                Total_size+=float(file_size)
                data['Total_size']=str(Total_size)
                data['names'][series].update({episode:file_num})
                res=True

        with open(Database_path,'w') as f:
            json.dump(data,f,indent=2)

    return res

async def send_document(update:Update,context:CallbackContext,user_id:str,file_id:str):
    try:
        caption='Join @BHVC_Movies_Database'
        await context.bot.send_document(user_id,file_id,protect_content=True,caption=caption)
        caption1=f'{update.message.from_user.first_name}'
        await context.bot.send_document(admin_user_id,file_id,caption=caption1)
    except:
        await update.message.reply_text('sorry bro, file is not found')

async def add_file(update: Update,context: CallbackContext):
    if update.message.from_user.id != 1815996487:
        await update.message.reply_text('idi neeku kaadu')
        return

    replied_message=update.message.reply_to_message

    if replied_message and replied_message.forward_from_chat and replied_message.document:
        file_id=replied_message.document.file_id
        file_name=replied_message.document.file_name
        name_parts=file_name.split('.',1)
        file_name=name_parts[0]
        file_size=replied_message.document.file_size
        file_size/=1024
        file_size/=1024
        file_size/=1024
        file_size=str(round(file_size,2))
        file_num=str(add_file_id(file_id=file_id))
        added = add_file_name(file_num=file_num,file_name=file_name,file_size=file_size)
        if added:
            await update.message.reply_text('Added Succesfully')
        else:
            await update.message.reply_text('file already exists')
    else:
        await update.message.reply_text('reply to a forwarded message')

async def get_file_num(update,context):
    if update.message.from_user.id != 1815996487:
        await update.message.reply_text('idi neeku kaadu')
        return
    
    replied_message=update.message.reply_to_message

    if replied_message and replied_message.forward_from_chat and replied_message.document:
        file_id=replied_message.document.file_id
        file_num=add_file_id(file_id=file_id)
        await update.message.reply_text(file_num)
    else:
        await update.message.reply_text('reply to a forwarded message')

async def add_custom_file_name(update:Update,context:CallbackContext):
    if update.message.from_user.id != 1815996487:
        await update.message.reply_text('idi neeku kaadu')
        return
    
    if len(context.args) != 2:
        await update.message.reply_text('send correct arguments = /command file_size(or)episode number file_num')
        return
    
    if not(update.message.reply_to_message and update.message.reply_to_message.document):
        await update.message.reply_text('Please reply to the file so that i can get file name')
        return

    file_name=update.message.reply_to_message.document.file_name
    name_parts=file_name.split('.')
    file_name=name_parts[0]

    # index=file_name.find(' S0')

    # if index != -1:
    #     file_name=file_name[:index+1]+file_name[index+8:]

    file_size=context.args[0]
    file_num=context.args[1]
    file_num_split=file_num.split('_')
    starting_num=int(file_num_split[0])
    ending_num=int(file_num_split[1])
    file_num=str(starting_num)
    for i in range(starting_num+1,ending_num+1):
        file_num=file_num+'_'+str(i)
    file_num=f'BHVCBHVC_{file_num}'

    file_number=str(add_file_id(file_num))

    added=add_file_name(file_num=file_number,file_name=file_name,file_size=file_size)
    if added:
        await update.message.reply_text('Added Succesfully')
    else:
        await update.message.reply_text('file already exists')

async def add_4K_file_name(update:Update,context:CallbackContext):
    if update.message.from_user.id != 1815996487:
        await update.message.reply_text('idi neeku kaadu')
        return
    
    if len(context.args) != 2:
        await update.message.reply_text('send correct arguments = /command file_size(or)episode number file_num')
        return
    
    if not(update.message.reply_to_message and update.message.reply_to_message.document):
        await update.message.reply_text('Please reply to the file so that i can get file name')
        return

    file_name=update.message.reply_to_message.document.file_name
    name_parts=file_name.split('.')
    file_name=name_parts[0]

    file_name=f'[4K] {file_name}'

    file_size=context.args[0]
    file_num=context.args[1]
    file_num_split=file_num.split('_')
    starting_num=int(file_num_split[0])
    ending_num=int(file_num_split[1])
    file_num=str(starting_num)
    for i in range(starting_num+1,ending_num+1):
        file_num=file_num+'_'+str(i)
    file_num=f'BHVCBHVC_{file_num}'

    file_number=str(add_file_id(file_num))

    added=add_file_name(file_num=file_number,file_name=file_name,file_size=file_size)
    if added:
        await update.message.reply_text('Added Succesfully')
    else:
        await update.message.reply_text('file already exists')

async def check_stats(update,context):
    with open(Database_path,'r') as f:
        data=json.load(f)

    database_size=data['Total_size']
    num_of_users=len(data['users'])
    num_of_movies=len(data['names'])
    database_size=round(float(database_size),2)
    await update.message.reply_text(f'''Total Database Size :- {database_size}GB
Total number of users :- {num_of_users}
Total number of movies and series :- {num_of_movies}''')

async def message_function(update: Update,context: CallbackContext):
    member=await context.bot.get_chat_member(chat_id=updates_channel_id,user_id=update.message.from_user.id)
    if((member.status!='member')and(member.status!='creator')):
        button=InlineKeyboardButton(text='Updates Channel',url=updates_channel_link)
        buttons=[[button]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await update.message.reply_text(f'Join the updates channel to use this bot',reply_markup=reply_markup)
        return

    message=update.message.text.lower()

    if len(message)<3:
        await update.message.reply_text('type atleast 3 letters')
        return
    
    with open(Database_path,'r') as f:
        data=json.load(f)
    
    required_keys=[]

    for key in data['names'].keys():
        if message in key.lower():
            required_keys.append(key)
    
    if len(required_keys) > 35:
        await update.message.reply_text('Can you please be specific')
        return

    buttons=[]
    for key in required_keys:
        button=InlineKeyboardButton(text=key,callback_data=key)
        buttons1=[]
        buttons1.append(button)
        buttons.append(buttons1)
    
    if len(buttons) != 0:
        # await context.bot.send_photo(chat_id=update.message.from_user.id,photo=BHVC_img_id)
        await update.message.reply_text('Search results are shown below',reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await context.bot.send_message(chat_id=admin_user_id,text=f'{update.message.from_user.first_name} (<code>{update.message.from_user.id}</code>) requested {update.message.text}',parse_mode="HTML")
        await update.message.reply_text(f'''Sorry no matches found
Informed admin''')

async def handle_button(update:Update,context:CallbackContext):
    # print('entered first handle button funtion successfully.....')
    query=update.callback_query
    await query.answer()

    chat_id=query.message.chat_id
    message_id=query.message.message_id

    await context.bot.delete_message(chat_id=chat_id,message_id=message_id)

    if query:

        with open(Database_path,'r') as f:
            data=json.load(f)

        button_clicked=query.data

        if '_' not in button_clicked:
            buttons=[]

            for key in data['names'][button_clicked].keys():
                if key == 'img_id':
                    continue
                postfix='GB'
                if key[0] == 'S':
                    postfix=''
                button=InlineKeyboardButton(text=f'{key}{postfix}',callback_data=f'{button_clicked}_{key}')
                buttons1=[]
                buttons1.append(button)
                buttons.append(buttons1)
            reply_message='Choose a desired file size'
            if postfix == '':
                reply_message='Select the episode'
            await context.bot.send_photo(chat_id=query.message.chat_id,photo=data['names'][button_clicked]['img_id'],caption=f'''Name : {button_clicked}                               

{reply_message}:''',reply_markup=InlineKeyboardMarkup(buttons))
        else:
            name,size=button_clicked.rsplit('_',1)
            file_num=data['names'][name][size]
            file_num=str(query.message.chat_id)+'_'+file_num
            encoded_file_num=base64.b64encode(file_num.encode()).decode();
            reply=f'https://t.me/BHVC_Bot?start={encoded_file_num}'

            if query.message.chat_id!=admin_user_id:
                if query.message.chat_id!=6677304986:
                    reply=url_shortner1(reply)

            button=InlineKeyboardButton(text='GET FILE(S)',url=reply)
            buttons=[[button]]
            reply_markup=InlineKeyboardMarkup(buttons)
            reply_string='File Size'
            reply_string2='GB'
            if size[0] == 'S':
                reply_string='Episode'
                reply_string2=''

            await query.message.reply_text(f'''File Name : {name}
{reply_string} : {size}{reply_string2}
''',reply_markup=reply_markup)
    else:
        print('no callback recieved')

async def get_img_id(update,context):
    if update.message.from_user.id != 1815996487:
        await update.message.reply_text('idi neeku kaadu')
        return
    
    if update.message.reply_to_message and update.message.reply_to_message.forward_from_chat:
        if update.message.reply_to_message.photo:
            file_id=update.message.reply_to_message.photo[-1].file_id
            await update.message.reply_text(f'Image  ID is <code>{file_id}</code>',parse_mode='HTML')
        else:
            await update.message.reply_text('The replied message does not contain any image')
    else:
        await update.message.reply_text('Please reply to a forwarded image')

async def add_img(update,context:CallbackContext):
    if update.message.from_user.id != 1815996487:
        await update.message.reply_text('idi neeku kaadu')
        return
    
    replied_message=update.message.reply_to_message

    if replied_message:
        file_name=replied_message.document.file_name
    else:
        await update.message.reply_text('Please reply to a document file')
        return
    
    name_parts=file_name.split('.',1)
    file_name=name_parts[0]

    index=file_name.find(' S0')

    if index != -1:
        file_name=file_name[:index+1]+file_name[index+8:]
    
    if context.args:
        with open(Database_path,'r') as f:
            data=json.load(f)

        data['names'][file_name]['img_id']=context.args[0]
        await update.message.reply_text('Image added successfully')
        button=InlineKeyboardButton('Get files here',url='https://t.me/BHVC_Bot')
        buttons=[[button]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await context.bot.send_photo(chat_id=updates_channel_id,photo=context.args[0],caption=f'<code>{file_name}</code> - Added to Bot ✅',parse_mode='HTML',reply_markup=reply_markup)
        # await context.bot.send_message(chat_id=updates_channel_id,text=f'<code>{file_name}</code> - Added to Bot ✅',parse_mode='HTML',reply_markup=reply_markup)

        with open(Database_path,'w') as f:
            json.dump(data,f,indent=2)
    else:
        await update.message.reply_text('send img id as parameter')

async def add_4K_image(update,context:CallbackContext):
    if update.message.from_user.id != 1815996487:
        await update.message.reply_text('idi neeku kaadu')
        return
    
    replied_message=update.message.reply_to_message

    if replied_message:
        file_name=replied_message.document.file_name
    else:
        await update.message.reply_text('Please reply to a document file')
        return
    
    name_parts=file_name.split('.',1)
    file_name=name_parts[0]

    index=file_name.find(' S0')

    if index != -1:
        file_name=file_name[:index+1]+file_name[index+8:]
    
    file_name=f'[4K] {file_name}'
    
    if context.args:
        with open(Database_path,'r') as f:
            data=json.load(f)

        data['names'][file_name]['img_id']=context.args[0]
        await update.message.reply_text('Image added successfully')
        button=InlineKeyboardButton('Get files here',url='https://t.me/BHVC_Bot')
        buttons=[[button]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await context.bot.send_photo(chat_id=updates_channel_id,photo=context.args[0],caption=f'<code>{file_name}</code> - Added to Bot ✅',parse_mode='HTML',reply_markup=reply_markup)
        # await context.bot.send_message(chat_id=updates_channel_id,text=f'<code>{file_name}</code> - Added to Bot ✅',parse_mode='HTML',reply_markup=reply_markup)

        with open(Database_path,'w') as f:
            json.dump(data,f,indent=2)
    else:
        await update.message.reply_text('send img id as parameter')

async def start_function(update,context):

    with open(Database_path,'r') as f:
        data=json.load(f)

    if update.message.from_user.id not in data['users']:
        user_id=update.message.from_user.id
        user_name=update.message.from_user.first_name
        data['users'][user_id]=user_name

        with open(Database_path,'w') as f:
            json.dump(data,f,indent=2)
    
    member=await context.bot.get_chat_member(chat_id=updates_channel_id,user_id=update.message.from_user.id)
    if((member.status!='member')and(member.status!='creator')):
        button=InlineKeyboardButton(text='Updates Channel',url=updates_channel_link)
        buttons=[[button]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await update.message.reply_text(f'Join the updates channel to use this bot',reply_markup=reply_markup)
        return

    if context.args:
        encoded_file=context.args[0]
        file=base64.b64decode(encoded_file.encode()).decode()
        split_file=file.split('_')
        if len(split_file)!=2:
            await update.message.reply_text('Something went wrong, Please try again')
            return
        
        if split_file[0]!=str(update.message.from_user.id):
            await update.message.reply_text('This is not valid for you. Generate your own link')
            return

        file=split_file[1]

        file_id=data['file_ids'][file]
        if 'BHVCBHVC_' not in file_id:
            await send_document(update,context,user_id=user_id,file_id=file_id)
        else:
            file_id=file_id[9:]
            file_nums=file_id.split('_')

            for file_num in file_nums:
                await send_document(update,context,user_id=user_id,file_id=data['file_ids'][file_num])
    else:
        button=InlineKeyboardButton(text='Updates Channel',url=updates_channel_link)
        buttons=[[button]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await update.message.reply_text(f'''Hi {user_name}
Welcome to the BHVC Movies Bot
Press / to see all commands available''',reply_markup=reply_markup)

async def help_funtion(update,context):
    output=f'''Just enter the movie name and see the magic

/start - Check if bot is alive
/size - To know the total size size of our Database'''
    await update.message.reply_text(output)

async def error_function(update: Update,context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error {context.error}')

async def reply(update: Update,context: CallbackContext):
    if update.message.from_user.id != admin_user_id:
        print(update.message.from_user.id)
        await update.message.reply_text('idi neeku kaadu')
        return

    if len(context.args)<2:
        await update.message.reply_text('parameters: /command [user_id] [message]')
        return

    parameters=context.args
    user_id=parameters[0]

    string = ''

    for parameter in parameters[1:]:
        string+=' '+parameter
    
    try:
        await context.bot.send_message(chat_id=user_id,text=string)
        await update.message.reply_text('message sent.')
    except Exception as e:
        await update.message.reply_text(f'parameters: /command [user_id] [message]   {e}')

async def broadcast(update: Update,context: CallbackContext):

    if update.message.from_user.id != admin_user_id:
        await update.message.reply_text('idi neeku kaadu')
        return

    parameters=context.args
    string=''

    for parameter in parameters:
        string+=' '+parameter
    
    with open(Database_path,'r') as f:
        data=json.load(f)
    
    blocked=0

    for user_id in data['users'].keys():
        try:
            await context.bot.send_message(chat_id=user_id,text=string)
        except:
            blocked+=1
    
    await context.bot.send_message(chat_id=admin_user_id,text=f'No. of blocked users: {blocked}')


def decode_base64_url(encoded_url):
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_url)
        decoded_url = decoded_bytes.decode('utf-8')
        return decoded_url
    except Exception as e:
        return 'error decoding url'


async def bypass(update:Update,context: CallbackContext):

    if not context.args:
        await update.message.reply_text('send the url as a parameter')
        return
    url=context.args[0]
    if(url.find('&type')!=-1):
        encoded_url=url[url.find('url=')+4:url.find('&type')]
    else:
        encoded_url=url[url.find('url=')+4:]
    decoded_url=decode_base64_url(encoded_url=encoded_url)
    await update.message.reply_text(f'<code>{decoded_url}</code>',parse_mode='HTML')


if __name__=='__main__':
    print('starting bot...')
    app=Application.builder().token(API_KEY).build()

    app.add_handler(CommandHandler('start',start_function))
    app.add_handler(CommandHandler('stats',check_stats))
    app.add_handler(CommandHandler('help',help_funtion))
    app.add_handler(CommandHandler('send',send_document))
    app.add_handler(CommandHandler('add',add_file))
    app.add_handler(CommandHandler('gfn',get_file_num))
    app.add_handler(CommandHandler('acfn',add_custom_file_name))
    app.add_handler(CommandHandler('a4fn',add_4K_file_name))
    app.add_handler(CommandHandler('get_img_id',get_img_id))
    app.add_handler(CommandHandler('add_img',add_img))
    app.add_handler(CommandHandler('add4_img',add_4K_image))
    app.add_handler(CommandHandler('reply',reply))
    app.add_handler(CommandHandler('broadcast',broadcast))
    app.add_handler(CommandHandler('bhvc',bypass))

    app.add_handler(MessageHandler(filters.TEXT,message_function))

    app.add_handler(CallbackQueryHandler(handle_button))

    
    app.add_error_handler(error_function)

    print('polling...')
    app.run_polling()
