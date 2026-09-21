=============
Sale Sign Oca
=============

..
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated. Regenerate it by hand   !!
   !! (or with oca-gen-addon-readme) after editing the !!
   !! readme/*.md fragments.                           !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Send a Sales Order for signature using Sign Oca

**Table of contents**

.. contents::
   :local:

Description
===========

This module adds a "Sign from Template" action to Sales Orders,
the same way sign_oca already provides it for Contacts, so a signature
request can be generated linked to a specific Sales Order
(its ``record_ref``) instead of only being reachable from a Contact.

This is a small bridge module (it only wires up an existing sign_oca
action to another model) rather than a change to sign_oca itself, so
that installs of sign_oca without the Sales app are unaffected.

Usage
=====

Sign from template (Sales Order)
---------------------------------

- Go to **Sales**, from either the list view (select one or more
  quotations/orders) or a single order's own form view.
- Open the Action (gear) menu and pick **"Sign from Template"**.
- Pick a sign template (one not linked to any model, or one linked to
  ``sale.order`` specifically), then click **Generate**.
- The resulting request is linked to that specific Sales Order, so
  "Pre-fill from database" fields on the template can pull data from
  the order itself (e.g. the customer, order lines, dates, ...) or one
  level through a relation (e.g. ``partner_id.vat``).

Automatically setting the signer from the order's customer
------------------------------------------------------------

By default, no signer is set on the generated request; add one
manually before sending it.

To have it set automatically, edit the Role you use on the template
(Sign > Settings > Roles): set its **Partner type** to **Expression**
and its **Expression** to::

    {{object.partner_id.id}}

This resolves to the Sales Order's own customer (``partner_id``) at
generation time, without any further configuration.

Licenses
========

This repository is licensed under `AGPL-3.0 <LICENSE>`_.
