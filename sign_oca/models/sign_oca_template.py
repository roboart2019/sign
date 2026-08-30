# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SignOcaTemplate(models.Model):
    _name = "sign.oca.template"
    _description = "Sign Oca Template"  # TODO
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    data = fields.Binary(attachment=True, required=True)
    ask_location = fields.Boolean()
    filename = fields.Char()
    item_ids = fields.One2many("sign.oca.template.item", inverse_name="template_id")
    request_count = fields.Integer(compute="_compute_request_count")
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        domain=[("transient", "=", False), ("model", "not like", "sign.oca")],
    )
    model = fields.Char(
        compute="_compute_model", string="Model name", compute_sudo=True, store=True
    )
    active = fields.Boolean(default=True)
    request_ids = fields.One2many("sign.oca.request", inverse_name="template_id")

    @api.depends("model_id")
    def _compute_model(self):
        for item in self:
            item.model = item.model_id.model or False

    @api.depends("request_ids")
    def _compute_request_count(self):
        groups = self.env["sign.oca.request"]._read_group(
            domain=[("template_id", "in", self.ids)],
            groupby=["template_id"],
            aggregates=["__count"],
        )
        res_dict = {template.id: count for template, count in groups}
        for record in self:
            record.request_count = res_dict.get(record.id, 0)

    def configure(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "sign_oca_configure",
            "name": self.name,
            "params": {
                "res_model": self._name,
                "res_id": self.id,
            },
        }

    def get_info(self):
        self.ensure_one()
        return {
            "name": self.name,
            "items": {item.id: item.get_info() for item in self.item_ids},
            "roles": [
                {"id": role.id, "name": role.name}
                for role in self.env["sign.oca.role"].search([])
            ],
            "fields": [
                {"id": field.id, "name": field.name}
                for field in self.env["sign.oca.field"].search([])
            ],
            "record_fields": self.env["sign.oca.field"]._get_model_field_choices(
                self.model
            ),
        }

    def delete_item(self, item_id):
        self.ensure_one()
        item = self.item_ids.browse(item_id)
        assert item.template_id == self
        item.unlink()

    def set_item_data(self, item_id, vals):
        self.ensure_one()
        item = self.env["sign.oca.template.item"].browse(item_id)
        assert item.template_id == self
        item.write(vals)

    def add_item(self, item_vals):
        self.ensure_one()
        item_vals["template_id"] = self.id
        return self.env["sign.oca.template.item"].create(item_vals).get_info()

    def _get_signatory_data(self, record=None):
        items = sorted(
            self.item_ids,
            key=lambda item: (
                item.page,
                item.position_y,
                item.position_x,
            ),
        )
        tabindex = 1
        signatory_data = {}
        item_id = 1
        for item in items:
            item_data = item._get_full_info(record)
            item_data["id"] = item_id
            item_data["tabindex"] = tabindex
            tabindex += 1
            signatory_data[item_id] = item_data
            item_id += 1
        return signatory_data

    def _prepare_sign_oca_request_vals_from_record(self, record):
        roles = self.mapped("item_ids.role_id").filtered(
            lambda x: x.partner_selection_policy != "empty"
        )
        return {
            "name": self.name,
            "template_id": self.id,
            "record_ref": f"{record._name},{record.id}",
            "signatory_data": self._get_signatory_data(record),
            "data": self.data,
            "signer_ids": [
                (
                    0,
                    0,
                    {
                        "partner_id": role._get_partner_from_record(record),
                        "role_id": role.id,
                    },
                )
                for role in roles
            ],
        }


class SignOcaTemplateItem(models.Model):
    _name = "sign.oca.template.item"
    _description = "Sign Oca Template Item"

    template_id = fields.Many2one(
        "sign.oca.template", required=True, ondelete="cascade"
    )
    field_id = fields.Many2one("sign.oca.field", ondelete="restrict")
    role_id = fields.Many2one(
        "sign.oca.role", default=lambda r: r._get_default_role(), ondelete="restrict"
    )
    required = fields.Boolean()
    # If no role, it will be editable by everyone...
    page = fields.Integer(required=True, default=1)
    position_x = fields.Float(required=True)
    position_y = fields.Float(required=True)
    width = fields.Float()
    height = fields.Float()
    placeholder = fields.Char()
    field_name = fields.Char(
        string="Database Field",
        help="Technical name of a field on the record linked to the "
        "document (optionally dotted to follow a many2one, e.g. "
        "'partner_id.vat'). When set, this item is automatically filled "
        "with that field's value instead of being filled in by a signer.",
    )

    @api.model
    def _get_default_role(self):
        return self.env.ref("sign_oca.sign_role_customer")

    @api.constrains("field_name")
    def _check_field_name(self):
        for item in self.filtered("field_name"):
            model = item.template_id.model_id
            if not model:
                raise ValidationError(
                    self.env._(
                        "You need to set a model on the template before "
                        "using database fields."
                    )
                )
            current_model = model.model
            chain = item.field_name.split(".")
            for index, fname in enumerate(chain):
                if current_model not in self.env:
                    raise ValidationError(
                        self.env._(
                            "Model %(model)s is not available", model=current_model
                        )
                    )
                current_model_obj = self.env[current_model]
                if fname not in current_model_obj._fields:
                    raise ValidationError(
                        self.env._(
                            "Field %(field)s does not exist in model "
                            "%(model)s",
                            field=fname,
                            model=current_model,
                        )
                    )
                field = current_model_obj._fields[fname]
                if index < len(chain) - 1:
                    if field.type != "many2one":
                        raise ValidationError(
                            self.env._(
                                "Field %(field)s in model %(model)s is not "
                                "a relation, so it cannot be followed by "
                                "more fields",
                                field=fname,
                                model=current_model,
                            )
                        )
                    current_model = field.comodel_name

    def get_info(self):
        self.ensure_one()
        return {
            "id": self.id,
            "field_id": self.field_id.id,
            "name": self.field_id.name,
            "role_id": self.role_id.id,
            "page": self.page,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "width": self.width,
            "height": self.height,
            "placeholder": self.placeholder,
            "required": self.required,
            "field_name": self.field_name,
        }

    def _get_full_info(self, record=None):
        """Method used in the wizards in the requests that are created."""
        self.ensure_one()
        vals = self.get_info()
        vals.update(
            {
                "field_type": self.field_id.field_type,
                "value": False,
                "default_value": self.field_id.default_value,
            }
        )
        if self.field_name:
            # Pre-fill the value from the record; "role_id"/"required" are
            # left as configured, so the assigned signer can still review
            # and correct it (an empty role keeps it uneditable, as before).
            vals["value"] = self.env["sign.oca.field"]._get_field_display_value(
                record, self.field_name
            )
        return vals
