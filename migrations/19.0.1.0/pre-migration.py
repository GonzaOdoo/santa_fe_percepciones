import logging
from odoo.upgrade import util
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_module_module
           SET state = 'installed'
         WHERE name IN (
             'account-payment-group',
             'account-payment-patch',
             'l10n_ar_account_withholding',
             'l10n_ar_withholding_ux',
             'account_invoice_pricelist',
             'Acccount_taxes',
             'Res_partner'
         )
           AND state = 'to upgrade'
    """)

    _logger.warning("Forced legacy modules from 'to upgrade' to 'installed'")
    cr.execute("""
        UPDATE l10n_latam_check
           SET payment_date = create_date::date
         WHERE id = 1400
           AND payment_date IS NULL
    """)
    _logger.warning("Set payment_date to create_date for l10n_latam_check with id 1400")