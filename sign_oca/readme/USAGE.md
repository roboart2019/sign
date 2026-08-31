## Creation of templates

- Access Sign / Templates
- Create a new template
- Add a PDF File
- Access the configuration menu
- You can add a field by doing a right click inside a page
- Click on the field in order to delete or edit some configuration of it
- The template is autosaved

## Sign role

- Access Sign / Settings / Roles
- Create a new role (Equipment employee for example)
- You can set the Partner type you need (empty, default or expression).
- With the expression option you can set: {{object.field_name.id}}
- If you create a sign request from template signer will be auto-create
  according to roles

## Sign a document from template

- Access Sign / Templates
- Press the Sign button from a template
- Fill all the possible partners that will sign the document
- You can link the template to a model (maintenance.equipment for
  example)
- The signature action will be opened.
- There, you can fill all the data you need.
- Once you finish, press the sign button on the top
- When the last signer signs it, the final file will be generated as a
  PDF

## Sign a pending document

- Go to the pencil icon in the upper right corner (systray) of the sign
  request to access the pending signatures.
- Press the Sign button from signer request
- The signature action will be opened.
- There, you can fill all the data you need.
- Once you finish, press the sign button on the top
- When the last signer signs it, the final file will be generated as a
  PDF

## Sign from template

- Go to **Contacts**, from either the list view (select one or more
  records) or a single contact's own form view.
- Open the Action (gear) menu and pick **"Sign from Template"**.
- The wizard offers any sign template that is either not linked to any
  model, or linked to `res.partner` specifically.
- Select a template, click **"Generate"**.
- One request per selected record is created, each linked to that
  specific record (`record_ref`) — this is what makes "Pre-fill from
  database" fields actually pull real data, and it's what a Model
  linked template needs to be sent at all.
- No signer is set automatically by this wizard on its own; some extra
  modules (e.g. maintenance_sign_oca) will set the signers for each
  request for their own model. For a plain Contact, add signers on the
  generated request(s) yourself (Sign > Requests) before sending.
- Other models don't have this action wired in out of the box yet —
  only Contacts does, for now.

## Sign from portal
- customers who are using portal can sign their documents from portal 
  directly in addition to being able to sign them from emails.

## Pre-fill fields from the database

- When configuring a template or a request, click on a field to open its
  edition dialog.
- In the "Pre-fill from database" selector, pick a field of the record
  linked to the document, or one level through a relation (e.g. a
  partner's VAT): a relation's own fields (e.g. "Company > City",
  "Company > State"...) always appear right after it in the list, so
  fields that belong together stay together. This
  selector is only available once the template (or request) is linked
  to a model/record.
- Once picked, the field starts out already filled with that value (e.g.
  the customer VAT, the contract amount...), computed from the record
  used to generate the request.
- "Filled by" and "Required" still work as usual on top of that: if you
  set "Filled by" to a role (e.g. Customer), that signer sees the
  pre-filled value in their normal editable field and can correct it
  before signing if it is wrong. Leave "Filled by" empty instead if you
  want the pre-filled value to be fixed, so nobody can change it.
- The final value (whether left as pre-filled or corrected by the
  signer) is written into the PDF once the relevant signer signs the
  document (or, for a field with no "Filled by" role, as soon as the
  first signer signs).
