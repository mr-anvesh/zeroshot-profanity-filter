import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Mock environment variables before importing bot
os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"
os.environ["PROFANITY_THRESHOLD"] = "0.5"

# Import the bot module (we need to mock ProfanityFilter first to avoid loading the model)
with patch('profanity_filter.ProfanityFilter') as MockFilter:
    import bot

class TestBotLogic(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Setup mock filter
        self.mock_pf = bot.pf
        self.mock_pf.is_profane = MagicMock()
        self.mock_pf.censor_text = MagicMock()
        
        # Reset strikes
        bot.user_strikes.clear()
        
        # Setup mock update and context
        self.update = MagicMock()
        self.context = MagicMock()
        self.context.bot.ban_chat_member = AsyncMock()
        self.context.bot.send_message = AsyncMock()
        
        self.user = MagicMock()
        self.user.id = 12345
        self.user.first_name = "TestUser"
        self.user.mention_html = MagicMock(return_value="<a href='...'>TestUser</a>")
        
        self.message = MagicMock()
        self.message.from_user = self.user
        self.message.chat_id = -100123456
        self.message.delete = AsyncMock()
        
        self.update.message = self.message

    async def test_clean_message(self):
        self.message.text = "Hello world"
        self.mock_pf.is_profane.return_value = {"is_profane": False}
        
        await bot.handle_message(self.update, self.context)
        
        self.message.delete.assert_not_called()
        self.assertEqual(bot.user_strikes[self.user.id], 0)

    async def test_profane_message_strike_1(self):
        self.message.text = "Bad word"
        self.mock_pf.is_profane.return_value = {"is_profane": True}
        self.mock_pf.censor_text.return_value = "B** w***"
        
        await bot.handle_message(self.update, self.context)
        
        self.message.delete.assert_called_once()
        self.context.bot.send_message.assert_called_once()
        self.assertEqual(bot.user_strikes[self.user.id], 1)
        # Verify warning message contains strike count
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("Strike 1/3", kwargs['text'])

    async def test_profane_message_kick(self):
        self.message.text = "Bad word"
        self.mock_pf.is_profane.return_value = {"is_profane": True}
        
        # Simulate 2 previous strikes
        bot.user_strikes[self.user.id] = 2
        
        await bot.handle_message(self.update, self.context)
        
        self.message.delete.assert_called_once()
        self.context.bot.ban_chat_member.assert_called_once_with(self.message.chat_id, self.user.id)
        # Verify kick message
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("kicked", kwargs['text'])

if __name__ == '__main__':
    unittest.main()
