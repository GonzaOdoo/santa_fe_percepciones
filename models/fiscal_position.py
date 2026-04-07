# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta
from markupsafe import Markup
from odoo import models, fields, api
import logging
from odoo.exceptions import UserError,ValidationError

_logger = logging.getLogger(__name__)
class AccountFiscalPositionTax(models.Model):
    _inherit = 'account.fiscal.position.tax'

    use_padron = fields.Boolean(
        string='Usar padrón dinámico'
    )

    padron_type = fields.Selection([
        ('percepcion', 'Percepción'),
        ('retencion', 'Retención'),
    ], string='Tipo padrón')


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    dynamic_padron = fields.Boolean("Usa padrón dinámico")

    def map_tax(self, taxes):
        if not self:
            return taxes
        if not self.dynamic_padron:
            return super().map_tax(taxes)
    
        result = self.env['account.tax']
    
        partner_id = self.env.context.get('partner_id')
        date = self.env.context.get('date') or fields.Date.today()

        padron = False
        if partner_id:
            padron = self.env['partner.tax.padron.santa_fe'].search([
                ('partner_id', '=', partner_id),
                ('vigencia_desde', '<=', date),
                ('vigencia_hasta', '>=', date),
            ], limit=1)
    
        for tax in taxes:
            # Buscar mapping line correspondiente
            mapping_line = self.tax_ids.filtered(
                lambda l: l.tax_src_id == tax
            )[:1]
    
            # Si no hay mapping → comportamiento normal
            if not mapping_line:
                result |= tax
                continue
    
            # Si NO usa padrón → usar mapping estándar
            if not mapping_line.use_padron:
                result |= mapping_line.tax_dest_id or tax
                continue
            else:
                # Si usa padrón pero no hay datos → fallback
                if not padron:
                    result |= tax
                    #raise ValidationError('No se encontró un padrón válido en el periodo dado en el cliente')
                    continue
        
                # 🔥 Acá aplicás padrón SOLO a este impuesto
                dynamic_tax = self._get_tax_from_padron(padron)
        
                result |= dynamic_tax or tax
        
        return result

    def _get_tax_from_padron(self, padron):
        self.ensure_one()
    
        alicuota = padron.alic_percepcion
    
        tax = self.env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('amount', '=', alicuota),
            #('x_padron_tax', '=', True),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        if not tax:
            raise ValidationError(f'No se encontró un impuesto con la alicuota {alicuota}, por favor proceda a la creación del mismo para poder continuar')

        _logger.info(tax)
        return tax
