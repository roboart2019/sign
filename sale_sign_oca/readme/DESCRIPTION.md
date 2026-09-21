This module adds a "Sign from Template" action to Sales Orders,
the same way sign_oca already provides it for Contacts, so a signature
request can be generated linked to a specific Sales Order
(its ``record_ref``) instead of only being reachable from a Contact.

This is a small bridge module (it only wires up an existing sign_oca
action to another model) rather than a change to sign_oca itself, so
that installs of sign_oca without the Sales app are unaffected.
