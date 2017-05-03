# auth_oauth_extended    [have merged into  odoo-cn/addons ]

for qq/weixin/weibo authorization and login into Odoo

provider | authorize url | validation url | user detail url | scope
--------|-------------|-----------|---------|-----
qq | https://graph.qq.com/oauth2.0/authorize | https://graph.qq.com/oauth2.0/me | https://graph.qq.com/oauth2.0/get_user_info | userinfo
weixin| https://open.weixin.qq.com/connect/oauth2/authorize | https://api.weixin.qq.com/sns/oauth2/access_token | https://api.weixin.qq.com/sns/userinfo | snsapi_userinfo
weibo | https://api.weibo.com/oauth2/authorize | https://api.weibo.com/oauth2/access_token | https://api.weibo.com/oauth2/get_token_info | email |
dingtalk | https://oapi.dingtalk.com/connect/oauth2/sns_authorize |  https://oapi.dingtalk.com/sns/get_sns_token  | https://oapi.dingtalk.com/sns/getuserinfo | snsapi_login


**comment**

 for qq oauth provider, need to fix controller to remove '+' from the returned json like this.

 ```
/auth_oauth/signin?access_token=CC75562316165BAC74675C1853121E85&expires_in=7776000&state=%7B%22p%22%3A%2B12%2C%2B%22r%22%3A%2B%22http%253A%252F%252Fo.odoo123.com%252Fweb%253F%22%2C%2B%22d%22%3A%2B%22odoo123%22%7D
```


 decode as 

```
/auth_oauth/signin?access_token=CC75562316165BAC74675C1853121E85&expires_in=7776000&state={"p":+12,+"r":+"http%3A%2F%2Fo.odoo123.com%2Fweb%3F",+"d":+"odoo123"}
```

 
so need replace '+' with space 

```
kw = simplejson.loads(simplejson.dumps(kw).replace('+',''))
```
