from odoo import models, fields, api

from odoo.exceptions import ValidationError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offers'
    _description = "Estate property offers"
    _order = "price desc"

    price = fields.Integer(string="Price")
    status = fields.Selection([('refuse', 'Refused'), ('accept', 'Accepted')], string="status")
    partner_ids = fields.Many2one("res.partner", "Partner")
    property_id = fields.Many2one("estate.property", "Estate")
    # property_type_id = fields.Char(related="property_id")
    validity = fields.Integer(string="Validity", default="7")
    date_deadline = fields.Date(string="Deadline")

    # add functionality to the selling and expected price
    @api.depends("status")
    def accept(self):
        estate_percentage = self.price / self.property_id.expected_price
        format_price = int('{:.0%}'.format(estate_percentage).rstrip("%"))
        MY__PERCENTAGE = int("{:.0%}".format(0.9).rstrip("%"))
        self.status = "accept"
        if self.status == "accept":
            self.property_id.state = "offer accepted"
            if format_price >= MY__PERCENTAGE:
                self.property_id.buyer_id = self.partner_ids
                self.property_id.price = self.price
                self.property_id.selling_price = self.price
            else:
                self.property_id.buyer_id = ''
                self.property_id.price = ''
                self.property_id.selling_price = ''
                raise ValidationError('''The Selling price must be at least 90% of the expected price. You must reduce
                the expected price if you want to accept this offer''')
        else:
            pass

    @api.depends("status")
    def refuse(self):
        self.status = "refuse"
        if self.status == 'refuse':
            pass

    @api.constrains("price")
    def is_positive(self):
        for record in self:
            if record.price < 0:
                raise ValidationError("Negative %s is not valid" % record.price)

    # When an offer is created, the state should switch to offer received
    @api.model
    def create(self, vals):
        # current_price = vals['price']
        all_price = []
        prop_offer = self.env['estate.property'].browse(vals['property_id'])
        for record in prop_offer:
            if record == record.price:
                all_price.append(record.price)
        if len(all_price) > 2:
            if all_price[-1] > all_price[-2]:
                prop_offer.state = 'offer received'
            elif all_price[-1] <= all_price[-2]:
                raise ValidationError(f"Offer must be greater than {all_price[-1]}")
            else:
                prop_offer.state = 'new'
                # print("Property Values", "Current price :", current_price, "state :", values.state, "prev price",  prev_price)
        else:
            pass

        return super(EstatePropertyOffer, self).create(vals)

