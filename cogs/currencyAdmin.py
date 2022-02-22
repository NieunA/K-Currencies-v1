import asyncio
from enum import Enum
from typing import List, Union

import discord
from discord import AllowedMentions, Color, DMChannel, Embed, Member, Role, TextChannel
from discord.ext import commands

from modules import accessToDB, customErrors, log


class CurrencyAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        if type(ctx.channel) == DMChannel:
            await ctx.send('이 명령어는 개인 메시지에서 사용하실 수 없어요!')
            return False

        try:
            guild_data = await accessToDB.getServerData(ctx.guild.id)
            role = ctx.guild.get_role(guild_data['controlRoleID'])

            if role is None:
                role = await ctx.guild.create_role(name='은행원', color=Color.green())
                await accessToDB.setServerData(ctx.guild.id, {'controlRoleID': role.id})

            if role in ctx.author.roles:
                return True
            else:
                await ctx.send(f'{role.mention} 역할을 가지고 있어야 사용할 수 있어요!', allowed_mentions=AllowedMentions.none())
                return False
        except customErrors.NoServerData:
            await ctx.send(f'우선 서버의 관리자에게 요청해 서버를 등록해주세요.'
                           f'서버 등록 명령어는 `{ctx.prefix}서버등록` 입니다.')
            return False

    @commands.command(name='관리역할')
    async def set_role(self, ctx: commands.Context, role_name: str):
        try:
            guild_data = await accessToDB.getServerData(ctx.guild.id)
            old_role = ctx.guild.get_role(guild_data['controlRoleId'])
            new_role: Role

            if old_role is not None:
                new_role = await ctx.guild.create_role(name=role_name, color=old_role.color)
                for member in old_role.members:
                    await member.add_roles(new_role)
                await old_role.delete()
            else:
                new_role = await ctx.guild.create_role(name=role_name, color=Color.green())

            await accessToDB.setServerData(ctx.guild.id, {'controlRoleId': new_role.id})
            await ctx.send(f'관리 역할을 {new_role.mention}(으)로 설정했어요!', allowed_mentions=AllowedMentions.none())

            await log.log(self.bot, ctx.guild.id, '관리역할 변경', f'{ctx.author.mention}님이 관리역할 변경')
        except commands.MissingPermissions:
            await ctx.send("'역할 관리' 권한이 필요해요!")

    @commands.command(name='지급', aliases=['회수', '보유금설정', '보유금', '소유금'])
    async def modify_money(self,
                           ctx: commands.Context,
                           target: Union[discord.Member, discord.Role, str] = None,
                           amount: float = None):
        class Target(Enum):
            MEMBER = '%m'
            ROLE = '%r'
            EVERYONE = '%e'

        def get_description():
            _desc = f'{ctx.author.mention}님이 {target_type.value} %g' \
                .replace('%m', f'{target.mention}님께') \
                .replace('%r', f'{target.mention} 역할을 가진 분들께') \
                .replace('%e', f'모든 분들께')
            if is_setting:
                _desc = _desc.replace('께', '의').replace('%g', f'소유 금액을 {amount}(으)로 설정했어요!')
            else:
                _desc = _desc.replace('%g', f'{amount}만큼 {"지급했어요" if is_giving else "회수했어요"}!')
            return _desc

        if target is None:  # TODO: Handle this case properly
            return
        if amount is None:  # TODO: Handle this case properly
            return
        if amount == 0:  # TODO: Handle this case properly
            return
        if ctx.invoked_with == '회수':
            amount = -abs(amount)

        is_setting = ctx.invoked_with in ['보유금설정', '보유금', '소유금']
        is_giving = amount > 0

        target_type: Target
        members: List[Member]
        if isinstance(target, Member):
            target_type = Target.MEMBER
            members = [target]
        elif isinstance(target, Role):
            target_type = Target.ROLE
            members = target.members
        elif target in ['전체', '모두', 'everyone']:
            target_type = Target.EVERYONE
            members = await ctx.guild.fetch_members(limit=None).flatten()
        else:  # TODO: Handle this case properly
            return

        for member in members:
            member_data = await accessToDB.getUserData(ctx.guild.id, member.id)
            if is_setting:
                member_data['money'] = amount
            else:
                member_data['money'] += amount
            await accessToDB.setUserData(ctx.guild.id, member.id, member_data)

        description = get_description()
        await ctx.send(description, allowed_mentions=AllowedMentions.none())
        await log.log(self.bot,
                      ctx.guild.id,
                      f'화폐 {"지급" if is_giving else "회수"}',
                      description
                      )

    @commands.command(name='서버초기화')
    async def reset_guild(self, ctx: commands.Context):
        await ctx.send('서버 초기화는 지원 서버에서 문의해주세요.'
                       '지원 서버 링크: https://discord.gg/wThxdtB')

    # ----------------------------------------------------------------------------------------------------------------------

    @commands.group(name='설정')
    async def settings(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return

        guild_data = await accessToDB.getServerData(ctx.guild.id)
        control_role = ctx.guild.get_role(guild_data['controlRoleId'])
        log_channel = ctx.guild.get_channel(guild_data['logChannelID'])

        embed = Embed(title=f'{ctx.guild.name} 설정')
        embed.description = f'서버 ID: `{ctx.guild.id}`\n' \
                            f'설정 방법은 `{ctx.prefix}도움 명령어 관리` 명령어를 참고해주세요.'
        embed.add_field(name='화폐명', value=guild_data['currency'])
        embed.add_field(name='위치', value='왼쪽' if guild_data['locate'] == 0 else '오른쪽')
        embed.add_field(name='\u200b', value='\u200b')

        if control_role is None:
            embed.add_field(name='관리 역할', value='역할이 없어요!')
        else:
            embed.add_field(name='관리 역할', value=f'{control_role.mention}\nID: `{control_role.id}`')

        if log_channel is None:
            embed.add_field(name='로그 채널', value='로그 채널이 없어요!')
        else:
            embed.add_field(name='로그 채널', value=f'{log_channel.mention}\n ID: `{log_channel.id}`')

        embed.add_field(name='\u200b', value='\u200b')

        embed.add_field(name='채팅 보상 (1분마다)', value=str(guild_data['chatReward']))
        embed.add_field(name='순위 기능', value='활성화' if guild_data['showRanking'] == 1 else '비활성화')
        embed.add_field(name='송금 기능', value='활성화' if guild_data['sendMoney'] == 1 else '비활성화')

        await ctx.send(embed=embed)

    @settings.group(name='화폐', invoke_without_command=False)
    async def currency(self, ctx: commands.Context):
        await ctx.send('세부항목이 올바르지 않아요!\n'
                       f'{", ".join(self.currency.commands)} 중 하나를 입력해주세요.')

    @currency.command(name='이름', aliases=['단위'])
    async def set_currency_name(self, ctx: commands.Context, *, name: str = None):
        if name is None or name == '':
            name = '(없음)'

        if len(name) > 20:
            await ctx.send('화폐 단위의 길이는 최대 20자를 넘을 수 없습니다.')
            return

        await accessToDB.setServerData(ctx.guild.id, {'currency': name})
        await ctx.send(f'화폐 단위를 `{name}`(으)로 변경 완료!', allowed_mentions=AllowedMentions.none())
        await log.log(self.bot, ctx.guild.id, '화폐 단위 변경', f'{ctx.author.mention}님이 화폐 단위를 {name}(으)로 변경')

    @currency.command(name='위치')
    async def set_unit_position(self, ctx: commands.Context):
        message = await ctx.send('화폐 표기 시의 화폐 단위 표기 위치를 지정해주세요.\n'
                                 '예) ⬅: $20, ➡: 20$')

        await message.add_reaction('⬅')
        await message.add_reaction('➡')

        def check(r, u):
            return str(r) in ['⬅', '➡'] and u.id == ctx.author.id

        try:
            (reaction, user) = await self.bot.wait_for('reaction_add', check=check, timeout=15)

            position = 0 if str(reaction) == '⬅' else 1
            position_locale = '왼쪽' if position == 0 else '오른쪽'
            await accessToDB.setServerData(ctx.guild.id, {'locate': position})

            await ctx.send(f'화폐 단위 표기 위치를 {position_locale}으로 설정 완료!')
            await log.log(
                self.bot,
                ctx.guild.id,
                '화폐 단위 변경',
                f'{ctx.author.mention}님이 화폐 단위 표기 위치를 {position_locale}으로 변경'
            )
        except asyncio.TimeoutError:
            await ctx.send('입력 시간이 초과되었습니다.')

    @settings.command(name='로그채널')
    async def set_log_channel(self, ctx: commands.Context, channel: TextChannel):
        await accessToDB.setServerData(ctx.guild.id, {'logChannelID': channel.id})
        await ctx.send(f'로그 채널을 {channel.mention}(으)로 설정 완료!')

    @settings.group(name='보상')
    async def reward(self, ctx):
        pass

    @reward.command(name='채팅')
    async def set_chatting_reward(self, ctx: commands.Context, amount: float):
        await accessToDB.setServerData(ctx.guild.id, {'chatReward': amount})
        await self.bot.get_cog('Events').addServer(ctx.guild)
        await ctx.send(f'채팅 시 보상을 {await accessToDB.getMoney(ctx.guild.id, amount)}(으)로 설정 완료!')

    @settings.group(name='기능')
    async def feature(self, ctx: commands.Context, key: str, value: str = None):
        features = {
            '순위': {
                'column': 'showRanking',
                'default': 1
            },
            '송금': {
                'column': 'sendMoney',
                'default': 0
            },
            '재가입시초기화': {
                'column': 'reregisterReset',
                'default': 0
            },
        }

        feature: dict
        final: int

        if key in features.keys():
            feature = features[key]
        else:
            await ctx.send('설정할 기능의 이름을 확인해주세요!')
            return

        if value is None:  # Toggle the feature
            guild_data = await accessToDB.read(
                f'SELECT {feature["column"]} FROM "serversData" WHERE serverID=?',
                (ctx.guild.id,)
            )

            final = 1 if guild_data[0][feature['column']] == 0 else 0
        else:
            value = value.lower()
            if value in ['true', 'o', '1', '활성화', 'on', '켜기']:
                final = 1
            elif value in ['false', 'x', '0', '비활성화', 'off', '끄기']:
                final = 0
            elif value in ['default', '기본', '기본값', '초기화', 'reset']:
                final = feature['default']
            else:
                await ctx.send('O 또는 X로 입력해주세요!')
                return

        await accessToDB.setServerData(ctx.guild.id, {feature['column']: final})
        await ctx.send(f'{key} 기능이 {"활성화" if final == 1 else "비활성화"}되었어요!')


def setup(bot):
    bot.add_cog(CurrencyAdmin(bot))
