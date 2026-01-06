**Enter following command to configure the bot **
```bash
python -m venv Botfinal

.\Botfinal\Scripts\activate

cd Botfinal/Bot
pip install -r requirements.txt
cd ..

python -m Bot.env 
#add your configuration in config/config.json file

# Bot is ready to trade fire below command
python -m Bot.Trade

