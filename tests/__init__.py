import asyncio
from datetime import datetime, timedelta

async def bootstrap():
    print(datetime.now().astimezone() - timedelta(minutes=25))
    print(datetime.now())
    # httpclient = aiohttp.ClientSession()
    #
    # username = os.getenv("ONDUS_USERNAME")
    # password = os.getenv("ONDUS_PASSWORD")
    # base_url = 'https://idp2-apigw.cloud.grohe.com/v3/iot/'
    # refresh_token = os.getenv('ONDUS_REFRESH_TOKEN')
    #
    # api = OndusApi(httpclient)
    # await api.login(username, password, refresh_token)
    #
    # locations = await api.get_locations()
    # rooms = await api.get_rooms(locations[0].id)
    # appliances = await api.get_appliances(locations[0].id, rooms[1].id)
    # notifications = await api.get_appliance_notifications(locations[0].id, rooms[1].id, appliances[0].id)
    # dashboard = await api.get_dashboard()
    #
    # print(dashboard)
    #
    # await httpclient.close()


asyncio.run(bootstrap())
