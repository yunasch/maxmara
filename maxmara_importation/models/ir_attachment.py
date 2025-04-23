from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import pandas as pd
from io import BytesIO

class IrAttachmentWizard(models.TransientModel):
    _name = 'ir.attachment.wizard'
    _description = 'Wizard para adjuntar archivos'

    filename = fields.Char('Nombre del Archivo')
    attachment = fields.Binary('Archivo', required=True, filename="filename")

    def action_upload_file(self):
        """ Método principal que procesa el archivo subido """
        df = self._read_excel_file()
        grouped = df.groupby(['STYLE CODE', 'NAME'])

        for (style_code, name), group in grouped:
            self._process_product_group(style_code, name, group)

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def _read_excel_file(self):
        """ Lee y convierte el archivo Excel o CSV a un DataFrame de pandas """
        if not self.attachment:
            raise UserError(_('Debe seleccionar un archivo para cargar.'))

        file_content = base64.b64decode(self.attachment)
        excel_file = BytesIO(file_content)

        try:
            if self.filename and self.filename.lower().endswith('.xls'):
                df = pd.read_excel(excel_file, sheet_name=0, engine=None, header=1) # Se lee a partir de la fila 1
            else:
                excel_file.seek(0)
                df = pd.read_csv(excel_file, header=1) # Se lee a partir de la fila 1
        except Exception as e:
            raise UserError(_('Error al leer el archivo: %s') % e)

        return df

    def _process_product_group(self, style_code, name, group):
        """ Procesa un grupo de lineas con el mismo STYLE CODE y NAME """
        category = self._get_or_create_category(group)
        price = float(group.iloc[0].get('PRICE', 0))

        template = self._get_or_create_template(name, style_code, price, category.id)

        colors, sizes = self._extract_attributes(group)
        self._assign_attributes_to_template(template, colors, sizes)
        self._assign_variants_data(template, group)

    def _get_or_create_category(self, group):
        """ Crea o asigna la categorii del producto """
        categ_name = str(group.iloc[0]['CLASS']).strip() if 'CLASS' in group.columns else 'General'
        category = self.env['product.category'].search([('name', 'ilike', categ_name)], limit=1)
        if not category:
            category = self.env['product.category'].create({'name': categ_name})
        return category

    def _get_or_create_template(self, name, style_code, price, categ_id):
        """ Crea o asigna el product template """
        template = self.env['product.template'].search([
            ('name', '=', name),
            ('default_code', '=', style_code)
        ], limit=1)
        if not template:
            template = self.env['product.template'].create({
                'name': name,
                'default_code': style_code,
                'list_price': price,
                'detailed_type': 'product',
                'categ_id': categ_id,
                'available_in_pos': True
            })
        return template

    def _extract_attributes(self, group):
        """ Extrae todos los valores únicos de COLOR y SIZE """
        colors = []
        sizes = []
        for _, row in group.iterrows():
            color = str(row['COLOR']).strip()
            size = str(row['SIZE']).strip()
            if color and color not in colors:
                colors.append(color)
            if size and size not in sizes:
                sizes.append(size)
        return colors, sizes

    def _get_or_create_attribute_value(self, attr_name, value_name):
        """ Recupera o crea un atributo y su valor """
        attr = self.env['product.attribute'].search([('name', '=', attr_name)], limit=1)
        if not attr:
            attr = self.env['product.attribute'].create({'name': attr_name})
        val = self.env['product.attribute.value'].search([
            ('name', '=', value_name), ('attribute_id', '=', attr.id)
        ], limit=1)
        if not val:
            val = self.env['product.attribute.value'].create({
                'name': value_name,
                'attribute_id': attr.id
            })
        return attr, val

    def _assign_attributes_to_template(self, template, colors, sizes):
        """ Asigna los atributos de color y talla al product.template """
        attr_lines = []
        existing_attr_names = template.attribute_line_ids.mapped('attribute_id.name')

        # COLOR
        if 'COLOR' not in existing_attr_names:
            attr_color, _ = self._get_or_create_attribute_value('COLOR', colors[0])
            val_color_ids = [self._get_or_create_attribute_value('COLOR', c)[1].id for c in colors]
            attr_lines.append((0, 0, {
                'attribute_id': attr_color.id,
                'value_ids': [(6, 0, val_color_ids)]
            }))
        else:
            attr_color = self.env['product.attribute'].search([('name', '=', 'COLOR')], limit=1)
            line = template.attribute_line_ids.filtered(lambda l: l.attribute_id.id == attr_color.id)
            if line:
                existing_ids = line.value_ids.ids
                new_ids = [self._get_or_create_attribute_value('COLOR', c)[1].id for c in colors if
                           self._get_or_create_attribute_value('COLOR', c)[1].id not in existing_ids]
                line.value_ids = [(6, 0, existing_ids + new_ids)]

        # SIZE
        attr_size = self.env['product.attribute'].search([('name', '=', 'SIZE')], limit=1)
        if not attr_size:
            attr_size = self.env['product.attribute'].create({'name': 'SIZE'})

        val_size_ids = [self._get_or_create_attribute_value('SIZE', s)[1].id for s in sizes]
        line = template.attribute_line_ids.filtered(lambda l: l.attribute_id.id == attr_size.id)
        if line:
            existing_ids = line.value_ids.ids
            new_ids = [i for i in val_size_ids if i not in existing_ids]
            line.value_ids = [(6, 0, existing_ids + new_ids)]
        else:
            attr_lines.append((0, 0, {
                'attribute_id': attr_size.id,
                'value_ids': [(6, 0, val_size_ids)]
            }))

        if attr_lines:
            template.write({'attribute_line_ids': attr_lines})
            # template._create_variant_ids()  # Forzar regeneración de variantes

    def _assign_variants_data(self, template, group):
        """ Asigna Style Code y SKU a cada variante según COLOR y SIZE o al producto en su defecto """
        for _, row in group.iterrows():
            size = str(row['SIZE']).strip()
            color = str(row['COLOR']).strip()
            style_code = str(row['STYLE CODE']).strip()
            sku = str(row['SKU']).strip()

            variant = self.env['product.product'].search([
                ('product_tmpl_id', '=', template.id),
                ('product_template_attribute_value_ids.attribute_id.name', '=', 'SIZE'),
                ('product_template_attribute_value_ids.name', '=', size),
                ('product_template_attribute_value_ids.attribute_id.name', '=', 'COLOR'),
                ('product_template_attribute_value_ids.name', '=', color),
            ], limit=1)

            if variant:
                variant.default_code = style_code
                variant.barcode = sku




