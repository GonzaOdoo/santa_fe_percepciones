import logging
from odoo.upgrade import util
_logger = logging.getLogger(__name__)

def migrate(cr, version):

    cr.execute("""
        SELECT name, state
        FROM ir_module_module
        WHERE name IN (
            'account-payment-group',
            'account-payment-patch',
            'l10n_ar_account_withholding',
            'l10n_ar_withholding_ux',
            'account_invoice_pricelist',
            'Acccount_taxes',
            'Res_partner'
        )
        ORDER BY name
    """)
    _logger.warning(
        "Module states before fix: %s",
        cr.fetchall()
    )

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

    _logger.warning(
        "Modules changed from 'to upgrade' to 'installed': %s",
        cr.rowcount
    )

    cr.execute("""
        SELECT name, state
        FROM ir_module_module
        WHERE name IN (
            'account-payment-group',
            'account-payment-patch',
            'l10n_ar_account_withholding',
            'l10n_ar_withholding_ux',
            'account_invoice_pricelist',
            'Acccount_taxes',
            'Res_partner'
        )
        ORDER BY name
    """)
    _logger.warning(
        "Module states after fix: %s",
        cr.fetchall()
    )