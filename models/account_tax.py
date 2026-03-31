from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)
class AccountTax(models.Model):
    _inherit = "account.tax"

    amount_type = fields.Selection(
        selection_add=([
            ('partner_tax_santafe', 'Alícuota en el Partner (Santa Fe)'),
        ]), ondelete={'partner_tax_santafe': 'set default'}
    )
    withholding_type = fields.Selection(
        selection_add=([
            ('partner_tax_santafe', 'Alícuota en el Partner (Santa Fe)'),
        ]), ondelete={'partner_tax_santafe': 'set default'}
    )


    def get_withholding_vals(self, payment):
        self.ensure_one()
        if self.withholding_type != 'partner_tax_santafe':
            return super().get_withholding_vals(payment)
    
        commercial_partner = payment.partner_id.commercial_partner_id
        date = payment.date or fields.Date.context_today(self)
    
        # Buscar padrón vigente
        padron = self.env['partner.tax.padron.santa_fe'].search([
            ('partner_id', '=', commercial_partner.id),
            ('vigencia_desde', '<=', date),
            ('vigencia_hasta', '>=', date),
        ], limit=1)
    
        vals = super().get_withholding_vals(payment)
        base_amount = vals['withholdable_base_amount']
    
        if not padron:
            amount = 0.0
            vals['comment'] = "Sin padrón vigente (Santa Fe)"
        else:
            alicuota = padron.alic_retencion  # ya viene en %
            amount = base_amount * (alicuota / 100.0)
    
            vals['comment'] = "%s x %s%% (SF)" % (
                base_amount,
                alicuota,
            )
    
        vals['period_withholding_amount'] = amount
    
        return vals