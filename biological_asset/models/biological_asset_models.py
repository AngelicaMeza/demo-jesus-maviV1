# -*- coding: utf-8 -*-

import calendar
from dateutil.relativedelta import relativedelta
from math import copysign

from odoo import api, fields, models, _
import odoo
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    is_biological = fields.Boolean(default=False)
    method = fields.Selection([
        ('linear', 'Linear'),
        ('degressive', 'Degressive'),
        ('degressive_then_linear', 'Accelerated Degressive'),
        ('bio', 'Biological')], string='Method', readonly=True, states={'draft': [('readonly', False)], 'model': [('readonly', False)]}, default = 'linear',
        help="Choose the method to use to compute the amount of depreciation lines.\n"
        "  * Linear: Calculated on basis of: Gross Value / Number of Depreciations\n"
        "  * Degressive: Calculated on basis of: Residual Value * Degressive Factor\n"
        "  * Accelerated Degressive: Like Degressive but with a minimum depreciation value equal to the linear value.\n"
        "  * Biological: ")

    @api.model_create_multi
    def create(self, vals_list):
        assets = super().create(vals_list)
        if self._context.get('is_biological', False):
            for rec in assets:
                rec.is_biological = True
        return assets

    species_id = fields.Many2one('account.asset.species', string='Species')

    data_ids = fields.One2many('account.asset.data', 'asset_id')

    # Pruebas porcentajes
    def _recompute_board(self, depreciation_number, starting_sequence, amount_to_depreciate, depreciation_date, already_depreciated_amount, amount_change_ids):
        self.ensure_one()
        residual_amount = amount_to_depreciate
        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        move_vals = []
        print("#"*50)
        print(self.data_ids)
        print("#"*50)
        prorata = self.prorata and not self.env.context.get("ignore_prorata")
        if amount_to_depreciate != 0.0:
            for asset_sequence in range(starting_sequence + 1, depreciation_number + 1):
                while amount_change_ids and amount_change_ids[0].date <= depreciation_date:
                    if not amount_change_ids[0].reversal_move_id:
                        residual_amount -= amount_change_ids[0].amount_total
                        amount_to_depreciate -= amount_change_ids[0].amount_total
                        already_depreciated_amount += amount_change_ids[0].amount_total
                    amount_change_ids[0].write({
                        'asset_remaining_value': float_round(residual_amount, precision_rounding=self.currency_id.rounding),
                        'asset_depreciated_value': amount_to_depreciate - residual_amount + already_depreciated_amount,
                    })
                    amount_change_ids -= amount_change_ids[0]
                if self.data_ids:
                    amount = self._compute_board_amount(asset_sequence, residual_amount, amount_to_depreciate, depreciation_number,starting_sequence, depreciation_date, self.data_ids[asset_sequence-1].monthly_depreciation_pct)
                else:
                    amount = self._compute_board_amount(asset_sequence, residual_amount, amount_to_depreciate, depreciation_number,starting_sequence, depreciation_date, 0)
                prorata_factor = 1
                move_ref = self.name + \
                    ' (%s/%s)' % (prorata and asset_sequence -
                                  1 or asset_sequence, self.method_number)
                if prorata and asset_sequence == 1:
                    move_ref = self.name + ' ' + _('(prorata entry)')
                    first_date = self.prorata_date
                    if int(self.method_period) % 12 != 0:
                        month_days = calendar.monthrange(
                            first_date.year, first_date.month)[1]
                        days = month_days - first_date.day + 1
                        prorata_factor = days / month_days
                    else:
                        total_days = (depreciation_date.year %
                                      4) and 365 or 366
                        days = (self.company_id.compute_fiscalyear_dates(
                            first_date)['date_to'] - first_date).days + 1
                        prorata_factor = days / total_days
                amount = self.currency_id.round(amount * prorata_factor)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount

                move_vals.append(self.env['account.move']._prepare_move_for_asset_depreciation({
                    'amount': amount,
                    'asset_id': self,
                    'move_ref': move_ref,
                    'date': depreciation_date,
                    'asset_remaining_value': float_round(residual_amount, precision_rounding=self.currency_id.rounding),
                    'asset_depreciated_value': amount_to_depreciate - residual_amount + already_depreciated_amount,
                }))

                depreciation_date = depreciation_date + \
                    relativedelta(months=+int(self.method_period))
                # datetime doesn't take into account that the number of days is not the same for each month
                if int(self.method_period) % 12 != 0:
                    max_day_in_month = calendar.monthrange(
                        depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(
                        day=max_day_in_month)
        return move_vals

    def _compute_board_amount(self, computation_sequence, residual_amount, total_amount_to_depr, max_depreciation_nb, starting_sequence, depreciation_date, bio_percent):
        amount = 0
        if computation_sequence == max_depreciation_nb:
            # last depreciation always takes the asset residual amount
            amount = residual_amount
        else:
            if self.method in ('degressive', 'degressive_then_linear'):
                amount = residual_amount * self.method_progress_factor
            if self.method in ('linear', 'degressive_then_linear'):
                nb_depreciation = max_depreciation_nb - starting_sequence
                if self.prorata:
                    nb_depreciation -= 1
                linear_amount = min(total_amount_to_depr /
                                    nb_depreciation, residual_amount)
                if self.method == 'degressive_then_linear':
                    amount = max(linear_amount, amount)
                else:
                    amount = linear_amount
            if self.method == 'bio':
                amount = residual_amount * bio_percent / 100
        return amount

    # Pruebas porcentajes

    @api.onchange('species_id')
    def species_onchange(self):
        if self._context.get('default_state') == 'model':
            # self.data_ids = None
            lista = list()
            for rec in self.species_id.data_ids:
                line = self.env['account.asset.data'].create({
                    'period': rec.period,
                    'monthly_depreciation_pct': rec.monthly_depreciation_pct,
                    'asset_id': self.id
                })
                lista.append(line.id)
            self.data_ids = lista
            self.method_number = len(lista)
            self.method_period = "1"

    @api.onchange('model_id')
    def model_onchange(self):
        if self.method == 'bio' and self.state != 'model':
            self.species_id = self.model_id.species_id
            self.method_number = len(self.model_id.data_ids)

            lista = list()
            for rec in self.model_id.data_ids:
                line = self.env['account.asset.data'].create({
                    'period': rec.period,
                    'monthly_depreciation_pct': rec.monthly_depreciation_pct,
                    'asset_id': self.id
                })
                lista.append(line.id)
            self.data_ids = lista

    @api.onchange('data_ids')
    def data_onchange(self):
        self.method_number = len(self.data_ids)
        cont = 0

        for rec in self.data_ids:
            cont += rec.monthly_depreciation_pct
        if(round(cont) > 100):
            raise UserError(
                _("The sum of the monthly depreciation values({}) cannot be greater than 100".format(cont)))
    
    @api.onchange('method')
    def method_onchange(self):
        if self.method == 'bio':
            self.is_biological = True

            return {'domain':{'model_id':[('method','=','bio'), ('state', '=', 'model')]}}
        else:
            return {'domain':{'model_id':[('method','!=','bio'), ('state', '=', 'model')]}}


class AccountAssetSpecies(models.Model):
    _name = 'account.asset.species'
    _description = 'Account Asset Species'

    name = fields.Char(string='Race Name')
    data_ids = fields.One2many('account.asset.data', 'name_id')


class AccountAssetData(models.Model):
    _name = 'account.asset.data'
    _description = 'Account Asset Data'

    period = fields.Integer(string='Period', default=lambda self: self.env['ir.sequence'].next_by_code('autoincrement_period'))
    monthly_depreciation_pct = fields.Float(string='Monthly Depreciation Porcentage')
    name_id = fields.Many2one('account.asset.species', string='Species Name')
    asset_id = fields.Many2one('account.asset', string='Asset ID')

