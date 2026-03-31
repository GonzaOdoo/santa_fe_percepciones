from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import csv
import zipfile
from io import BytesIO, StringIO
from datetime import datetime
import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)

class PadronSantaFeImportWizard(models.Model):
    _name = 'padron.santa.fe.import.wizard'
    _description = 'Importar Padrón Santa Fe'

    name = fields.Char('Periodo')
    file = fields.Binary(string='Archivo CSV', required=True)
    filename = fields.Char(string='Nombre Archivo')
    line_ids = fields.One2many(
        'partner.tax.padron.santa_fe',
        'import_id',
        string='Registros generados'
    )

    result_line_ids = fields.One2many(
        'padron.santa.fe.import.result',
        'wizard_id',
        string='Resultados'
    )

    def _parse_date(self, value):
        """Convierte fechas tipo 21022026 → 2026-02-21"""
        if not value:
            return False

        value = value.strip()

        # completar con ceros si viene tipo 1032026
        if len(value) == 7:
            value = '0' + value

        try:
            return datetime.strptime(value, '%d%m%Y').date()
        except Exception:
            return False

    def _normalize_cuit(self, cuit):
        return ''.join(filter(str.isdigit, cuit or ''))

    def _parse_float(self, value):
        if not value:
            return 0.0
        value = value.strip().replace(',', '.')
        try:
            return float(value)
        except:
            return 0.0

    def action_import(self):
        _logger.info("Importando padrón Santa Fe")
        self.ensure_one()
    
        if not self.file:
            raise UserError("Debe cargar un archivo.")
    
        file_bytes = base64.b64decode(self.file)
    
        # Obtener contenido
        if self.filename and self.filename.lower().endswith('.zip'):
            zip_file = zipfile.ZipFile(BytesIO(file_bytes))
    
            csv_filename = next(
                (name for name in zip_file.namelist() if name.lower().endswith('.csv')),
                None
            )
    
            if not csv_filename:
                raise UserError("El ZIP no contiene ningún archivo CSV.")
    
            with zip_file.open(csv_filename) as f:
                content = f.read().decode('utf-8', errors='ignore')
        else:
            content = file_bytes.decode('utf-8', errors='ignore')
    
        file_data = StringIO(content)
    
        # Columnas fijas del padrón
        columns = [
            'F.PUBLIC',
            'F.VIGEN.DESDE',
            'F.VIGEN.HASTA',
            'NRO.CUIT',
            'TIPO CONTRIB',
            'MARCA ALTA',
            'MARCA ALICUOTA',
            'ALIC.PERCEP',
            'ALICUOTA RETENC',
            'GRUPO PER.',
            'GRUPO RETEN',
            'RAZON SOCIAL',
        ]
    
        reader = csv.reader(file_data, delimiter=';')
    
        Partner = self.env['res.partner']
        Padron = self.env['partner.tax.padron.santa_fe']
    
        # 🔥 Optimización: indexar partners por CUIT
        partners_map = defaultdict(list)
        for p in Partner.search([('l10n_ar_vat', '!=', False)]):
            partners_map[p.l10n_ar_vat].append(p.id)
    
        for i, row in enumerate(reader, start=1):
            # Evitar filas vacías o mal formadas
            if not row or len(row) < 4:
                continue
    
            # Convertir a dict
            row_dict = dict(zip(columns, row))
    
            _logger.info(row_dict)
    
            cuit = self._normalize_cuit(row_dict.get('NRO.CUIT'))
            partner_ids = partners_map.get(cuit, [])
    
            if not partner_ids:
                continue
    
            desde = self._parse_date(row_dict.get('F.VIGEN.DESDE'))
            hasta = self._parse_date(row_dict.get('F.VIGEN.HASTA'))
    
            for partner_id in partner_ids:
                existing = Padron.search([
                    ('partner_id', '=', partner_id),
                    ('vigencia_desde', '=', desde),
                    ('vigencia_hasta', '=', hasta),
                ], limit=1)
    
                if existing:
                    continue
    
                Padron.create({
                    'partner_id': partner_id,
                    'import_id': self.id,
                    'cuit': cuit,
                    'fecha_publicacion': self._parse_date(row_dict.get('F.PUBLIC')),
                    'vigencia_desde': desde,
                    'vigencia_hasta': hasta,
                    'tipo_contribuyente': row_dict.get('TIPO CONTRIB'),
                    'marca_alta': row_dict.get('MARCA ALTA'),
                    'marca_alicuota': row_dict.get('MARCA ALICUOTA'),
                    'alic_percepcion': self._parse_float(row_dict.get('ALIC.PERCEP')),
                    'alic_retencion': self._parse_float(row_dict.get('ALICUOTA RETENC')),
                    'grupo_percepcion': row_dict.get('GRUPO PER.'),
                    'grupo_retencion': row_dict.get('GRUPO RETEN'),
                    'razon_social': (row_dict.get('RAZON SOCIAL') or '').strip(),
                })


    def _get_csv_content(self):
        file_bytes = base64.b64decode(self.file)
    
        if self.filename and self.filename.lower().endswith('.zip'):
            zip_file = zipfile.ZipFile(BytesIO(file_bytes))
            csv_filename = next(
                (name for name in zip_file.namelist() if name.lower().endswith('.csv')),
                None
            )
            if not csv_filename:
                raise UserError("El ZIP no contiene CSV")
    
            with zip_file.open(csv_filename) as f:
                return f.read().decode('utf-8', errors='ignore')
        else:
            return file_bytes.decode('utf-8', errors='ignore')

    def _process_row(self, row):
        Partner = self.env['res.partner']
        Padron = self.env['partner.tax.padron.santa_fe']
    
        cuit = self._normalize_cuit(row.get('NRO.CUIT'))
        partner = Partner.search([('vat', '=', cuit)], limit=1)
    
        estado = 'no_encontrado'
    
        if partner:
            desde = self._parse_date(row.get('F.VIGEN.DESDE'))
            hasta = self._parse_date(row.get('F.VIGEN.HASTA'))
    
            existing = Padron.search([
                ('partner_id', '=', partner.id),
                ('vigencia_desde', '=', desde),
                ('vigencia_hasta', '=', hasta),
            ], limit=1)
    
            if not existing:
                Padron.create({...})
                estado = 'creado'
            else:
                estado = 'duplicado'
    
        self.env['padron.santa.fe.import.result'].create({
            'wizard_id': self.id,
            'cuit': cuit,
            'partner_id': partner.id if partner else False,
            'estado': estado,
        })


class PadronSantaFeImportResult(models.Model):
    _name = 'padron.santa.fe.import.result'
    _description = 'Resultado Importación'

    wizard_id = fields.Many2one('padron.santa.fe.import.wizard')

    cuit = fields.Char(string='CUIT')
    partner_id = fields.Many2one('res.partner', string='Contacto')

    estado = fields.Selection([
        ('creado', 'Creado'),
        ('duplicado', 'Duplicado'),
        ('no_encontrado', 'No encontrado'),
    ], string='Estado')
    
    mensaje = fields.Char(string='Mensaje')


class PadronSantaFeImportBatch(models.Model):
    _name = 'padron.santa.fe.import.batch'

    wizard_id = fields.Many2one('padron.santa.fe.import.wizard')
    offset = fields.Integer()
    limit = fields.Integer(default=100000)
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('done', 'Hecho'),
        ('error', 'Error'),
    ], default='pending')

    log = fields.Text()


    def action_process_batch(self):
        self.ensure_one()
        self.state = 'processing'
    
        wizard = self.wizard_id
        content = wizard._get_csv_content()
    
        file_data = StringIO(content)
        reader = csv.DictReader(file_data, delimiter=';')
    
        for i, row in enumerate(reader):
            if i < self.offset:
                continue
            if i >= self.offset + self.limit:
                break
    
            wizard._process_row(row)
    
        self.state = 'done'