# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.tools import format_amount, format_date, format_datetime

_logger = logging.getLogger(__name__)

# Field types that do not make sense to expose as a database field to embed
# in a document (too heavy, not meant to be printed, or not a leaf value).
_EXCLUDED_FIELD_TYPES = {"one2many", "binary", "html"}


class SignOcaField(models.Model):
    _name = "sign.oca.field"
    _description = "Signature Field Type"

    name = fields.Char(required=True)
    field_type = fields.Selection(
        [("text", "Text"), ("signature", "Signature"), ("check", "Check")],
        required=True,
        default="text",
    )
    default_value = fields.Char()

    @api.model
    def _get_model_field_choices(self, model_name):
        """Return the fields that can be picked as a "database field" to
        pre-fill an item, for the given model, as
        ``{"direct": [...], "groups": [...]}``.

        ``direct`` are the plain fields of ``model_name``. ``groups`` holds
        one entry per many2one field, each with the (one level deep) fields
        of the related model, e.g. all the fields reachable through
        ``partner_id`` (``partner_id.vat``, ``partner_id.city``...) grouped
        together under a "Customer" label — instead of being scattered
        across a single alphabetized list, where fields that belong
        together (e.g. a related company's city and state) could end up
        far apart from each other.
        """
        if not model_name or model_name not in self.env:
            return {"direct": [], "groups": []}
        model = self.env[model_name]
        direct = []
        groups = []
        for fname, field in model._fields.items():
            if fname == "id" or field.type in _EXCLUDED_FIELD_TYPES:
                continue
            direct.append({"name": fname, "string": field.string or fname})
            if field.type == "many2one" and field.comodel_name in self.env:
                related_model = self.env[field.comodel_name]
                sub_choices = []
                for sub_fname, sub_field in related_model._fields.items():
                    if sub_fname == "id" or sub_field.type in _EXCLUDED_FIELD_TYPES:
                        continue
                    sub_choices.append(
                        {
                            "name": f"{fname}.{sub_fname}",
                            "string": sub_field.string or sub_fname,
                        }
                    )
                if sub_choices:
                    groups.append(
                        {
                            "label": field.string or fname,
                            "fields": sorted(
                                sub_choices, key=lambda item: item["string"]
                            ),
                        }
                    )
        direct.sort(key=lambda item: item["string"])
        groups.sort(key=lambda group: group["label"])
        return {"direct": direct, "groups": groups}

    @api.model
    def _get_field_display_value(self, record, field_path):
        """Resolve a (possibly dotted) field path on ``record`` and return
        a human readable string suitable to be printed on a document.

        Returns an empty string whenever the record, the path, or any
        intermediate value is missing, instead of raising, so that a wrong
        or outdated configuration never blocks the signature flow.
        """
        if not record or not field_path:
            return ""
        try:
            current = record
            chain = field_path.split(".")
            for fname in chain[:-1]:
                if fname not in current._fields:
                    return ""
                current = current[fname]
                if not current:
                    return ""
            fname = chain[-1]
            if fname not in current._fields:
                return ""
            field = current._fields[fname]
            value = current[fname]
            return self._format_field_display_value(current, field, value)
        except Exception:
            _logger.exception(
                "Error getting the value of field '%s' for a sign.oca item",
                field_path,
            )
            return ""

    @api.model
    def _format_field_display_value(self, record, field, value):
        if not value:
            return ""
        if field.type == "many2one":
            return value.display_name
        if field.type in ("many2many", "one2many"):
            return ", ".join(value.mapped("display_name"))
        if field.type == "date":
            return format_date(self.env, value)
        if field.type == "datetime":
            return format_datetime(self.env, value)
        if field.type == "monetary":
            currency = (
                field.currency_field
                and record[field.currency_field]
                or self.env.company.currency_id
            )
            return format_amount(self.env, value, currency)
        if field.type == "selection":
            try:
                selection = field._description_selection(self.env)
            except Exception:
                selection = field.selection if isinstance(field.selection, list) else []
            return str(dict(selection).get(value, value))
        return str(value)
