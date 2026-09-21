## Sign from template (Sales Order)

- Go to **Sales**, from either the list view (select one or more
  quotations/orders) or a single order's own form view.
- Open the Action (gear) menu and pick **"Sign from Template"**.
- Pick a sign template (one not linked to any model, or one linked to
  `sale.order` specifically), then click **Generate**.
- The resulting request is linked to that specific Sales Order, so
  "Pre-fill from database" fields on the template can pull data from
  the order itself (e.g. the customer, order lines, dates, ...) or one
  level through a relation (e.g. `partner_id.vat`).

## Automatically setting the signer from the order's customer

By default, no signer is set on the generated request; add one
manually before sending it.

To have it set automatically, edit the Role you use on the template
(Sign > Settings > Roles): set its **Partner type** to **Expression**
and its **Expression** to:

```
{{object.partner_id.id}}
```

This resolves to the Sales Order's own customer (`partner_id`) at
generation time, without any further configuration.
