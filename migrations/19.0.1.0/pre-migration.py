import logging
from odoo.upgrade import util
_logger = logging.getLogger(__name__)

def migrate(cr, version):

    cr.execute("""
        SELECT name, state
        FROM ir_module_module
        WHERE name IN (
            'account_payment_group',
            'l10n_ar_tax'
        )
    """)
    _logger.warning("Replacement modules: %s", cr.fetchall())
    cr.execute("""
        SELECT name, state
        FROM ir_module_module
        WHERE state IN ('to install', 'to upgrade')
        ORDER BY name
    """)
    _logger.warning("Pending modules: %s", cr.fetchall())
    cr.execute("""
        SELECT name, state, latest_version
        FROM ir_module_module
        WHERE name IN (
            'account-payment-group',
            'account_payment_group',
            'l10n_ar_account_withholding',
            'l10n_ar_withholding_ux',
            'l10n_ar_tax'
        )
        ORDER BY name
    """)
    _logger.warning("Migration module status: %s", cr.fetchall())

    _logger.warning(
        "Installing replacement modules"
    )

    util.force_install_module(
        cr,
        "account_payment_group",
    )

    util.force_install_module(
        cr,
        "l10n_ar_tax",
    )
    cr.execute("""
        SELECT name, state
        FROM ir_module_module
        WHERE name IN (
            'account_payment_group',
            'l10n_ar_tax'
        )
    """)
    _logger.warning(
        "Replacement modules after force install: %s",
        cr.fetchall()
    )
    cr.execute("""
        UPDATE ir_module_module
        SET state = 'uninstalled'
        WHERE name IN (
            'Acccount_taxes',
            'Res_partner',
            'account-payment-patch',
            'account_invoice_pricelist'
        )
    """)
    cr.execute("""
        UPDATE ir_module_module
        SET state = 'uninstalled'
        WHERE name IN (
            'account-payment-group',
            'l10n_ar_account_withholding',
            'l10n_ar_withholding_ux'
        )
    """)

    _logger.warning(
        "Marked legacy modules as uninstalled"
    )
    cr.execute("""
        DELETE FROM l10n_ar_payment_withholding
        WHERE payment_id IS NULL
        AND id IN (1928,2687,2688)
    """)

    _logger.warning(
        "Deleted %s orphan withholding records",
        cr.rowcount
    )
    cr.execute("""
        UPDATE sale_order
        SET x_studio_stockcliente = 'Cliente'
        WHERE x_studio_stockcliente IS NULL
    """)

    _logger.warning(
        "Fixed %s sale orders with NULL x_studio_stockcliente",
        cr.rowcount
    )
    #if util.module_installed(cr, "account_payment_group"):
    #    util.remove_module(cr, "account-payment-group")

    #if util.module_installed(cr, "l10n_ar_tax"):
    #    util.remove_module(cr, "l10n_ar_account_withholding")
    #    util.remove_module(cr, "l10n_ar_withholding_ux")