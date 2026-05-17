import logging
from odoo.upgrade import util
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    if not version:
        return
    _logger.info( util.module_installed(cr, 'santa_fe_percepciones'))
    _logger.info(util.module_installed(cr, 'account-payment-group'))
    
    _logger.info('Uninstalling module santa_fe_percepciones')
    util.uninstall_module(cr,'santa_fe_percepciones')
    