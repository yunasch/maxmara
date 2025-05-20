from odoo import models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_attach_file(self):
        """
        Acción para adjuntar un archivo al producto.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': _('Adjuntar Archivo'),
            'res_model': 'ir.attachment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'product.template',
            }
        }