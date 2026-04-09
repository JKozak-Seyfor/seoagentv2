{
  "name": "Setup_Agent",
  "flow": [
    {
      "id": 1,
      "module": "gateway:CustomWebHook",
      "version": 1,
      "parameters": {
        "hook": 3845800,
        "maxResults": 1
      },
      "mapper": {},
      "metadata": {
        "designer": { "x": 0, "y": 150 },
        "restore": {
          "parameters": {
            "hook": {
              "data": { "editable": "true" },
              "label": "seo_setup_request"
            }
          }
        },
        "parameters": [
          { "name": "hook", "type": "hook:gateway-webhook", "label": "Webhook", "required": true },
          { "name": "maxResults", "type": "number", "label": "Maximum number of results" }
        ],
        "interface": [
          {
            "name": "action",
            "type": "text",
            "label": "Action: 'upsert' nebo 'delete'"
          },
          {
            "name": "client_id",
            "type": "text",
            "label": "Client ID (required, klíč do seo_config datastoru)"
          },
          {
            "name": "notification_email",
            "type": "text",
            "label": "Notification email (required)"
          },
          {
            "name": "company_name",
            "type": "text",
            "label": "Company name"
          },
          {
            "name": "website_url",
            "type": "text",
            "label": "Website URL"
          },
          {
            "name": "default_language",
            "type": "text",
            "label": "Default language (cs / en / sk / de…)"
          },
          {
            "name": "default_tone",
            "type": "text",
            "label": "Default tone"
          },
          {
            "name": "default_audience",
            "type": "text",
            "label": "Default audience"
          },
          {
            "name": "default_intent",
            "type": "text",
            "label": "Default search intent"
          },
          {
            "name": "default_length_words",
            "type": "number",
            "label": "Default article length (words)"
          },
          {
            "name": "requires_manual_review",
            "type": "boolean",
            "label": "Requires manual review flag"
          },
          {
            "name": "brand_voice_rules",
            "type": "text",
            "label": "Brand voice rules (text)"
          },
          {
            "name": "company_context",
            "type": "text",
            "label": "Company context (text, pro social planner)"
          },
          {
            "name": "drive_folder_id",
            "type": "text",
            "label": "Google Drive folder ID"
          },
          {
            "name": "channels_json",
            "type": "text",
            "label": "Channels config (JSON string)"
          },
          {
            "name": "utm_defaults_json",
            "type": "text",
            "label": "UTM defaults (JSON string)"
          },
          {
            "name": "employee_advocacy",
            "type": "text",
            "label": "Employee advocacy rules (JSON string)"
          }
        ]
      }
    },
    {
      "id": 2,
      "module": "builtin:BasicRouter",
      "version": 1,
      "mapper": null,
      "metadata": {
        "designer": { "x": 300, "y": 150 }
      },
      "routes": [
        {
          "flow": [
            {
              "id": 20,
              "module": "datastore:DeleteRecord",
              "version": 1,
              "parameters": {
                "datastore": 148248
              },
              "filter": {
                "name": "Delete klienta",
                "conditions": [
                  [
                    {
                      "a": "{{1.action}}",
                      "b": "delete",
                      "o": "text:equal"
                    }
                  ]
                ]
              },
              "mapper": {
                "key": "{{1.client_id}}"
              },
              "metadata": {
                "designer": { "x": 600, "y": 0 },
                "restore": {
                  "parameters": {
                    "datastore": { "label": "seo_config" }
                  }
                },
                "parameters": [
                  { "name": "datastore", "type": "datastore", "label": "Data store", "required": true }
                ],
                "expect": [
                  { "name": "key", "type": "text", "label": "Key", "required": true }
                ]
              }
            },
            {
              "id": 21,
              "module": "microsoft-email:createAndSendAMessage",
              "version": 3,
              "parameters": {
                "account": ""
              },
              "mapper": {
                "to": [{ "name": "", "address": "{{1.notification_email}}" }],
                "subject": "[SEO Agent] Klient {{1.client_id}} byl smazán",
                "bodyType": "html",
                "content": "<!DOCTYPE html>\n<html lang=\"cs\">\n<head><meta charset=\"utf-8\"/></head>\n<body>\n  <p>Ahoj,</p>\n  <p>konfigurace klienta <strong>{{1.client_id}}</strong> byla úspěšně odstraněna ze SEO agenta.</p>\n  <p>Pokud byl smazán omylem, proveď znovu Setup pro tohoto klienta.</p>\n  <p>S pozdravem,<br/><em>SEO Agent Setup</em></p>\n</body>\n</html>"
              },
              "metadata": {
                "designer": { "x": 900, "y": 0 },
                "restore": {
                  "parameters": {
                    "account": { "label": "Vyber účet" }
                  },
                  "expect": {
                    "bodyType": { "label": "HTML" }
                  }
                },
                "parameters": [
                  { "name": "account", "type": "account:microsoft-email", "label": "Connection", "required": true }
                ],
                "expect": [
                  { "name": "to", "spec": { "name": "value", "spec": [{ "name": "name", "type": "text", "label": "Name" }, { "name": "address", "type": "email", "label": "Email address", "required": true }], "type": "collection", "label": "Recipient" }, "type": "array", "label": "To", "required": true },
                  { "name": "subject", "type": "text", "label": "Subject", "required": true },
                  { "name": "content", "type": "text", "label": "Content", "required": true },
                  { "name": "bodyType", "type": "select", "label": "Content type", "validate": { "enum": ["text", "html"] } }
                ]
              }
            }
          ]
        },
        {
          "flow": [
            {
              "id": 10,
              "module": "datastore:AddRecord",
              "version": 1,
              "parameters": {
                "datastore": 148248
              },
              "filter": {
                "name": "Upsert klienta",
                "conditions": [
                  [
                    {
                      "a": "{{1.action}}",
                      "b": "upsert",
                      "o": "text:equal"
                    }
                  ]
                ]
              },
              "mapper": {
                "key": "{{1.client_id}}",
                "overwrite": true,
                "data": {
                  "company_name": "{{1.company_name}}",
                  "website_url": "{{1.website_url}}",
                  "default_language": "{{1.default_language}}",
                  "default_tone": "{{1.default_tone}}",
                  "default_audience": "{{1.default_audience}}",
                  "default_intent": "{{1.default_intent}}",
                  "default_length_words": "{{1.default_length_words}}",
                  "requires_manual_review": "{{1.requires_manual_review}}",
                  "brand_voice_rules": "{{1.brand_voice_rules}}",
                  "company_context": "{{1.company_context}}",
                  "drive_folder_id": "{{1.drive_folder_id}}",
                  "channels_json": "{{1.channels_json}}",
                  "utm_defaults_json": "{{1.utm_defaults_json}}",
                  "employee_advocacy": "{{1.employee_advocacy}}",
                  "notification_email": "{{1.notification_email}}",
                  "setup_at": "{{now}}"
                }
              },
              "metadata": {
                "designer": { "x": 600, "y": 300 },
                "restore": {
                  "expect": {
                    "overwrite": { "mode": "chose" }
                  },
                  "parameters": {
                    "datastore": { "label": "seo_config" }
                  }
                },
                "parameters": [
                  { "name": "datastore", "type": "datastore", "label": "Data store", "required": true }
                ],
                "expect": [
                  { "name": "key", "type": "text", "label": "Key" },
                  { "name": "overwrite", "type": "boolean", "label": "Overwrite an existing record", "required": true },
                  {
                    "name": "data",
                    "spec": [
                      { "name": "company_name", "type": "text", "label": null },
                      { "name": "website_url", "type": "text", "label": null },
                      { "name": "default_language", "type": "text", "label": null },
                      { "name": "default_tone", "type": "text", "label": null },
                      { "name": "default_audience", "type": "text", "label": null },
                      { "name": "default_intent", "type": "text", "label": null },
                      { "name": "default_length_words", "type": "number", "label": null },
                      { "name": "requires_manual_review", "type": "boolean", "label": null },
                      { "name": "brand_voice_rules", "type": "text", "label": null },
                      { "name": "company_context", "type": "text", "label": null },
                      { "name": "drive_folder_id", "type": "text", "label": null },
                      { "name": "channels_json", "type": "text", "label": null },
                      { "name": "utm_defaults_json", "type": "text", "label": null },
                      { "name": "employee_advocacy", "type": "text", "label": null },
                      { "name": "notification_email", "type": "text", "label": null },
                      { "name": "setup_at", "type": "date", "label": null }
                    ],
                    "type": "collection",
                    "label": "Record"
                  }
                ]
              }
            },
            {
              "id": 11,
              "module": "microsoft-email:createAndSendAMessage",
              "version": 3,
              "parameters": {
                "account": ""
              },
              "mapper": {
                "to": [{ "name": "", "address": "{{1.notification_email}}" }],
                "subject": "[SEO Agent] Klient {{1.client_id}} – konfigurace uložena",
                "bodyType": "html",
                "content": "<!DOCTYPE html>\n<html lang=\"cs\">\n<head><meta charset=\"utf-8\"/></head>\n<body style=\"font-family:sans-serif;color:#111;\">\n  <p>Ahoj,</p>\n  <p>konfigurace SEO agenta pro klienta <strong>{{1.client_id}}</strong> byla úspěšně uložena.</p>\n  <table style=\"border-collapse:collapse;font-size:14px;margin:16px 0;\">\n    <tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Firma</td><td><strong>{{1.company_name}}</strong></td></tr>\n    <tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Jazyk</td><td>{{1.default_language}}</td></tr>\n    <tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Tón</td><td>{{1.default_tone}}</td></tr>\n    <tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Délka článku</td><td>{{1.default_length_words}} slov</td></tr>\n    <tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Manuální schválení</td><td>{{1.requires_manual_review}}</td></tr>\n    <tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Nastaveno</td><td>{{now}}</td></tr>\n  </table>\n  <p>Klient je nyní aktivní a může začít používat SEO Article Request.</p>\n  <p>S pozdravem,<br/><em>SEO Agent Setup</em></p>\n</body>\n</html>"
              },
              "metadata": {
                "designer": { "x": 900, "y": 300 },
                "restore": {
                  "parameters": {
                    "account": { "label": "Vyber účet" }
                  },
                  "expect": {
                    "bodyType": { "label": "HTML" }
                  }
                },
                "parameters": [
                  { "name": "account", "type": "account:microsoft-email", "label": "Connection", "required": true }
                ],
                "expect": [
                  { "name": "to", "spec": { "name": "value", "spec": [{ "name": "name", "type": "text", "label": "Name" }, { "name": "address", "type": "email", "label": "Email address", "required": true }], "type": "collection", "label": "Recipient" }, "type": "array", "label": "To", "required": true },
                  { "name": "subject", "type": "text", "label": "Subject", "required": true },
                  { "name": "content", "type": "text", "label": "Content", "required": true },
                  { "name": "bodyType", "type": "select", "label": "Content type", "validate": { "enum": ["text", "html"] } }
                ]
              }
            }
          ]
        }
      ]
    }
  ],
  "metadata": {
    "instant": true,
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": true,
      "autoCommitTriggerLast": true,
      "sequential": false,
      "slots": null,
      "confidential": false,
      "dataloss": false,
      "dlq": false,
      "freshVariables": false
    },
    "designer": {
      "orphans": []
    },
    "zone": "eu2.make.com",
    "notes": [
      {
        "moduleIds": [1],
        "content": "<p><strong>Setup_Agent – vstupní webhook</strong><br>Povinné vždy: action (\"upsert\" / \"delete\"), client_id, notification_email<br>Povinné pro upsert: všechna ostatní pole<br>Pro delete: stačí action + client_id + notification_email</p>",
        "isFilterNote": false,
        "metadata": { "color": "#00BCD4" }
      },
      {
        "moduleIds": [2],
        "content": "<p><strong>Router</strong><br>Route 1 – filter: action == \"delete\" → smaže záznam z seo_config + email<br>Route 2 – filter: action == \"upsert\" → uloží/přepíše záznam v seo_config + email<br><br>⚠️ Oba filtry jsou explicitní – neznámá action projde bez výsledku.</p>",
        "isFilterNote": false,
        "metadata": { "color": "#9138FE" }
      },
      {
        "moduleIds": [20],
        "content": "<p><strong>Delete klienta</strong><br>Smaže celý záznam z seo_config datastoru (key = client_id).<br>Neovlivní již spuštěné joby – ty mají config embedded v seo_jobs.</p>",
        "isFilterNote": false,
        "metadata": { "color": "#F44336" }
      },
      {
        "moduleIds": [10],
        "content": "<p><strong>Upsert klienta</strong><br>overwrite: true = vytvoří nový záznam nebo přepíše existující.<br>Bezpečné opakovat při aktualizaci konfigurace.</p>",
        "isFilterNote": false,
        "metadata": { "color": "#4CAF50" }
      },
      {
        "moduleIds": [11, 21],
        "content": "<p>E-mail přes Microsoft / Outlook.<br>Po importu: přiřadit účet v parametrech obou e-mailových modulů.</p>",
        "isFilterNote": false,
        "metadata": { "color": "#9138FE" }
      }
    ]
  }
}
