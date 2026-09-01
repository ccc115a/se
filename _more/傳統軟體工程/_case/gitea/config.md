# config

* https://docs.gitea.io/zh-cn/config-cheat-sheet/

所有改变请修改 custom/conf/app.ini 文件

## Service (service)

```
ACTIVE_CODE_LIVE_MINUTES: 登录验证码失效时间，单位分钟。
RESET_PASSWD_CODE_LIVE_MINUTES: 重置密码失效时间，单位分钟。
REGISTER_EMAIL_CONFIRM: 启用注册邮件激活，前提是 Mailer 已经启用。
REGISTER_MANUAL_CONFIRM: false: 新注册用户必须由管理员手动激活,启用此选项需取消REGISTER_EMAIL_CONFIRM. (重要！)
DISABLE_REGISTRATION: 禁用注册，启用后只能用管理员添加用户。 (重要！)
SHOW_REGISTRATION_BUTTON: 是否显示注册按钮。 (重要！)
REQUIRE_SIGNIN_VIEW: 是否所有页面都必须登录后才可访问。 (重要！)
ENABLE_CACHE_AVATAR: 是否缓存来自 Gravatar 的头像。
ENABLE_NOTIFY_MAIL: 是否发送工单创建等提醒邮件，需要 Mailer 被激活。
ENABLE_REVERSE_PROXY_AUTHENTICATION: 允许反向代理认证，更多细节见：https://github.com/gogits/gogs/issues/165
ENABLE_REVERSE_PROXY_AUTO_REGISTRATION: 允许通过反向认证做自动注册。
ENABLE_CAPTCHA: 注册时使用图片验证码。
```

## Attachment (attachment)

```
ENABLED: 是否允许用户上传附件。
ALLOWED_TYPES: 允许上传的附件类型。比如：image/jpeg|image/png，用 */* 表示允许任何类型。
MAX_SIZE: 附件最大限制，单位 MB，比如： 4。
MAX_FILES: 一次最多上传的附件数量，比如： 5。
STORAGE_TYPE: local: 附件存储类型，local 将存储到本地文件夹， minio 将存储到 s3 兼容的对象存储服务中。
PATH: data/attachments: 附件存储路径，仅当 STORAGE_TYPE 为 local 时有效。
MINIO_ENDPOINT: localhost:9000: Minio 终端，仅当 STORAGE_TYPE 是 minio 时有效。
MINIO_ACCESS_KEY_ID: Minio accessKeyID ，仅当 STORAGE_TYPE 是 minio 时有效。
MINIO_SECRET_ACCESS_KEY: Minio secretAccessKey，仅当 STORAGE_TYPE 是 minio 时有效。
MINIO_BUCKET: gitea: Minio bucket to store the attachments，仅当 STORAGE_TYPE 是 minio 时有效。
MINIO_LOCATION: us-east-1: Minio location to create bucket，仅当 STORAGE_TYPE 是 minio 时有效。
MINIO_BASE_PATH: attachments/: Minio base path on the bucket，仅当 STORAGE_TYPE 是 minio 时有效。
MINIO_USE_SSL: false: Minio enabled ssl，仅当 STORAGE_TYPE 是 minio 时有效。
```
