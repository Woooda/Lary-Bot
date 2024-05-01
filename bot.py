import disnake
from disnake.ext import commands
import aiosqlite
import random
from disnake.ext import tasks
import asyncio
bot = commands.Bot(command_prefix="/", intents=disnake.Intents.all())
bot.remove_command('help')



async def create_db():
    async with aiosqlite.connect('economy.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 1000,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        ''')
        await db.commit()


async def main():
    await create_db()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
	
#on_ready
@bot.event
async def on_ready():
    print(f'██████╗░░█████╗░███╗░░██╗███████╗')
    print("██╔══██╗██╔══██╗████╗░██║██╔════╝")
    print("██║░░██║██║░░██║██╔██╗██║█████╗░░")
    print("██║░░██║██║░░██║██║╚████║██╔══╝░░")
    print("██████╔╝╚█████╔╝██║░╚███║███████╗")
    print("╚═════╝░░╚════╝░╚═╝░░╚══╝╚══════╝")
    print(f'Я (РАБ), запустил {bot.user.name} и он работает!')
    change_status.start()

@tasks.loop(seconds=5)  # Интервал в секундах между изменениями статуса
async def change_status():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name="обновление 0.2"))
    await asyncio.sleep(5)
    
    await bot.change_presence(activity=disnake.Game(name="Lary Bot"))
    await asyncio.sleep(5)
    
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening, name="Prosto Георгий"))
    await asyncio.sleep(5)
    
    await bot.change_presence(activity=disnake.Game(name="/хелп"))
    
    
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name="Youtube"))
    await asyncio.sleep(5)
    
    await bot.change_presence(activity=disnake.Game(name="Minecraft"))
    await asyncio.sleep(5)



# --------------------------------------------- НАСТРОЙКИ ----------------------------------------------
colemb = 0xFF0000 # Цвет эмбедов
token = "" # Токен бота


# ------------------------------- ДАЛЬШЕ ТРОГАЙТЕ ЕСЛИ ЗНАЕТЕ ЧТО ДЕЛАЕТЕ ------------------------------

# Экономические команды
@bot.slash_command(description="Выводит баланс пользователя")
async def баланс(ctx):
    async with aiosqlite.connect('economy.db') as db:
        cursor = await db.execute('SELECT balance FROM users WHERE user_id = ?', (ctx.author.id,))
        balance = await cursor.fetchone()
        if balance:
            await ctx.send(f"Ваш баланс: {balance[0]} монет")
        else:
            await ctx.send("У вас пока нет монет.")

@bot.slash_command(description="Рулетка")
async def рулетка(ctx, bet: int):
    async with aiosqlite.connect('economy.db') as db:
        cursor = await db.execute('SELECT balance FROM users WHERE user_id = ?', (ctx.author.id,))
        balance = await cursor.fetchone()
        if not balance:
            await ctx.send("У вас пока нет баланса.")
            return
        if balance[0] < bet:
            await ctx.send("У вас недостаточно монет для ставки.")
            return

        result = random.choice(['Выигрыш', 'Проигрыш'])
        if result == 'Выигрыш':
            new_balance = balance[0] + bet
            await ctx.send(f"Поздравляем! Вы выиграли {bet} монет.")
        else:
            new_balance = balance[0] - bet
            await ctx.send(f"К сожалению, вы проиграли {bet} монет.")
        await db.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, ctx.author.id,))
        await db.commit()

@bot.slash_command(description="Топ пользователей")
async def лидерборд(ctx):
    async with aiosqlite.connect('economy.db') as db:
        cursor = await db.execute('SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10')
        leaders = await cursor.fetchall()
        if leaders:
            leaderboard = '\n'.join(f"{ctx.guild.get_member(leader[0]).display_name}: {leader[1]} монет" for leader in leaders)
            await ctx.send(f"Лидерборд:\n{leaderboard}")
        else:
            await ctx.send("Лидерборд пуст.")

@bot.slash_command(description="Работа для заработка монет")
async def work(ctx):
    earnings = random.randint(100, 500)
    async with aiosqlite.connect('economy.db') as db:
        await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (earnings, ctx.author.id))
        await db.commit()
    await ctx.send(f"Вы заработали {earnings} монет на работе.")

@bot.slash_command(description="Добавляет x монет")
@commands.has_permissions(administrator=True)
async def добавить_монеты(ctx, member: disnake.Member, amount: int):
    async with aiosqlite.connect('economy.db') as db:
        await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, member.id))
        await db.commit()
    await ctx.send(f"Добавлено {amount} монет на счет {member.display_name}.")

# Команды модерации
@bot.slash_command(description="Очищает x сообщений")
@commands.has_permissions(manage_messages=True)
async def очистить(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

@bot.slash_command(description="Бан пользователя")
@commands.has_permissions(ban_members=True)
async def бан(ctx, member: disnake.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.display_name} был забанен по причине: {reason}')

@bot.slash_command(description="Разбан пользователя")
@commands.has_permissions(ban_members=True)
async def разбан(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f'{user.display_name} был разбанен.')

@bot.slash_command(description="Выдача кика")
@commands.has_permissions(kick_members=True)
async def кик(ctx, member: disnake.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.display_name} был выгнан по причине: {reason}')

@bot.slash_command(description="Выдача предупреждения пользователю")
@commands.has_permissions(manage_roles=True)
async def варн(ctx, member: disnake.Member, *, reason=None):
    await ctx.send(f'{member.display_name}, вам выдано предупреждение по причине: {reason}')






# Система уровней и опыта
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    xp_add = random.randint(5, 10)
    async with aiosqlite.connect('economy.db') as db:
        cursor = await db.execute('SELECT xp, level FROM users WHERE user_id = ?', (message.author.id,))
        result = await cursor.fetchone()
        if result:
            new_xp = result[0] + xp_add
            new_level = int(new_xp / 100) + 1
            if new_level > result[1]:
                await message.channel.send(f'Поздравляем, {message.author.display_name}, вы достигли уровня {new_level}!')
            await db.execute('UPDATE users SET xp = ?, level = ? WHERE user_id = ?', (new_xp, new_level, message.author.id,))
        else:
            await db.execute('INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)', (message.author.id, xp_add, 1,))
        await db.commit()
    await bot.process_commands(message)

@bot.slash_command(description="Показывает ранг")
async def ранг(ctx, member: disnake.Member = None):
    member = member or ctx.author
    async with aiosqlite.connect('economy.db') as db:
        cursor = await db.execute('SELECT level, xp FROM users WHERE user_id = ?', (member.id,))
        data = await cursor.fetchone()
        if data:
            await ctx.send(f"{member.display_name} на уровне {data[0]} с {data[1]} XP.")
        else:
            await ctx.send("Данные пользователя не найдены.")

@bot.slash_command(description="Сбрасывает ранг пользователю")
@commands.has_permissions(administrator=True)
async def сбросить_ранг(ctx, member: disnake.Member):
    async with aiosqlite.connect('economy.db') as db:
        await db.execute('UPDATE users SET xp = 0, level = 1 WHERE user_id = ?', (member.id,))
        await db.commit()
    await ctx.send(f"Ранг пользователя {member.display_name} сброшен.")
    
@bot.slash_command(description="Устанавливает ранг пользователю")
@commands.has_permissions(administrator=True)
async def установить_ранг(ctx, member: disnake.Member, level: int, xp: int):
    async with aiosqlite.connect('economy.db') as db:
        await db.execute('UPDATE users SET level = ?, xp = ? WHERE user_id = ?', (level, xp, member.id))
        await db.commit()
    await ctx.send(f"Установлен ранг {level} и XP {xp} для пользователя {member.display_name}.")





# Информационные команды
@bot.slash_command(description="Выводит информацию о пользователе")
async def инфо(ctx):
    """Выводит информацию о пользователе."""
    embed = disnake.Embed(
        title="Информация о пользователе",
        color=colemb
    )
    embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.add_field(name="Имя", value=ctx.author.display_name, inline=False)
    embed.add_field(name="ID", value=ctx.author.id, inline=False)
    embed.add_field(name="Присоединился к серверу", value=ctx.author.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Дата создания аккаунта", value=ctx.author.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    await ctx.send(embed=embed)

@bot.slash_command(description="Показывает текущий пинг бота")
async def пинг(ctx):
    embed=disnake.Embed(title="Пинг", description="", color=colemb)
    embed.add_field(name=f"Пинг: {round(bot.latency * 1000)}ms", value="", inline=False)
    await ctx.send(embed=embed)

@bot.slash_command(description="Показывает информацию о сервере")
async def сервер(ctx):
    guild = ctx.guild
    members = guild.members
    online_members = len([member for member in members if member.status == disnake.Status.online])
    total_members = len(members)
    created_at = guild.created_at
    bot_added_at = guild.me.joined_at
    owner = guild.owner

    # Создаем эмбед
    emb = disnake.Embed(title=f'Информация о сервере {guild.name}', color=colemb)
    
    # Проверяем наличие иконки сервера
    if guild.icon:
        emb.set_thumbnail(url=guild.icon.url)
    emb.add_field(name='Общее количество участников', value=f'{total_members}', inline=False)
    emb.add_field(name='Дата создания сервера', value=f'{created_at}', inline=False)
    emb.add_field(name='Дата добавления бота на сервер', value=f'{bot_added_at}', inline=False)
    emb.add_field(name='Создатель сервера', value=f'{owner}', inline=False)
    emb.add_field(name='Количество онлайн-участников', value=f'{online_members}', inline=False)
    
    # Дополнительная информация
    emb.add_field(name='Уровень верификации', value=f'{guild.verification_level}', inline=True)
    emb.add_field(name='Общее количество каналов', value=f'{len(guild.channels)}', inline=True)
    emb.add_field(name='Общее количество текстовых каналов', value=f'{len(guild.text_channels)}', inline=True)
    emb.add_field(name='Общее количество голосовых каналов', value=f'{len(guild.voice_channels)}', inline=True)
    
    # Информация о ролях
    emb.add_field(name='Высшая роль бота', value=guild.me.top_role.mention, inline=True)
    emb.set_footer(text=f'Вызвано пользователем {ctx.author.display_name}', icon_url=ctx.author.display_avatar.url)
    emb.timestamp = ctx.created_at
    await ctx.send(embed=emb)

@bot.slash_command(description="Хелп") # Откладываем ответ
async def хелп(ctx):    
    embed = disnake.Embed(title="Список команд", description="*Ниже перечислены доступные команды* \n ", color=colemb)
    embed.add_field(name="📊 Экономика и уровни", value="  `/баланс` `/ранг` `/установить_ранг` `/сбросить_ранг` `/рулетка` `/лидерборд` `/work`", inline=False)
    embed.add_field(name="🛠️ Модерация", value="`/очистить` `/бан` `/кик` `/варн` `/разбан`", inline=False)
    embed.add_field(name="🆘 Информация", value="`/сервер` `/инфо` `/пинг`", inline=False)
    embed.add_field(name="ℹ️ Другое", value="`/калькулятор` `/повтори` `/число`", inline=False)
    embed.set_footer(text=f"Вызвано пользователем {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.send(embed=embed)
    
    
    
    
    
# Другие команды
@bot.slash_command(description="Предложите команду для улучшения бота.")
async def предложить_команду(ctx, *, suggestion):
    print(f"Поступило новое предложение. От пользователя {ctx.author.display_name}. Предложение {suggestion}")
    # Здесь должен быть ваш метод записи или обработки предложения
    await ctx.send("Ваше предложение принято. Спасибо!")

@bot.slash_command(description="Показывает рандомное число")
async def число(ctx):
    random_number = random.randint(1, 100000)
    await ctx.send(f'{random_number}')

@bot.slash_command(description="2+2=5")
async def калькулятор(ctx, number1: int, number2: int):
    try:
        summ = number1 + number2
        summ2 = number1 - number2
        summ3 = number1 * number2
        summ4 = number1 / number2
        print(f'Сумма чисел: {summ}')
        await ctx.response.send_message(f"Результаты: \n \n Сложение: {summ} \n Вычитание: {summ2} \n Умножение: {summ3} \n Деление: {summ4}", ephemeral=True)
    except ValueError:
        await ctx.response.send_message('Ошибка: введите числа.', ephemeral=True)

@bot.slash_command(description="Повторяет сообщение пользователя.")
async def повтори(ctx, *, message):
    await ctx.send(message)

# Запуск бота
bot.run(token)

