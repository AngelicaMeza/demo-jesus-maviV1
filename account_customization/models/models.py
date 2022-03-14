# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def date_difference(self):
        return((self.invoice_date - self.invoice_date_due).days)
