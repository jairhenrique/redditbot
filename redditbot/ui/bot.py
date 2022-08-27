import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

import redditbot.crawlers.reddit_crawler as rc
from redditbot.config import settings

DEFAULT_MESSAGE = """r/{subreddit} - [{upvotes} votos]
{title}
Link: {link}
Comentários: {comments}"""


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        text='Está sem o que fazer? Dá um confere no Reddit!'
    )


async def nada_para_fazer(update: Update, context: CallbackContext):
    args = context.args
    joined_args = str.join(';', args)  # If you pass separeted we join using ; separator

    subreddits = joined_args.split(';')

    if len(subreddits) == 0 or len(args) == 0:
        await update.message.reply_text(
            text='Digite o termo da procura, ex: /nadaparafazer dogs;python'
        )
        return

    await send_subreddit(update, subreddits)


async def send_subreddit(update, subreddits):
    canais_message = ', '.join([
        f'r/{subreddit}' for subreddit in subreddits
    ])
    await update.message.reply_text(
        text=f'Procurando o que está bombando em {canais_message}...'
    )
    threads = await rc.get_subreddits(subreddits)
    filtered_threads = rc.filter_by_votes(threads, min_votes=settings.MIN_VOTES)
    threads = rc.filter_by_votes(filtered_threads)
    for thread in threads:
        await update.message.reply_text(
            text=DEFAULT_MESSAGE.format(**thread)
        )
    if len(threads) == 0:
        await update.message.reply_text(
            text=f'Não encontrei nada bombando em {canais_message}'
        )


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    token = settings.TELEGRAM_TOKEN

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(
        CommandHandler('nadaparafazer', nada_para_fazer)
    )
    app.add_handler(
        CommandHandler('n', nada_para_fazer)
    )

    app.run_polling()


if __name__ == '__main__':
    main()
