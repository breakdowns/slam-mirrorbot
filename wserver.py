# -*- coding: utf-8 -*-
# (c) YashDK [yash-dk@github]

import os
import time
import logging
import qbittorrentapi as qba
import asyncio

from aiohttp import web
import nodes

LOGGER = logging.getLogger(__name__)

routes = web.RouteTableDef()

page = """
<html>
<head>
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha256-4+XzXVhsDmqanXGHaHvgh1gMQKX40OUvDEBTu8JcmNs=" crossorigin="anonymous"></script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
  padding: 20px;
}
ul { 
  list-style: none;
  margin: 5px 20px;
}
li {
  margin: 10px 0;
}


p { font-size: 12px; margin: 24px;}
</style>
</head>
<body>
<h1>slam-tg-mirror-bot: <a href="https://github.com/breakdowns/slam-tg-mirror-bot">@Github</a></h1>
<form action="{form_url}" method="POST">

{My_content}

<input type="submit" name="Select these files ;)">
</form>

<script>
$('input[type="checkbox"]').change(function(e) {

  var checked = $(this).prop("checked"),
      container = $(this).parent(),
      siblings = container.siblings();
/*
  $(this).attr('value', function(index, attr){
     return attr == 'yes' ? 'noo' : 'yes';
  });
*/
  container.find('input[type="checkbox"]').prop({
    indeterminate: false,
    checked: checked
  });

  function checkSiblings(el) {

    var parent = el.parent().parent(),
        all = true;

    el.siblings().each(function() {
      let returnValue = all = ($(this).children('input[type="checkbox"]').prop("checked") === checked);
      return returnValue;
    });
    
    if (all && checked) {

      parent.children('input[type="checkbox"]').prop({
        indeterminate: false,
        checked: checked
      });

      checkSiblings(parent);

    } else if (all && !checked) {

      parent.children('input[type="checkbox"]').prop("checked", checked);
      parent.children('input[type="checkbox"]').prop("indeterminate", (parent.find('input[type="checkbox"]:checked').length > 0));
      checkSiblings(parent);

    } else {

      el.parents("li").children('input[type="checkbox"]').prop({
        indeterminate: true,
        checked: false
      });

    }

  }

  checkSiblings(container);
});
</script>
</body>
</html>

"""

code_page = """
<html>
<head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous">
<title>
Slam Torrent Files
</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<div class="container">
<form action="{form_url}">
  <div class="form-group">
    <label for="pin_code">Pin Code</label>
    <input type="text" class="form-control" name="pin_code" placeholder="Enter code to access the torrent">
    <small class="form-text text-muted">Dont mess around. You download will get messed up.</small>
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
</div>
</body>
</html>
"""


@routes.get('/slam/files/{hash_id}')
async def list_torrent_contents(request):

    torr = request.match_info["hash_id"]

    gets = request.query

    if not "pin_code" in gets.keys():
        rend_page = code_page.replace("{form_url}",f"/slam/files/{torr}")
        return web.Response(text=rend_page,content_type='text/html')

    
    client = qba.Client(host="localhost",port="8090",username="admin",password="adminadmin")
    client.auth_log_in()
    try:
      res = client.torrents_files(torrent_hash=torr)
    except qba.NotFound404Error:
      raise web.HTTPNotFound()
    count = 0
    passw = ""
    for n in str(torr):
        if n.isdigit():
            passw += str(n)
            count += 1
        if count == 4:
            break
    if isinstance(passw, bool):
        raise web.HTTPNotFound()
    pincode = passw
    if gets["pin_code"] != pincode:
        return web.Response(text="Incorrect pin code")

    
    par = nodes.make_tree(res)
    
    cont = ["",0]
    nodes.create_list(par,cont)

    rend_page = page.replace("{My_content}",cont[0])
    rend_page = rend_page.replace("{form_url}",f"/slam/files/{torr}?pin_code={pincode}")
    client.auth_log_out()
    return web.Response(text=rend_page,content_type='text/html')
    

async def re_verfiy(paused, resumed, client, torr):

    paused = paused.strip()
    resumed = resumed.strip()
    if paused:
        paused = paused.split("|")
    if resumed:
        resumed = resumed.split("|")
    k = 0
    while True:
        
        res = client.torrents_files(torrent_hash=torr)
        verify = True
        
        for i in res:
            if str(i.id) in paused:
                if i.priority == 0:
                    continue
                else:
                    verify = False
                    break

            if str(i.id) in resumed:
                if i.priority != 0:
                    continue
                else:
                    verify = False
                    break


        if not verify:
            LOGGER.info("Reverification Failed :- correcting stuff")
            # reconnect and issue the request again
            client.auth_log_out()
            client = qba.Client(host="localhost",port="8090",username="admin",password="adminadmin")
            client.auth_log_in()
            try:
                client.torrents_file_priority(torrent_hash=torr,file_ids=paused,priority=0)
            except:
                LOGGER.error("Errored in reverification paused")
            try:
                client.torrents_file_priority(torrent_hash=torr,file_ids=resumed,priority=1)
            except:
                LOGGER.error("Errored in reverification resumed")
            client.auth_log_out()
        else:
            break
        k += 1
        if k >= 2:
            # avoid an infite loop here
            return False
    return True



@routes.post('/slam/files/{hash_id}')
async def set_priority(request):

    torr = request.match_info["hash_id"]
    client = qba.Client(host="localhost",port="8090",username="admin",password="adminadmin")
    client.auth_log_in()

    data = await request.post()
    resume = ""
    pause = ""
    data = dict(data)
    
    for i in data.keys():
        if i.find("filenode") != -1:
            node_no = i.split("_")[-1]

            if data[i] == "on":
                resume += f"{node_no}|"
            else:
                pause += f"{node_no}|"
            
    pause = pause.strip("|")
    resume = resume.strip("|")
    LOGGER.info(f"Paused {pause} of {torr}")
    LOGGER.info(f"Resumed {resume} of {torr}")
    
    try:
        client.torrents_file_priority(torrent_hash=torr,file_ids=pause,priority=0)
    except qba.NotFound404Error:
        raise web.HTTPNotFound()
    except:
        LOGGER.info("Errored in paused")
    
    try:
        client.torrents_file_priority(torrent_hash=torr,file_ids=resume,priority=1)
    except qba.NotFound404Error:
        raise web.HTTPNotFound()
    except:
        LOGGER.info("Errored in resumed")

    await asyncio.sleep(2)
    if not await re_verfiy(pause,resume,client,torr):
        LOGGER.error("The torrent choose errored reverification failed")
    client.auth_log_out()
    return await list_torrent_contents(request)

@routes.get('/')
async def homepage(request):

    return web.Response(text="<h1>See slam-tg-mirror-bot <a href='https://github.com/breakdowns/slam-tg-mirror-bot'>@GitHub</a> By <a href='https://github.com/breakdowns'>Breakdowns</a></h1>",content_type="text/html")

async def e404_middleware(app, handler):

  async def middleware_handler(request):

      try:
          response = await handler(request)
          if response.status == 404:
              return web.Response(text="<h1>404: Page not found</h2><br><h3>slam-tg-mirror-bot</h3>",content_type="text/html")
          return response
      except web.HTTPException as ex:
          if ex.status == 404:
              return web.Response(text="<h1>404: Page not found</h2><br><h3>slam-tg-mirror-bot</h3>",content_type="text/html")
          raise
  return middleware_handler

async def start_server():

    app = web.Application(middlewares=[e404_middleware])
    app.add_routes(routes)
    return app

async def start_server_async(port = 8080):

    app = web.Application(middlewares=[e404_middleware])
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner,"0.0.0.0", port).start()
