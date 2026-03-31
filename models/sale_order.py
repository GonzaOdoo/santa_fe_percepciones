from collections import defaultdict
from datetime import timedelta
from markupsafe import Markup
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)
class SaleReport(models.Model):
    _inherit = 'sale.order'

    checkbox_cliente_final = fields.Boolean(string='Usar cliente final')
    cliente_final_usar = fields.Char(string='Cliente Final')
    padron_warning = fields.Char(
        string="Advertencia Padrón",
        compute="_compute_padron_warning",
        store = False,
    )

    @api.depends('partner_id', 'date_order', 'fiscal_position_id')
    def _compute_padron_warning(self):
        Padron = self.env['partner.tax.padron.santa_fe']
    
        for order in self:
            order.padron_warning = False
    
            # Validaciones base
            if not order.partner_id or not order.fiscal_position_id:
                continue
    
            if not order.fiscal_position_id.dynamic_padron:
                continue
    
            # Solo si realmente usa padrón
            if not order.fiscal_position_id.tax_ids.filtered(lambda l: l.use_padron):
                continue
    
            date = order.date_order or fields.Date.today()
    
            padron = Padron.search([
                ('partner_id', '=', order.partner_id.id),
                ('vigencia_desde', '<=', date),
                ('vigencia_hasta', '>=', date),
            ], limit=1)
            if not padron:
                order.padron_warning = (
                    f"No existe padrón vigente para el cliente "
                    f"{order.partner_id.display_name} en la fecha {date}."
                )
            if padron:
                alicuota = padron.alic_percepcion
                tax = self.env['account.tax'].search([
                    ('type_tax_use', '=', 'sale'),
                    ('amount', '=', alicuota),
                    ('company_id', '=', order.company_id.id),
                ], limit=1)
            
                if not tax:
                    order.padron_warning = (
                        f"No existe impuesto configurado con alícuota {alicuota}% "
                        f"para el cliente {order.partner_id.display_name}."
                    )
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def _get_custom_compute_tax_cache_key(self):
        self.ensure_one()

        partner = self.order_id.partner_id
        date = self.order_id.date_order

        return (
            partner.id,
            fields.Date.to_string(date) if date else None,
        )

    def _compute_tax_id(self):
        lines_by_company = defaultdict(lambda: self.env['sale.order.line'])
        cached_taxes = {}

        for line in self:
            lines_by_company[line.company_id] += line

        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = None
                if line.product_id:
                    taxes = line.product_id.taxes_id._filter_taxes_by_company(company)

                if not line.product_id or not taxes:
                    line.tax_id = False
                    continue

                fiscal_position = line.order_id.fiscal_position_id

                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                cache_key += line._get_custom_compute_tax_cache_key()

                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.with_context(
                        partner_id=line.order_id.partner_id.id,
                        date=line.order_id.date_order,
                    ).map_tax(taxes)

                    cached_taxes[cache_key] = result

                line.tax_id = result

