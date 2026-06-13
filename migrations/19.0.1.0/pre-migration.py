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
    if util.module_installed(cr, "account_payment_group"):
        util.remove_module(cr, "account-payment-group")

    if util.module_installed(cr, "l10n_ar_tax"):
        util.remove_module(cr, "l10n_ar_account_withholding")
        util.remove_module(cr, "l10n_ar_withholding_ux")