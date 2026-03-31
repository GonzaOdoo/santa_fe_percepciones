from odoo import api, fields, models

class SaleReport(models.Model):
    _inherit = 'account.payment'

    padron_warning = fields.Char(
        string="Advertencia Padrón",
        compute="_compute_padron_warning",
        store=False,
    )

    @api.depends('partner_id', 'date')
    def _compute_padron_warning(self):
        Padron = self.env['partner.tax.padron.santa_fe']
    
        for payment in self:
            payment.padron_warning = False
    
            if not payment.partner_id:
                continue
    
            date = payment.date or fields.Date.today()
    
            padron = Padron.search([
                ('partner_id', '=', payment.partner_id.id),
                ('vigencia_desde', '<=', date),
                ('vigencia_hasta', '>=', date),
            ], limit=1)
    
            if not padron:
                payment.padron_warning = (
                    f"No existe padrón vigente para el cliente. Por favor tener en cuenta al momento de calcular retenciones"
                    f"{payment.partner_id.display_name} en la fecha {date}."
                )