import logging
from nicegrill import utils
from database import snipsdb as nicedb, settingsdb as settings

logger = logging.getLogger(__name__)


class Snips:
    """Saves some texts to call on them literally anywhere and anytime"""

    async def snipxxx(message):
        """Adds a snip into the list. Separate it with comma(,)"""
        args = utils.arg_split_with(message, ",")
        reply = await message.get_reply_message()
        name = args[0]
        if len(args) == 0:
            await message.edit("<b>Enter the name of the snip first</b>")
            return
        if len(args) == 1 and not message.is_reply:
            await message.edit("<b>Enter or reply to a text to save as snip</b>")
            return
        if message.is_reply:
            if reply.media:
                value = (await message.client.send_message(settings.check_asset(), reply)).id
                media = True
            else:
                value = reply.message
                media = False
        else:
            value = args[1]
            media = False
        if not nicedb.check_one(name):
            nicedb.add(name, value, media)
        else:
            nicedb.update({"Key": name}, name, value, media)
        await message.edit(
            "<b>Snip </b><i>{}</i><b> successfully saved into the list."
            "Type </b><i>${}</i><b> to call it.</b>".format(name, name))

    async def remsnipxxx(message):
        """Removes a snip from the list."""
        snipn = utils.get_arg(message)
        if not snipn:
            await message.edit("<b>Please specify the name of the snip to remove.</b>")
            return
        if nicedb.check_one(snipn):
            nicedb.delete_one(snipn)
            await message.edit("<b>Snip </b><i>{}</i><b> successfully deleted</b>".format(snipn))
        else:
            await message.edit("<b>Snip </b><i>{}</i><b> not found in snips list</b>".format(snipn))

    async def remsnipsxxx(message):
        """Clears out the snip list."""
        if not nicedb.check():
            await message.edit("<b>There are no snips in the list to clear out.</b>")
            return
        nicedb.delete()
        await message.edit("<b>All snips successfully removed from the list.</b>")

    async def snipsxxx(message):
        """Shows saved snips."""
        snips = ""
        get = nicedb.check()
        if not get:
            await message.edit("<b>No snip found in snips list.</b>")
            return
        for snip in get:
            snips += "<b> ◍  " + snip["Key"] + "</b>\n"
        snipl = "<b>Snips that you saved: </b>\n\n" + snips
        await message.edit(snipl)

    async def othersxxx(message):
        """Turns on/off snips for others usage."""
        state = utils.get_arg(message)
        if state == "on":
            nicedb.delete_others()
            nicedb.set_others(True)
            await message.edit("<b>Snips are now open to use for anyone.</b>")
        elif state == "off":
            nicedb.delete_others()
            nicedb.set_others(False)
            await message.edit("<b>Snips are now turned off for others.</b>")
            return

    async def watchout(message):
        if not nicedb.check_one(message.text[1::]):
            return
        args = message.text
        if not nicedb.check_others():
            if message.sender_id != (await message.client.get_me()).id:
                return
        if args.startswith("$"):
            argsraw = args[1::]
            snip = nicedb.check_one(argsraw)
            value = (
                    snip["Value"] if not snip["Media"]
                    else await message.client.get_messages(settings.check_asset(), ids=snip["Value"]))
            if not snip["Media"]:
                if message.sender_id == (await message.client.get_me()).id:
                    await message.edit(value)
                else:
                    await message.reply(value)
            else:
                if message.sender_id == (await message.client.get_me()).id:
                    await message.client.send_message(message.chat_id, value)
                    await message.delete()
                else:
                    await message.client.send_message(message.chat_id, value, reply_to=message.id)
