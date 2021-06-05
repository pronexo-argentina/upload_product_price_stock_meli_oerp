# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import csv
from datetime import date, datetime
from datetime import timedelta
import pytz
from pytz import timezone
import logging
import sys

_logger = logging.getLogger(__name__)

class ProductUploadPrices(models.Model):
    _name = 'product.upload_meli_oerp.prices'
    _description = 'product.upload_meli_oerp.prices'


    def btn_process(self):
        self.ensure_one()
      
        if not self.delimiter:
            raise ValidationError('Debe ingresar el delimitador')
        if not self.product_file:
            raise ValidationError('Debe seleccionar el archivo')
        if self.state != 'draft':
            raise ValidationError('Archivo procesado!')
        self.file_content = base64.b64decode(self.product_file)
        
        lines = self.file_content.split('\n')
        for line in lines:
            lista = line.split(self.delimiter)
            if len(lista) == 6:
                default_code = lista[0].replace("\"","")
                meli_price = lista[2].replace("\"","")
                meli_available_quantity = lista[3].replace("\"","")
                product_product = self.env['product.product'].search([('default_code','=',default_code)])
                product_template = self.env['product.template'].search([('default_code','=',default_code)])
                if product_product:
                    product_product.meli_price = meli_price
                    product_product.meli_available_quantity = meli_available_quantity
                    product_template.meli_price = meli_price
                else:
                    not_processed_content = self.not_processed_content or '' + line or '' + '\n'
                    self.not_processed_content = not_processed_content
            else:
                not_processed_content = self.not_processed_content or '' + line or '' + '\n'
                self.not_processed_content = not_processed_content

        self.state = 'processed'


    name = fields.Datetime(string="Fecha Hora",  default=lambda *a: datetime.now())
    userid = fields.Char("Usuario",default=lambda self: self.env.user.name)
    product_file = fields.Binary('Archivo')
    delimiter = fields.Char('Delimitador',default=";")
    state = fields.Selection(selection=[('draft','Borrador'),('processed','Procesado')],string='Estado',default='draft')
    file_content = fields.Text('Texto archivo')
    not_processed_content = fields.Text('Texto no procesado')
