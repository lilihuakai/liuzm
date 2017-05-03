# -*- coding: utf-8 -*-
from openerp import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class distribution(models.Model):
    _name='website_myaccount_base.distribution.faq'
    faq_question= fields.Char(string="Question", required=True)
    faq_anwser = fields.Text(string="Anwser")

