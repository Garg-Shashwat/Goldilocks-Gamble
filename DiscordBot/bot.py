import discord
import random
import os
from discord.ext import commands
import pandas as pd
import math
import time

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '.', description="type .help for available commands", intents = intents,help_command=None)
#add aliases to commands
#add poem and epilogue
#end conditions
dev_channel=825646165294579723
announcement=825646023456063489
waittime = 5
size = {1:"Dwarf", 2:"Terrestial", 3:"Super-Earth"} #large is good
distance = {2:"Cytherean", 3:"Gaian", 1:"Martian"} #ideal is good
mass = {1:"Sub-Earth", 2:"Mid-Earth", 3:"Midplanet"} 

data=pd.read_csv('data.csv')

d_era = {
    1:"Ancient",
    2:"Medieval",
    3:"Industrial",
    4:"Information",
    5:"Future",
    6:"Future"}

crisis_aliases={
    'floods':'Floods',
    'drought':'Droughts',
    'famine':'Famine',
    'tsunami':'Tsunami',
    'cyclone':'Cyclone',
    'earthquake':'Earthquake',
    'fire':'Forest Fires',
    'plague':'Plague',
    'fuel':'Fuel Shortage',
    'wars':'Great Wars',
    'warming':'Global Warming',
    'watershortage':'Water Shortage',
    'corona':'Corona',
    'ebola':'Ebola',
    'flare':'Solar Flare',
    'nuclear':'Nuclear Disaster',
    'ozone':'Ozone Depletion',
    'ai':'AI Coup'}

res_aliases={
    'seeds':'Population Seed(s)',
    'oxygen':'Oxygen',
    'co2':'Carbon Dioxide',
    'pollute':'Pollutants',
    'water':'Water',
    'land':'Land',
    'temp':'Temperature',
    'population':'Population',
    'biomes':'Biome(s)',
    'mine':'Mine(s)',
    'factory':'Factory(s)',
    'farms':'Farm(s)',
    'fuel':'Oil Well(s)',
    'ai':'AI',
    'satellite':'Shuttle Mines',
    'dyson':"Dyson's Sphere"}

initial_values={
    'era':1,
    'story':0,
    'asked':0,
    'size':0,
    'distance':0,
    'mass':0,
    'mult':0,
    'si':0,
    'di':0,
    'credits':5000.0,
    'credch':0,
    'population':1000,
    'change':0,
    'iq':10,
    'iqch':0,
    'pdensity':1,
    'oxygen':25.0,
    'co2':0,
    'pollute':0,
    'water':0,
    'land':0,
    'temp':0,
    'biomes':0,
    'farms':0,
    'factory':0,
    'fuel':0,
    'mine':0,
    'ai':0,
    'satellite':0,
    'dyson':0}
@client.command()
async def start(ctx):
    if ctx.channel.id == dev_channel:
        a_cont=await client.get_context(await client.get_channel(announcement).get_partial_message(client.get_channel(announcement).last_message_id).fetch())

        if os.path.isfile('data.csv'):      #make the file alag se
            os.remove('data.csv')
        with open('data.csv','a') as data_file:
            data_file.write('id,name,'+','.join(initial_values.keys()))
            for ch in a_cont.channel.category.text_channels:
                if ch!=a_cont.channel:
                    data_file.write('\n'+str(ch.id)+','+str(ch.name))
        df=pd.read_csv('data.csv')
        teams = len(df)
        message=""
        for line in open('./start_message.txt',encoding='utf8'):
            message = message + line
        embed=discord.Embed(title='Prologue', 
            description = f'{message}',
            color = discord.Colour.red())
        await a_cont.send(embed=embed)
        df=initialise(df)
        for i in range(teams):
            id = [int(x) for x in df.index][i]
            chan=client.get_channel(int(id))
            mess=await chan.get_partial_message(chan.last_message_id).fetch()
            cont=await client.get_context(mess)
            await stats(cont)

def initialise(df):
    #Active parameter chart
    water = {1:50, 2:60, 3:70}
    temp = {2:17 , 3:14 , 1:11}
    multiplier = {1:0.95, 2:1.0, 3:1.05}
    #Passive parameters
    with open('parameters.csv','w') as para_file:
            para_file.write('turn,2')
            para_file.close()
    for i in range(len(df.index)):
        for res in range(2,len(df.keys())):
            df.iloc[i,res]=0
        initial_values['size']=random.choice(list(size.keys()))
        initial_values['distance']=random.choice(list(distance.keys()))
        initial_values['mass']=initial_values['size'] 

        #Active parameters
        initial_values['water'] = water[initial_values['size']]
        initial_values['land'] = 100 - initial_values['water']
        initial_values['temp'] = temp[initial_values['distance']]

        initial_values['si']= round(0.000044*initial_values['water']*initial_values['land']*initial_values['oxygen']*(60-initial_values['oxygen']),2)
        initial_values['mult']=multiplier[initial_values['size']]
        
        #Initial resources
        initial_values['biomes']=random.randrange(40,60) #randomising flora and fauna diversity
        value_list=list(initial_values.values())
        
        for res in range(1,len(df.keys())):
            df.iloc[i,res]=value_list[res-1]
    df.to_csv('data.csv')
    return df

async def the_end(ctx):
    await ctx.send('**Game Over! Well played!**')
    #await client.logout()

async def new_era(ctx, era):
    await ctx.send("Congratulations! Your civilization has progressed to " + d_era[era] + " era.")
    await ctx.send("You have uncovered a memory Cache.")
    time.sleep(waittime)
    message=""
    for line in open('./story'+str(era-1)+'1.txt',encoding='utf8'):
        message = message + line
    await ctx.send(message)
    time.sleep(waittime)
    message=""
    for line in open('./story'+str(era-1)+'2.txt',encoding='utf8'):
        message = message + line
    await ctx.send(message)
    time.sleep(waittime)
    #else:
    if era==6:
        message=""
        for line in open('./poem.txt',encoding='utf8'):
            message = message + line
        await ctx.send(message)
        await the_end(ctx)


@client.command()
async def buy(ctx,resource,quantity=1):
    team=ctx.channel.id
    unlocked,exhaust=buy_resource(team,resource,quantity)
    if unlocked:
        if not exhaust:
            await ctx.send(str(quantity)+' '+res_aliases[resource] + " successfully bought! \nPlease check your stats.")
        else:
            await ctx.send("You don\'t have the credits to perform this transaction. Kindly wait for the next turn.")
    else:
        await ctx.send("Resource not available.")

def buy_resource(id,resource,quantity):
    cred=0
    exhaust=0
    rf = pd.read_csv('mapping.csv')
    df=data.loc[data['id']== id]
    era=df['era']
    resf=pd.read_csv('resources.csv',index_col=0)
    if resource in resf.index and resf.loc[resource,str(era)]>0:
        cred=resf.loc[resource,'6']
        updated_creds=df['credits']-int(quantity)*cred*df['mult']
        if updated_creds<0:
            exhaust=1
        else:
            df['credch']=int(df['credch']+updated_creds-df['credits'])
            df['credits']=updated_creds
            if resource.lower() == 'seeds':
                seed = int(5*int(df['population'])/100 + float(df['si'])*5)
                df['population']=int(df['population']+int(quantity)*seed)
                df['change']=df['change']+int(quantity)*seed
            else:
                df[resource]+=int(quantity)
                di_i = int(quantity)*resf.loc[resource,str(era)]
                df['di']+=round(di_i,2)
                df['iqch']=round(df['iqch']+initial_values['iq'] + 241/(1+math.exp(-0.02*(df['di']-150)))-df['iq'],2)
                df['iq']=round(241/(1+math.exp(-0.02*(df['di']-150))),2)
            for index in rf.keys()[1:]:
                df.loc[id,index]=df.loc[id,index]+int(quantity)*float(rf.loc[rf['f']==resource,index])
    else:
        return False,exhaust
    data.loc[data['id']==id,[data.keys()[1:]]]=df[data.keys()[1:]].to_list()
    data.to_csv('data.csv')
    return True,exhaust

@client.command()
async def turn(ctx):
    if ctx.channel.id == dev_channel:
        
        teams = len(data)
        turn=0
        with open('parameters.csv','r+') as para_file:
            turn=[row.split(sep=',')[1] for row in para_file]
            para_file.seek(0,os.SEEK_SET)
            para_file.write('turn,'+str(int(turn[0])+1))
            para_file.close()
        if int(turn[0])%5==0:
            await leaderboard(await client.get_context(await client.get_channel(announcement).get_partial_message(client.get_channel(announcement).last_message_id).fetch()))
        id=df['id'].to_list()
        for i in id:
            df=data.loc[data['id']== i]
            # id = [int(x) for x in df.index][i]
            chan=client.get_channel(int(i))
            mess=await chan.get_partial_message(chan.last_message_id).fetch()
            cont=await client.get_context(mess)
            water=df['water']
            land=df['land']
            pollute=df['pollute']
            di=df['di']
            biomes=df['biomes']
            size_p=df['size']
            oxygen=df['oxygen']
            era=df['era']
            iq=initial_values['iq'] + 241/(1+math.exp(-0.02*(di-150)))
            if iq>=240:
                era=6
            if iq>212:
                era=5
            elif iq>120:
                era=4
            elif iq>75:
                era=3
            elif iq>30:
                era=2
            if df['era']!=era:
                await new_era(cont,era)
            
            df['era']=era
            population=df['population']
            pdensity=int(iq/10+1)
            si= 0.00004*water*(land**1.3)*(1-pollute/100)*oxygen*(60-oxygen)
            pop_capacity=pdensity*land*int(size_p)*1000
            new_pop=int(population*si*0.03*(1-population/pop_capacity))
            df['change']=df['change']+new_pop-population
            df['iq']=iq  
            df['population']=new_pop
            df['pdensity']=pdensity
            df['credch']=int(df['credch']+(si*(1+di)*(1.2**era)))
            df['credits'] = int(df['credits'] + (si*(1+di)*(1.2**era)))
            
            await cont.send(("Turn "+turn[0]+' started!'))
            crisis,death=crisis_for_era(id)
            df['change']-=death
            if crisis!='none':
                await cont.send('Your civilization is hit by '+crisis_aliases[crisis]+'.\nYou lost '+str(death)+' people.')
            await stats(cont)
            data.loc[data['id']== i,[data.keys()[1:]]]=df[data.keys()[1:]].to_list()
        data.to_csv('data.csv')

def crisis_for_era(id):
    df=data.loc[data['id']== id]
    era=df['era']
    water=df['water']
    population=df['population']
    farm=df['farms']
    oxygen=df['oxygen']
    co2=df['co2']
    factory=df['factory']
    satellite=df['satellite']
    pollute=df['pollute']
    crisis='none'
    cf=pd.read_csv('crisis.csv')
    era_df=cf.loc[cf['era']==era]

    era_list=list(era_df['crisis'])
    if 'floods' in era_list and water < 40:
        era_list.remove('floods')
    if 'drought' in era_list and water > 30:
        era_list.remove('drought')
    if 'watershortage' in era_list and water > 40:
        era_list.remove('watershortage')
    if 'cyclone' in era_list and water < 50: 
        era_list.remove('cyclone')
    if 'tsunami' in era_list and water < 50:
        era_list.remove('tsunami')
    if 'ozone' in era_list and pollute < 50:
        era_list.remove('ozone')
    if 'warming' in era_list and (oxygen > 13 and co2 < 10):
        era_list.remove('warming')
    if 'famine' in era_list and (1000*farm/population > 1  and water > 35):
        era_list.remove('famine')
    
    chance = random.random()
    if chance < .75:
        crisis = random.choice(era_list)
    death=0
    if crisis!='none':
        death = int(int(population)*float(era_df.loc[era_df['crisis']==crisis,'death'])/100)
        population=int(population)-death
        for index in era_df.loc[era_df['crisis']==crisis].keys()[3:]:
            df[index]=locals()[str(index)]*(1-float(era_df.loc[era_df['crisis']==crisis,index])/100)
        df['population']=population
    if crisis == 'flare':
        satellite = int(satellite*0.8)
        df['satellite']=satellite
    elif crisis == 'ai':
        factory = int(factory*1.2)
        df['factory']=factory
    elif crisis ==  'floods' or crisis == 'drought':
        farm = int(farm*0.9)
        df['farms']=farm

    data.loc[data['id']==id,[data.keys()[1:]]]=df[data.keys()[1:]].to_list()    
    data.to_csv("data.csv")
    return crisis,death

@client.command()
async def stats(ctx):
    id=ctx.channel.id
    df=data.loc[data['id']== id]
    era=int(df['era'])
    turn=[row.split(sep=',')[1] for row in open('parameters.csv','r')][0]
    embed=discord.Embed(title='Stats',
        description = f"Your planet : {str(df['name'])}\n Current Era : { d_era[int(df['era'])]}\n Population : { float(df['population'])} ({'{:+}'.format(df['change'])}) \n Average IQ : { round(df['iq'],2)} ({'{:+}'.format(df['iqch'])})\n Credits : {round(float(df['credits']),2)} ({'{:+}'.format(df['credch'])})\n"
                      f"-----------------------------------------------\n"
                      f"Resources\n"
                      f"-----------------------------------------------\n"
        ,color=discord.Colour.blue()
    )
    df['change']=0      #why??
    df['credch']=0
    df['iqch']=0
    for i in df.columns.to_list()[df.columns.to_list().index('oxygen'):]:        #traverse the dataframe from oxygen till the end
        embed.add_field(name=res_aliases[i], value=round(float(df[i]),2), inline=True)
    embed.set_footer(text=f"Type : {str(size[df['size']])}\t\t\t\t\t\tTurn : {str(int(turn)-1)}\nOrbit Size : {str(distance[df['distance']])}\nMass : {str(mass[df['mass']])}")
    await ctx.send(embed=embed)
    data.loc[data['id']==id,[data.keys()[1:]]]=df[data.keys()[1:]].to_list()  
    data.to_csv('data.csv')
    await buy_list(ctx, era)

async def buy_list(ctx, era):
    mult=float(data.loc[data['id']==ctx.channel.id,'mult'])
    res_file=pd.read_csv('resources.csv',index_col=0)
    embed = discord.Embed(title="Resource Buy List",color=discord.Colour.red(), description='Resources available')
    for i in res_file.index:
        if float(res_file.loc[i,str(era)]):
            embed.add_field(name=i+' : '+str(float(res_file.loc[i,'6'])*mult)+" credits", value='Buy 1 '+res_aliases[i] ,inline=False)
    await ctx.send(embed=embed)

@client.command()
async def leaderboard(ctx):
    teams = len(data)
    embed=discord.Embed(title='Leaderboard',description='------------------------------------------------------',color=discord.Color.gold())
    # name=[]
    # era=[]
    # score=[]
    sorted_df=pd.DataFrame(columns=['name','era','score'],index=range(teams))
    for i in range(teams):
        sorted_df.loc[i,'name']=data.iloc[i,list(data.columns).index('name')]
        sorted_df.loc[i,'era']=d_era[data.iloc[i,list(data.columns).index('era')]]
        sorted_df.loc[i,'score']=str(round(data.iloc[i,list(data.columns).index('si')]*data.iloc[i,list(data.columns).index('di')],2)) #needed in string to display in discord

    
    sorted_df.sort_values(by='score',ascending=False,inplace=True)
    name=sorted_df.name.to_list()
    era=sorted_df.era.to_list()
    score=sorted_df.score.to_list()
    # for i in range(teams):
    #     name.append(sorted_df.iloc[i,0])
    #     era.append(sorted_df.iloc[i,1])
    #     score.append(sorted_df.iloc[i,2])

    embed.add_field(name='Team', value="\n".join(name), inline=True)
    embed.add_field(name='Era', value="\n".join(era), inline=True)
    embed.add_field(name='Score', value="\n".join(score), inline=True)
    await ctx.send(embed=embed)

@client.command()
async def id(ctx):
    print("ID requested:", ctx.channel.id)
    print("Channel: ", ctx.channel.name)

'''@client.event
async def on_message(message):
    print(f'{message.author} sends',message.content)'''

@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")

for filename in os.listdir('./cogs'):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client_id='NzczNDUzMDE5MzY2NDI0NTg2.X6JcQQ.68IPgG2VJuaj5dxS-m3SmuHe1jc'
client.run(client_id)
