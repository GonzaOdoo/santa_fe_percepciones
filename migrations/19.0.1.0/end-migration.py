import logging
from odoo.upgrade import util
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    _logger.info('Starting post-migration script for Padron de Impuestos Santa Fe')
    _logger.info('Checking if module santa_fe_percepciones is installed')
    _logger.info( util.module_installed(cr, 'santa_fe_percepciones'))
    _logger.info('Checking if module account-payment-group is installed')
    _logger.info(util.module_installed(cr, 'account-payment-group'))
    _logger.info("Renaming module account-payment-group to account_payment_group")
    #util.rename_module(cr, 'account-payment-group', 'account_payment_group')
    _logger.info('Uninstalling module santa_fe_percepciones')
    util.uninstall_module(cr,'santa_fe_percepciones')
    