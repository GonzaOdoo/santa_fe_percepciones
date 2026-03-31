from odoo import models, fields, api

class PartnerTaxPadron(models.Model):
    _name = 'partner.tax.padron.santa_fe'
    _description = 'Padron Impositivo por Contacto'
    _order = 'vigencia_desde desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade',
        index=True
    )

    cuit = fields.Char(string='CUIT', required=True, index=True)

    fecha_publicacion = fields.Date(string='Fecha Publicación')
    vigencia_desde = fields.Date(string='Vigencia Desde', required=True)
    vigencia_hasta = fields.Date(string='Vigencia Hasta', required=True)

    tipo_contribuyente = fields.Char(string='Tipo Contribuyente')
    marca_alta = fields.Char(string='Marca Alta')
    marca_alicuota = fields.Char(string='Marca Alicuota')

    alic_percepcion = fields.Float(string='Alic. Percepción')
    alic_retencion = fields.Float(string='Alic. Retención')

    grupo_percepcion = fields.Char(string='Grupo Percepción')
    grupo_retencion = fields.Char(string='Grupo Retención')

    razon_social = fields.Char(string='Razón Social')
    import_id = fields.Many2one(
        'padron.santa.fe.import.wizard',
        string='Importación',
        ondelete='set null'
    )
    _sql_constraints = [
    (
        'unique_partner_period',
        'unique(partner_id, vigencia_desde, vigencia_hasta)',
        'Ya existe un registro para este contacto en ese período.'
    )
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tax_padron_ids = fields.One2many(
        'partner.tax.padron.santa_fe',
        'partner_id',
        string='Histórico Padron',
        order='vigencia_desde desc'
    )