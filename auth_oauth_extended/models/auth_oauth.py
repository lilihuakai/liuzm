from openerp import fields,models

class auth_oauth_provider(models.Model):
    _inherit = 'auth.oauth.provider'

    provider_type = [
        ('qq', 'for QQ'),
        ('weixin', 'for Weixin'),
        ('weibo', 'for Weibo'),
        ('other', 'for Other'),

    ]

    provider_type = fields.Selection(provider_type, 'Provider Type', required=True)

    _defaults = {
        'provider_type': 'other',
    }